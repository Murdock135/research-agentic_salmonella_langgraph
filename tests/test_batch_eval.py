import asyncio
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

from eval.batch_eval import persist_manifest, run_bounded, update_batch_summary
from sparq.architectures.v1.system import Agentic_system
from sparq.schemas.output_schemas import BatchEvalOutput, BatchRunEntry, RunStatus, SystemOutput


class TestBatchSummary(unittest.TestCase):
    def make_batch(self, statuses: list[str]) -> BatchEvalOutput:
        runs = [
            BatchRunEntry(
                question_id=index + 1,
                question_index=index,
                iteration=1,
                run_id=f"run-{index}",
                result_path=Path(f"runs/run-{index}/result.json"),
                status=cast(RunStatus, status),
            )
            for index, status in enumerate(statuses)
        ]
        return BatchEvalOutput(
            batch_id="batch-1",
            time_started=datetime.now(timezone.utc),
            dataset_path=Path("data/Q_dataset.json"),
            dataset_hash="sha256:test",
            question_filter={},
            requested_question_count=len(runs),
            selected_question_ids=[entry.question_id for entry in runs],
            iterations=1,
            max_concurrent_runs=3,
            code_version={},
            configuration={},
            planned_runs=len(runs),
            runs=runs,
        )

    def test_summary_is_completed_when_all_runs_complete(self):
        batch = self.make_batch(["completed", "completed"])

        update_batch_summary(batch)

        self.assertEqual(batch.status, "completed")
        self.assertEqual(batch.completed_runs, 2)

    def test_summary_reports_mixed_terminal_results(self):
        batch = self.make_batch(["completed", "failed"])

        update_batch_summary(batch)

        self.assertEqual(batch.status, "completed_with_errors")
        self.assertEqual(batch.completed_runs, 1)
        self.assertEqual(batch.failed_runs, 1)

    def test_inactive_batch_with_unfinished_runs_is_interrupted(self):
        batch = self.make_batch(["completed", "pending"])

        update_batch_summary(batch, active=False)

        self.assertEqual(batch.status, "interrupted")


class TestRunLifecycle(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.manifest_path = Path(self.temporary_directory.name) / "batch.json"
        self.entry = BatchRunEntry(
            question_id=1,
            question_index=0,
            iteration=1,
            run_id="run-1",
            result_path=Path("runs/iteration_001/question_001/run-1/result.json"),
        )
        self.batch = BatchEvalOutput(
            batch_id="batch-1",
            time_started=datetime.now(timezone.utc),
            dataset_path=Path("data/Q_dataset.json"),
            dataset_hash="sha256:test",
            question_filter={"weather_related": False},
            requested_question_count=1,
            selected_question_ids=[1],
            iterations=1,
            max_concurrent_runs=1,
            code_version={},
            configuration={},
            planned_runs=1,
            runs=[self.entry],
        )
        self.question = {"id": 1, "text": "Test question?", "grade": 4}

    def tearDown(self):
        self.temporary_directory.cleanup()

    async def test_successful_run_is_persisted_as_completed(self):
        output = SystemOutput(
            run_id="run-1",
            query=self.question["text"],
            difficulty=4,
            models={},
            response="Test answer",
            time_started=datetime.now(timezone.utc),
            time_ended=datetime.now(timezone.utc),
            duration=0.1,
            ablation_config={},
            token_out=None,
            cost=None,
            evaluation_context=None,
            sparq_judge_score=None,
            sparq_judge_review=None,
        )
        agent = SimpleNamespace(run=AsyncMock(return_value=output))

        result = await run_bounded(
            asyncio.Semaphore(1),
            cast(Agentic_system, agent),
            self.question,
            self.entry,
            self.batch,
            self.manifest_path,
            asyncio.Lock(),
        )

        self.assertEqual(result, output)
        self.assertEqual(self.entry.status, "completed")
        evaluation_context = agent.run.await_args.kwargs["evaluation_context"]
        self.assertEqual(evaluation_context.batch_id, "batch-1")
        self.assertEqual(evaluation_context.question_id, 1)
        self.assertEqual(evaluation_context.iteration, 1)
        manifest = json.loads(self.manifest_path.read_text())
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual(manifest["completed_runs"], 1)

    async def test_failed_run_records_the_exception(self):
        agent = SimpleNamespace(run=AsyncMock(side_effect=RuntimeError("model unavailable")))

        result = await run_bounded(
            asyncio.Semaphore(1),
            cast(Agentic_system, agent),
            self.question,
            self.entry,
            self.batch,
            self.manifest_path,
            asyncio.Lock(),
        )

        self.assertIsNone(result)
        self.assertEqual(self.entry.status, "failed")
        self.assertEqual(self.entry.error_type, "RuntimeError")
        self.assertEqual(self.entry.error_message, "model unavailable")
        manifest = json.loads(self.manifest_path.read_text())
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["failed_runs"], 1)

    async def test_pending_manifest_is_written_before_execution(self):
        await persist_manifest(self.batch, self.manifest_path, asyncio.Lock())

        manifest = json.loads(self.manifest_path.read_text())
        self.assertEqual(manifest["status"], "running")
        self.assertEqual(manifest["runs"][0]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
