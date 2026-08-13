"""Run repeatable batch evaluations over eligible questions in Q_dataset.json."""

import argparse
import asyncio
import hashlib
import json
import subprocess
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

from sparq.architectures.v1.system import Agentic_system
from sparq.schemas.output_schemas import (
    BatchEvalOutput,
    BatchRunEntry,
    EvaluationContext,
    SystemOutput,
)
from sparq.settings import ENVSettings
from sparq.utils.get_package_dir import get_project_root


MAX_CONCURRENT_RUNS = 3
_project_root = get_project_root()
if _project_root is None:
    raise RuntimeError("Could not locate project root")
PROJECT_ROOT: Path = _project_root
FILE_PATH = PROJECT_ROOT / "data" / "Q_dataset.json"
RESULTS_ROOT = Path(__file__).parent / "results" / "batch_eval"


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


parser = argparse.ArgumentParser(
    description="Run batch evaluation on SPARQ over test questions in data/Q_dataset",
)
parser.add_argument("-n", "--n_questions", type=positive_int, default=1)
parser.add_argument("-k", "--iterations", type=positive_int, default=1)


def load_data(file_path: str | Path) -> list[dict]:
    with open(file_path) as file:
        questions = json.load(file).get("questions", [])

    if not questions:
        raise ValueError(f"No questions found in {file_path}")

    return questions


def local_now() -> datetime:
    return datetime.now().astimezone()


def make_batch_id(started_at: datetime) -> str:
    timestamp = started_at.strftime("%Y-%m-%dT%H-%M-%S-%Z")
    return f"{timestamp}_{uuid.uuid4().hex[:8]}"


def hash_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def get_code_version(project_root: Path) -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}

    return {"commit": commit, "dirty": dirty}


def update_batch_summary(batch: BatchEvalOutput, active: bool = True) -> None:
    counts = Counter(entry.status for entry in batch.runs)
    batch.completed_runs = counts["completed"]
    batch.failed_runs = counts["failed"]
    batch.cancelled_runs = counts["cancelled"]
    batch.interrupted_runs = counts["interrupted"]

    if not active and (counts["pending"] or counts["running"]):
        batch.status = "interrupted"
    elif counts["pending"] or counts["running"]:
        batch.status = "running"
    elif batch.completed_runs == batch.planned_runs:
        batch.status = "completed"
    elif batch.completed_runs:
        batch.status = "completed_with_errors"
    else:
        batch.status = "failed"


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.tmp")

    if isinstance(value, BatchEvalOutput):
        payload = value.model_dump(mode="json")
    else:
        payload = value

    with open(temporary_path, "w") as file:
        json.dump(payload, file, indent=2)
        file.write("\n")
    temporary_path.replace(path)


async def persist_manifest(
    batch: BatchEvalOutput,
    manifest_path: Path,
    lock: asyncio.Lock,
    active: bool = True,
) -> None:
    async with lock:
        update_batch_summary(batch, active=active)
        write_json_atomic(manifest_path, batch)


async def run_bounded(
    semaphore: asyncio.Semaphore,
    agentic_system: Agentic_system,
    question: dict,
    run_entry: BatchRunEntry,
    batch: BatchEvalOutput,
    manifest_path: Path,
    manifest_lock: asyncio.Lock,
) -> SystemOutput | None:
    try:
        async with semaphore:
            run_entry.status = "running"
            run_entry.time_started = local_now()
            await persist_manifest(batch, manifest_path, manifest_lock)

            try:
                result = await agentic_system.run(
                    question["text"],
                    run_id=run_entry.run_id,
                    difficulty=question["grade"],
                    evaluation_context=EvaluationContext(
                        batch_id=batch.batch_id,
                        question_id=question["id"],
                        iteration=run_entry.iteration,
                    ),
                )
            except Exception as error:
                run_entry.status = "failed"
                run_entry.error_type = type(error).__name__
                run_entry.error_message = str(error)
                run_entry.time_ended = local_now()
                await persist_manifest(batch, manifest_path, manifest_lock)
                return None

            run_entry.status = "completed"
            run_entry.time_ended = local_now()
            await persist_manifest(batch, manifest_path, manifest_lock)
            return result
    except asyncio.CancelledError:
        run_entry.status = "cancelled"
        run_entry.time_ended = local_now()
        await persist_manifest(batch, manifest_path, manifest_lock)
        raise


