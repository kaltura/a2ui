"""Serves the sample agent over A2A. See README.md."""
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import Part, TextPart
from a2a.utils import get_message_text, new_agent_parts_message
from a2ui.a2a import create_a2ui_parts
from google.adk.models.base_llm import BaseLlm

from agent import agent_card, handle_request


class SampleExecutor(AgentExecutor):
    """Runs one A2A request through `handle_request`. The client's A2UI catalogs ride in message metadata."""

    def __init__(self, model: BaseLlm | str):
        self.model = model

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        message = context.message
        reply = await handle_request(get_message_text(message) if message else "", message.metadata if message else None, self.model)
        parts = [Part(root=TextPart(text=reply.text))] if reply.text else []
        parts += create_a2ui_parts(reply.messages, "1.0")
        await event_queue.enqueue_event(new_agent_parts_message(parts))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("The sample does not support cancel.")


def build_app(model: BaseLlm | str, url: str = "http://localhost:8080/"):
    """The Starlette app. The AgentCard is served at /.well-known/agent-card.json."""
    handler = DefaultRequestHandler(agent_executor=SampleExecutor(model), task_store=InMemoryTaskStore())
    return A2AStarletteApplication(agent_card=agent_card(url), http_handler=handler).build()
