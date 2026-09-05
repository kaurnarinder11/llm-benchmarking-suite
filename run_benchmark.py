import json
import time
import statistics
import os

from google import genai

from evaluator import evaluate_response
from llm_judge import judge_response
from api_utils import create_interaction_with_retry


MODEL = "gemini-3.6-flash"
RUNS = 1


def build_prompt(item):
    context = item.get("context")

    if context:
        return (
            f"Context:\n{context}\n\n"
            f"Question:\n{item['question']}"
        )

    return item["question"]


# -----------------------------
# Load benchmark dataset
# -----------------------------

with open(
    "data/benchmark.json",
    "r",
    encoding="utf-8"
) as file:
    benchmark = json.load(file)


# Gemini client
client = genai.Client()


# Stores results from the entire benchmark
all_results = []


# -----------------------------
# Run benchmark
# -----------------------------

for item in benchmark:

    print("\n===================================")
    print("Question ID:", item["id"])
    print("Category:", item["category"])
    print("Question:", item["question"])
    print("===================================")

    prompt = build_prompt(item)

    # These belong only to the current question
    latencies = []
    correctness_results = []


    # Repeat the same question RUNS times
    for run_number in range(1, RUNS + 1):

        # -----------------------------
        # Call model under test
        # -----------------------------

        start_time = time.perf_counter()

        interaction = create_interaction_with_retry(
            client,
            model=MODEL,
            input=prompt
        )

        end_time = time.perf_counter()

        latency = end_time - start_time

        model_response = interaction.output_text


        # -----------------------------
        # Evaluate response
        # -----------------------------

        evaluation_method = item["evaluation"]["method"]

        judge_result = None

        if evaluation_method == "llm_judge":

            judge_result = judge_response(
                client,
                item,
                model_response
            )

            is_correct = (
                judge_result["verdict"] == "PASS"
            )

        else:

            is_correct = evaluate_response(
                item,
                model_response
            )


        # -----------------------------
        # Store raw measurements
        # -----------------------------

        latencies.append(latency)
        correctness_results.append(is_correct)


        result_record = {
            "question_id": item["id"],
            "category": item["category"],
            "model": MODEL,
            "run": run_number,
            "response": model_response,
            "correct": is_correct,
            "latency_seconds": round(latency, 3),
            "evaluation_method": evaluation_method
        }


        if judge_result is not None:
            result_record["judge_result"] = judge_result


        all_results.append(result_record)


        # -----------------------------
        # Print individual run
        # -----------------------------

        print(f"\n--- Run {run_number} ---")
        print("Response:", model_response)
        print("Correct:", is_correct)
        print(
            "Latency:",
            round(latency, 3),
            "seconds"
        )


        if judge_result is not None:
            print(
                "Judge verdict:",
                judge_result["verdict"]
            )

            print(
                "Judge reason:",
                judge_result["reason"]
            )

            print(
                "Judge criteria:",
                judge_result["criteria"]
            )


    # -----------------------------
    # Question-level statistics
    # -----------------------------

    average_latency = statistics.mean(latencies)

    median_latency = statistics.median(latencies)


    print("\n--- Question Summary ---")

    print(
        "Correct runs:",
        sum(correctness_results),
        "/",
        RUNS
    )

    print(
        "Average latency:",
        round(average_latency, 3),
        "seconds"
    )

    print(
        "Median latency:",
        round(median_latency, 3),
        "seconds"
    )


# -----------------------------
# Save results
# -----------------------------

os.makedirs(
    "results",
    exist_ok=True
)


with open(
    "results/results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        all_results,
        file,
        indent=2
    )


# -----------------------------
# Final benchmark summary
# -----------------------------

print("\n===================================")
print("BENCHMARK COMPLETE")
print("Total questions:", len(benchmark))
print("Total model runs:", len(all_results))
print("Results saved to results/results.json")
print("===================================")