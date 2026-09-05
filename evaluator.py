def evaluate_response(item, model_response):
    response = model_response.lower().strip()

    evaluation = item["evaluation"]
    method = evaluation["method"]

    if method == "contains":
        expected = evaluation["expected"].lower().strip()
        return expected in response

    if method == "required_concepts":
        concept_groups = evaluation["concepts"]

        for alternatives in concept_groups:
            concept_found = False

            for phrase in alternatives:
                if phrase.lower() in response:
                    concept_found = True
                    break

            if not concept_found:
                return False

        return True

    return False