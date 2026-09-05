import json
import statistics


# -----------------------------
# Load benchmark definitions
# -----------------------------

with open(
    "data/benchmark.json",
    "r",
    encoding="utf-8"
) as file:
    benchmark = json.load(file)


# -----------------------------
# Load saved experiment results
# -----------------------------

with open(
    "results/results.json",
    "r",
    encoding="utf-8"
) as file:
    results = json.load(file)


# -----------------------------
# Build question lookup table
# -----------------------------

benchmark_by_id = {
    item["id"]: item
    for item in benchmark
}


# -----------------------------
# Overall metrics
# -----------------------------

total_runs = len(results)

if total_runs == 0:
    print("No benchmark results found.")
    raise SystemExit


correct_runs = sum(
    result["correct"]
    for result in results
)


accuracy = correct_runs / total_runs


latencies = [
    result["latency_seconds"]
    for result in results
]


average_latency = statistics.mean(latencies)
median_latency = statistics.median(latencies)


# -----------------------------
# Category-level metrics
# -----------------------------

category_stats = {}


for result in results:

    question_id = result["question_id"]

    benchmark_item = benchmark_by_id[question_id]

    category = benchmark_item["category"]


    if category not in category_stats:
        category_stats[category] = {
            "total": 0,
            "correct": 0,
            "latencies": []
        }


    category_stats[category]["total"] += 1

    category_stats[category]["correct"] += int(
        result["correct"]
    )

    category_stats[category]["latencies"].append(
        result["latency_seconds"]
    )


# -----------------------------
# Evaluation-method counts
# -----------------------------

evaluation_methods = {}


for result in results:

    method = result.get(
        "evaluation_method",
        "unknown"
    )

    evaluation_methods[method] = (
        evaluation_methods.get(method, 0) + 1
    )


# -----------------------------
# Print overall summary
# -----------------------------

print("\n===================================")
print("BENCHMARK ANALYSIS")
print("===================================")

print("Total evaluated runs:", total_runs)

print(
    "Correct runs:",
    correct_runs
)

print(
    "Run-level accuracy:",
    round(accuracy * 100, 2),
    "%"
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
# Print category analysis
# -----------------------------

print("\n--- Category Performance ---")


for category, stats in category_stats.items():

    category_accuracy = (
        stats["correct"] / stats["total"]
    )

    category_average_latency = statistics.mean(
        stats["latencies"]
    )


    print(f"\nCategory: {category}")

    print(
        "Accuracy:",
        round(category_accuracy * 100, 2),
        "%"
    )

    print(
        "Correct:",
        stats["correct"],
        "/",
        stats["total"]
    )

    print(
        "Average latency:",
        round(category_average_latency, 3),
        "seconds"
    )


# -----------------------------
# Print evaluator usage
# -----------------------------

print("\n--- Evaluation Methods ---")

for method, count in evaluation_methods.items():
    print(method, ":", count)


# -----------------------------
# Build summary data
# -----------------------------

summary = {
    "total_runs": total_runs,
    "correct_runs": correct_runs,
    "run_level_accuracy": round(accuracy, 4),
    "average_latency_seconds": round(average_latency, 3),
    "median_latency_seconds": round(median_latency, 3),
    "category_performance": {},
    "evaluation_methods": evaluation_methods
}


for category, stats in category_stats.items():

    category_accuracy = (
        stats["correct"] / stats["total"]
    )

    summary["category_performance"][category] = {
        "total": stats["total"],
        "correct": stats["correct"],
        "accuracy": round(category_accuracy, 4),
        "average_latency_seconds": round(
            statistics.mean(stats["latencies"]),
            3
        )
    }


# -----------------------------
# Save summary
# -----------------------------

with open(
    "results/summary.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        summary,
        file,
        indent=2
    )


print("\nAnalysis saved to results/summary.json")

print("\n===================================")