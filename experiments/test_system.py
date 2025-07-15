from core.main import main
import os
import subprocess
import sys

questions = [
    "What is the most common food vehicle associated with salmonella outbreaks?",
    "Which county in AZ had the highest food insecurity rate in 2022?",
    "What factors might contribute to the variation in outbreak sizes across different food vehicles?",
    "How does social vulnerability at the county level correlate with food insecurity and poverty and are there any notable differences in salmonella outbreak incidence between counties with high vs low social vulnerability and food insecurity?",
    "Can we identify specific socioeconomic factors that are strong predictors of increased Salmonella outbreaks in specific regions?",
    "What is the current salmonella risk level in Boone County, and what actions should I take?"
]

def test():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root
    for question in questions:
        print("Input:", question)
        process = subprocess.Popen(
            [sys.executable, "core/main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        # Send the question as input
        stdout, stderr = process.communicate(input=question + "\n")
        print(f"Question: {question}")
        print("Output:")
        print(stdout)
        if stderr:
            print("Errors:")
            print(stderr)

if __name__ == "__main__":
    test()
