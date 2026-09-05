import json


JUDGE_MODEL = "gemini-3.8-flash"


def judge_response(client, item, model_response):
    rubric = item["evaluation"]["rubric"]

    rubric_text = "\n".join(
        f"{index + 1}. {criterion}"
        for index, criterion in enumerate(rubric)
    )

    judge_prompt = f"""
You are evaluating an AI model response.

QUESTION:
{item["question"]}

REFERENCE ANSWER:
{item["ground_truth"]}

RUBRIC:
{rubric_text}

MODEL RESPONSE:
{model_response}

Judge the response only against the rubric.

PASS means every required criterion is satisfied.
FAIL means at least one required criterion is not satisfied.

Keep the reason brief.
"""

    interaction = client.interactions.create(
        model=JUDGE_MODEL,
        input=judge_prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "verdict": {
                        "type": "string",
                        "enum": ["PASS", "FAIL"]
                    },
                    "criteria": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "criterion_number": {
                                    "type": "integer"
                                },
                                "met": {
                                    "type": "boolean"
                                }
                            },
                            "required": [
                                "criterion_number",
                                "met"
                            ]
                        }
                    },
                    "reason": {
                        "type": "string"
                    }
                },
                "required": [
                    "verdict",
                    "criteria",
                    "reason"
                ]
            }
        }
    )

    return json.loads(interaction.output_text)