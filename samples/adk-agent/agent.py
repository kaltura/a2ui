"""A small A2UI agent on Google ADK. See README.md."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2ui.a2a import get_a2ui_agent_extension
from a2ui.constants import A2UI_RENDERER_CAPABILITIES_KEY
from a2ui.core import A2uiError
from a2ui.inference_formats.direct_json import DirectJsonFormatFactory
from a2ui.parser import A2uiPart, TextPart, to_message_dicts
from a2ui.processor import A2uiGenerator, A2uiRequestProcessor, CatalogConfig
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.runners import InMemoryRunner
from google.genai import types

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_ID = "https://kaltura.github.io/a2ui/v3/catalog.json"

# One folder per catalog id. Each holds catalog.json and examples/*.json.
CATALOG_FOLDERS = {CATALOG_ID: REPO_ROOT / "v3"}

INSTRUCTION = "You help people find and work with media in their Kaltura library."
PLAIN_INSTRUCTION = f"{INSTRUCTION} Answer in plain text only."
APP_NAME = "kaltura-a2ui-sample"
USER_ID = "sample-user"


@dataclass
class Reply:
    text: str
    messages: list[dict[str, Any]] = field(default_factory=list)


def load_generators(folders: dict[str, Path] = CATALOG_FOLDERS) -> dict[str, A2uiGenerator]:
    """One generator per catalog id. Its few-shot examples come from the same folder."""
    generators = {}
    for catalog_id, folder in folders.items():
        config = CatalogConfig.from_path(str(folder / "catalog.json"), catalog_id=catalog_id)
        examples = [
            json.loads(file.read_text(encoding="utf-8"))["messages"]
            for file in sorted((folder / "examples").glob("*.json"))
        ]
        generators[catalog_id] = A2uiGenerator(
            [config], examples=examples, inference_format_factory=DirectJsonFormatFactory()
        )
    return generators


def create_processor(
    generators: dict[str, A2uiGenerator], capabilities: dict[str, Any] | None
) -> A2uiRequestProcessor | None:
    """Builds the processor for one request. None if the client lists no catalog we hold."""
    for generator in generators.values():
        try:
            return generator.create_processor(capabilities)
        except A2uiError:
            continue
    return None


def agent_card(url: str = "http://localhost:8080/") -> AgentCard:
    """The A2A card. The A2UI extension lists the catalog ids this agent can use."""
    return AgentCard(
        name="Kaltura A2UI sample",
        description="Answers media questions with A2UI surfaces.",
        url=url,
        version="0.1.0",
        capabilities=AgentCapabilities(
            extensions=[get_a2ui_agent_extension("1.0", supported_catalog_ids=list(CATALOG_FOLDERS))]
        ),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[AgentSkill(id="media-help", name="Media help", description="Search and review media.", tags=["media"])],
    )


async def handle_request(
    text: str, metadata: dict[str, Any] | None, model: BaseLlm | str, generators: dict[str, A2uiGenerator] | None = None
) -> Reply:
    """Runs one request.

    `metadata` is the A2A message metadata. The client sends its catalogs under
    `a2uiRendererCapabilities`. Raises A2uiError if the model output is not valid A2UI.
    """
    generators = generators if generators is not None else load_generators()
    capabilities = (metadata or {}).get(A2UI_RENDERER_CAPABILITIES_KEY)
    processor = create_processor(generators, capabilities)
    instruction = f"{INSTRUCTION}\n\n{processor.prompt_snippet}" if processor else PLAIN_INSTRUCTION

    # A function, not a string: ADK reads {name} in a string as session state, and the A2UI prompt has braces.
    agent = LlmAgent(name="media_agent", model=model, instruction=lambda _context: instruction)
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    answer = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=text)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            answer = "".join(part.text or "" for part in event.content.parts)

    if processor is None:
        return Reply(text=answer)

    # Model output is untrusted. The processor checks it against the catalog and raises if it fails.
    reply = Reply(text="")
    for part in processor.parse_response(answer):
        if isinstance(part, TextPart):
            reply.text += part.text
        elif isinstance(part, A2uiPart):
            reply.messages += to_message_dicts(part.a2ui)
    return reply
