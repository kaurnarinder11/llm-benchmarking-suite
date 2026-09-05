# LLM Benchmarking & Evaluation Suite

A Python-based prototype for evaluating Large Language Models across multiple categories using structured benchmark questions, ground-truth/reference answers, automated model execution, hybrid evaluation, latency measurement, and result analysis.

This is an independently developed, general-purpose public demonstration of LLM benchmarking and evaluation. It does **not** use Indian Army internal data, confidential information, or internal systems.

---

## Project Goal

LLM responses cannot always be evaluated using simple exact string matching.

For example:

- Factual questions may have short deterministic answers.

- Reasoning answers may use different wording while remaining correct.

- Mathematical questions may require precise answers.

- Contextual questions require the model to follow information supplied in the prompt.

- Ambiguity questions require the model to recognize missing information.

- Hallucination traps test whether the model invents information when the premise is false or unsupported.

This project explores how a benchmark pipeline can evaluate these different behaviors using a combination of deterministic rules, required-concept checks, and rubric-based LLM judging.

---

## Current Benchmark

The current prototype contains **12 curated benchmark questions** across six categories:

| Category | Questions | Purpose |

|---|---:|---|

| Factual | 2 | Test verifiable factual knowledge |

| Reasoning | 2 | Test logical inference |

| Mathematical | 2 | Test numerical and mathematical correctness |

| Contextual | 2 | Test use of supplied context |

| Ambiguity | 2 | Test recognition of missing information |

| Hallucination | 2 | Test resistance to false premises and fabricated answers |

Each benchmark item can contain structured metadata such as:

- Question ID

- Category

- Difficulty

- Question

- Optional context

- Ground-truth/reference answer

- Source or verification status

- Expected behavior where applicable

- Evaluation method

---

## Architecture

```text

benchmark.json

      |

      v

Prompt Builder

      |

      v

LLM API

      |

      v

Model Response

      |

      +------------------------------+

      |                              |

      v                              v

Deterministic Evaluator       Rubric-Based LLM Judge

      |                              |

      +---------------+--------------+

                      |

                      v

               Evaluation Result

                      |

                      v

           Latency + Result Storage

                      |

                      v

                results.json

                      |

                      v

              Analysis Pipeline

                      |

                      v

                summary.json

```

---

## Implemented Features

- Structured JSON benchmark dataset

- Six benchmark categories

- Context-aware prompt construction

- Gemini API integration

- Deterministic evaluation for suitable questions

- Required-concept evaluation

- Rubric-based LLM-as-a-judge evaluation for reasoning tasks

- End-to-end client-side latency measurement

- Repeated-run support

- Basic API rate-limit retry handling

- Structured JSON result storage

- Overall and category-level result analysis

- Mean and median latency calculation

- Evaluation-method tracking

---

## Hybrid Evaluation

Different question types require different evaluation strategies.

### Deterministic Evaluation

Deterministic evaluation is used when an expected answer can be checked reliably.

Example:

```text

Ground truth:

Madhya Pradesh

Model response:

Gwalior is located in the Indian state of Madhya Pradesh.

Result:

PASS

```

Another example:

```text

Question:

What is ln(-1) in the real number system?

Expected concept:

undefined

```

For questions like these, simple deterministic checks are fast and reproducible.

---

### Required-Concept Evaluation

Some responses can be correct even when they do not exactly match the reference wording.

For example:

```text

Question:

I drink 6 bottles of water every day.

How many liters of water do I drink?

Expected behavior:

Recognize that the volume of each bottle is missing.

```

Valid responses may use different expressions such as:

- bottle size

- bottle volume

- capacity of each bottle

- not enough information

- insufficient information

The evaluator can therefore check for required concepts instead of demanding one exact sentence.

---

### Rubric-Based LLM Judge

Reasoning responses are harder to evaluate using simple phrase matching.

For selected reasoning questions, an LLM judge receives:

```text

Question

+

Reference answer

+

Evaluation rubric

+

Model response

```

The judge returns structured JSON containing:

- PASS or FAIL verdict

- Criterion-level results

- A short explanation

Example structure:

```json

{

  "verdict": "PASS",

  "criteria": [

    {

      "criterion_number": 1,

      "met": true

    },

    {

      "criterion_number": 2,

      "met": true

    }

  ],

  "reason": "The response reaches the correct conclusion and satisfies the reasoning criteria."

}

```

This evaluation path was introduced after the original rule-based evaluator produced a false negative on a logically correct reasoning response.

That exposed an important limitation of keyword-based evaluation:

```text

Semantic correctness

does not always equal

literal phrase matching

```

---

## Example Evaluation Insight

During development, one reasoning response correctly concluded that loving dogs as pets does not imply loving dogs as food.

The original required-phrase evaluator marked the response incorrect because the model expressed the correct reasoning using different wording.

A rubric-based LLM judge later evaluated the same type of response correctly.

This highlighted an important benchmarking principle:

> Evaluation systems themselves can introduce errors.

A benchmark therefore needs to distinguish between:

- Model failure

- Evaluator failure

- API or infrastructure failure

---

## Latency Measurement

The benchmark measures elapsed client-side API time using Python's:

```python

time.perf_counter()

```

The measured latency represents **end-to-end API response time from the client application's perspective**.

It may include:

- Network delay

- API overhead