def create_batch(
    questions: list[dict],
    requested_question_count: int,
    iterations: int,
    configuration: dict,
) -> tuple[BatchEvalOutput, Path]:
    started_at = local_now()
    batch_id = make_batch_id(started_at)
    batch_dir = RESULTS_ROOT / batch_id
    runs: list[BatchRunEntry] = []

    for iteration in range(1, iterations + 1):
        for question_index, question in enumerate(questions):
            run_id = str(uuid.uuid4())
            relative_run_dir = (
                Path("runs")
                / f"iteration_{iteration:03d}"
                / f"question_{question['id']:03d}"
                / run_id
            )
            runs.append(
                BatchRunEntry(
                    question_id=question["id"],
                    question_index=question_index,
                    iteration=iteration,
                    run_id=run_id,
                    result_path=relative_run_dir / "result.json",
                )
            )

    batch = BatchEvalOutput(
        batch_id=batch_id,
        time_started=started_at,
        dataset_path=FILE_PATH.relative_to(PROJECT_ROOT),
        dataset_hash=hash_file(FILE_PATH),
        question_filter={"weather_related": False, "excluded_grade": -1},
        requested_question_count=requested_question_count,
        selected_question_ids=[question["id"] for question in questions],
        iterations=iterations,
        max_concurrent_runs=MAX_CONCURRENT_RUNS,
        code_version=get_code_version(PROJECT_ROOT),
        configuration=configuration,
        planned_runs=len(runs),
        runs=runs,
    )
    return batch, batch_dir


async def main() -> None:
    args = parser.parse_args()
    all_questions = load_data(FILE_PATH)
    eligible_questions = [
        question
        for question in all_questions
        if not question["weather_related"] and question["grade"] != -1
    ]
    questions = eligible_questions[:args.n_questions]
    if not questions:
        raise ValueError("No questions matched the batch filters")

    ENVSettings()
    settings_source = Agentic_system()
    configuration = {"models": settings_source.settings.llm_config.model_dump(mode="json")}
    batch, batch_dir = create_batch(
        questions=questions,
        requested_question_count=args.n_questions,
        iterations=args.iterations,
        configuration=configuration,
    )
    manifest_path = batch_dir / "batch.json"
    manifest_lock = asyncio.Lock()

    batch_dir.mkdir(parents=True, exist_ok=False)
    write_json_atomic(batch_dir / "questions.json", {"questions": questions})
    await persist_manifest(batch, manifest_path, manifest_lock)
    print(f"Batch {batch.batch_id}: {batch.planned_runs} runs")
    print(f"Manifest: {manifest_path}")

    try:
        for iteration in range(1, args.iterations + 1):
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_RUNS)
            tasks = []

            for question in questions:
                run_entry = next(
                    entry
                    for entry in batch.runs
                    if entry.iteration == iteration and entry.question_id == question["id"]
                )
                run_dir = batch_dir / run_entry.result_path.parent
                run_dir.mkdir(parents=True, exist_ok=False)

                agentic_system = Agentic_system()
                agentic_system.settings.paths.output_dir = run_dir.parent
                agentic_system.settings.paths.run_dir = run_dir
                tasks.append(
                    run_bounded(
                        semaphore,
                        agentic_system,
                        question,
                        run_entry,
                        batch,
                        manifest_path,
                        manifest_lock,
                    )
                )

            await asyncio.gather(*tasks)
    except BaseException:
        for run_entry in batch.runs:
            if run_entry.status == "running":
                run_entry.status = "interrupted"
                run_entry.time_ended = local_now()
        batch.time_ended = local_now()
        batch.duration = (batch.time_ended - batch.time_started).total_seconds()
        await persist_manifest(batch, manifest_path, manifest_lock, active=False)
        raise

    batch.time_ended = local_now()
    batch.duration = (batch.time_ended - batch.time_started).total_seconds()
    await persist_manifest(batch, manifest_path, manifest_lock)
    print(
        f"Batch {batch.status}: {batch.completed_runs} completed, "
        f"{batch.failed_runs} failed, {batch.cancelled_runs} cancelled"
    )


if __name__ == "__main__":
    asyncio.run(main())
