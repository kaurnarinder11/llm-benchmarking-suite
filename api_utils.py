import re
import time


def create_interaction_with_retry(
    client,
    *,
    model,
    input,
    response_format=None,
    max_retries=3
):
    for attempt in range(1, max_retries + 1):

        try:
            kwargs = {
                "model": model,
                "input": input
            }

            if response_format is not None:
                kwargs["response_format"] = response_format

            return client.interactions.create(**kwargs)

        except Exception as error:
            message = str(error).lower()

            is_rate_limit = (
                "429" in message
                or "too_many_requests" in message
                or "rate limit" in message
            )

            if not is_rate_limit:
                raise

            if attempt == max_retries:
                raise

            match = re.search(
                r"retry in ([0-9.]+)s",
                message
            )

            if match:
                wait_seconds = float(match.group(1)) + 2
            else:
                wait_seconds = 10 * attempt

            print(
                f"Rate limit reached. "
                f"Waiting {wait_seconds:.1f}s "
                f"before retry {attempt + 1}/{max_retries}..."
            )

            time.sleep(wait_seconds)