"""A fake ADK model. It needs no API key and no network."""
import json
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from a2ui.constants import A2UI_CLOSE_TAG, A2UI_OPEN_TAG
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.models import LlmCapabilities
from google.genai import types


def reply_from_example(path: Path) -> str:
    """Builds a model reply from a catalog example: a sentence, then the A2UI block."""
    messages = json.loads(path.read_text(encoding="utf-8"))["messages"]
    return f"Here is your form.\n{A2UI_OPEN_TAG}\n{json.dumps(messages)}\n{A2UI_CLOSE_TAG}"


class FakeLlm(BaseLlm):
    """Answers with `a2ui_reply` when the system prompt asks for A2UI, else with `plain_reply`."""

    model: str = "fake-a2ui"
    a2ui_reply: str
    plain_reply: str = "I cannot show a UI here. Ask me in text and I will answer in text."

    @property
    def capabilities(self) -> LlmCapabilities:
        return LlmCapabilities(output_schema_and_tools=False)

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        system_prompt: Any = llm_request.config.system_instruction if llm_request.config else ""
        wants_a2ui = A2UI_OPEN_TAG in str(system_prompt or "")
        text = self.a2ui_reply if wants_a2ui else self.plain_reply
        usage = types.GenerateContentResponseUsageMetadata(prompt_token_count=0, candidates_token_count=0, total_token_count=0)
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]), usage_metadata=usage)
