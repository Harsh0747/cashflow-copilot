from __future__ import annotations

import json
import os
from typing import Any


def generate_finance_summary(payload: dict[str, Any]) -> str | None:
    """Return an LLM summary when configured; otherwise return None.

    The model receives aggregates and explanations, not raw bank descriptions.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-5.6")
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a cautious small-business cash-flow analyst. "
                        "Use only the supplied numbers. Clearly label uncertainty. "
                        "Do not provide investment, lending, tax, or legal advice. "
                        "Return four concise bullets: outlook, key driver, biggest risk, next action."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, default=str)},
            ],
        )
        return response.output_text
    except Exception:
        return None