- Model processing

- Response transmission

It should therefore not be interpreted as pure model inference time.

Repeated runs are supported because individual API latency measurements can vary significantly.

The analysis layer currently reports:

- Mean latency

- Median latency

Using both is useful because large latency outliers can strongly affect the arithmetic mean.

---

## Rate-Limit Handling

During repeated benchmark experiments, API quota limits can temporarily return HTTP 429 rate-limit errors.

The project includes basic retry handling that:

1\. Detects rate-limit-related failures.

2\. Reads the suggested retry delay when available.

3\. Waits before retrying.

4\. Limits the maximum number of retry attempts.

This prevents immediate failure during temporary quota exhaustion.

The current retry mechanism is intentionally simple and can be improved in future versions.

---

## Result Storage

Each model run can be stored as a structured record containing information such as:

```json

{

  "question_id": "Q002",

  "model": "gemini-3.6-flash",

  "run": 1,

  "response": "Model response text",

  "correct": true,

  "latency_seconds": 9.113,

  "evaluation_method": "llm_judge"

}

```

When an LLM judge is used, the judge verdict, criterion-level checks, and explanation can also be preserved.

Raw experiment results are stored separately from derived summary metrics.

```text

results.json

    |

    v

analyze_results.py

    |

    v

summary.json

```

This makes it possible to recompute analysis later without rerunning the model.

---

## Project Structure

```text

llm-benchmarking-suite/

|

├── data/

│   └── benchmark.json

|

├── results/

│   ├── results.json

│   └── summary.json

|

├── analyze_results.py

├── api_utils.py

├── evaluator.py

├── llm_judge.py

├── run_benchmark.py

├── requirements.txt

├── .gitignore

└── README.md

```

---

## Installation

Install the required dependency:

```bash

pip install -r requirements.txt

```

The current implementation uses the Google Gemini API.

Set the Gemini API key as an environment variable:

```text

GEMINI_API_KEY

```

API keys should never be written directly into source code or committed to the repository.

---

## Running the Benchmark

Run:

```bash

python run_benchmark.py

```

The runner:

1\. Loads the benchmark dataset.

2\. Builds the appropriate prompt.

3\. Calls the configured LLM.

4\. Measures response latency.

5\. Selects the configured evaluation method.

6\. Evaluates the response.

7\. Stores structured results.

The number of repeated runs can be configured in the benchmark runner.

---

## Analyzing Results

Run:

```bash

python analyze_results.py

```

The analysis layer can calculate:

- Total evaluated runs

- Correct runs

- Run-level accuracy

- Mean latency

- Median latency

- Category-level performance

- Evaluation-method usage

It also generates:

```text

results/summary.json

```

The summary reflects only the experiment records currently present in `results.json`.

It should not be interpreted as the performance of the full benchmark unless the complete benchmark has actually been executed.

---

## Current Status

The project is an actively developing prototype.

### Implemented

- 12-question categorized benchmark dataset

- Six benchmark categories

- Gemini model integration

- Context-aware prompt construction

- Full-dataset benchmark runner

- Deterministic evaluation

- Required-concept evaluation

- Rubric-based LLM judging

- Latency measurement

- Repeated-run support

- Structured result storage

- Analysis pipeline

- Basic rate-limit retry handling

### Current Experimental Limitation

The complete 12-question benchmark has not yet been used to produce a final large-scale or multi-model evaluation report.

API free-tier quota limits have also affected some experimental runs.

For this reason, partial experiment summaries should not be presented as final benchmark-wide performance results.

---

## In Progress / Planned

- Expand the benchmark to approximately 40–60 curated questions

- Integrate at least one additional LLM

- Perform multi-model comparison

- Strengthen consistency evaluation

- Improve hallucination and error analysis

- Add optional API cost tracking

- Add a Streamlit dashboard

- Expand statistical analysis

- Add benchmark versioning

- Improve experiment reproducibility

- Improve resumable execution after API failures

---

## Known Limitations

- The current benchmark is intentionally small.

- Deterministic keyword-based evaluation can miss semantically correct responses.

- Required-concept matching remains phrase-sensitive.

- LLM judges can themselves make evaluation errors or exhibit bias.

- Generator and judge models may not be fully independent.

- Current saved results may represent partial experiments rather than a completed full benchmark.

- API latency includes network and service-side effects.

- API quotas can interrupt large benchmark runs.

- Multi-model comparison has not yet been implemented.

- Cost tracking has not yet been implemented.

- The current prototype focuses on LLM evaluation; computer-vision benchmarking is outside the current implementation.

---

## Future Work

Planned development includes:

1\. Expand the benchmark to 40–60 curated and reviewed questions.

2\. Integrate at least one additional LLM.

3\. Compare models across accuracy, latency, consistency, and error patterns.

4\. Improve hallucination evaluation.

5\. Add stronger semantic evaluation methods.

6\. Add optional API cost tracking.

7\. Add a Streamlit dashboard.

8\. Add benchmark versioning and experiment metadata.

9\. Improve API failure handling and resumable benchmark execution.

10\. Extend the broader benchmarking approach to computer-vision evaluation.

---

## Disclaimer

This is an independently developed educational and portfolio project.

It is not an Indian Army system, does not contain Indian Army internal datasets or confidential information, and does not represent any official Indian Army benchmarking implementation.