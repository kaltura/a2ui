"""Runs the sample agent once. Valid A2UI messages go to stdout as JSON lines.

python main.py           the client lists the v3 catalog
python main.py --plain   the client does not, so the agent answers in plain text
python main.py --serve   serve the agent over A2A on http://127.0.0.1:8080
"""
import asyncio
import json
import sys

from agent import CATALOG_ID, REPO_ROOT, agent_card, handle_request
from a2ui.constants import A2UI_RENDERER_CAPABILITIES_KEY
from fake_llm import FakeLlm, reply_from_example

# To use a real model, replace this line with: MODEL = "gemini-3.5-flash" (and set GOOGLE_API_KEY).
MODEL = FakeLlm(a2ui_reply=reply_from_example(REPO_ROOT / "v3/examples/search-form.json"))


async def main() -> None:
    supported = [] if "--plain" in sys.argv else [CATALOG_ID]
    metadata = {A2UI_RENDERER_CAPABILITIES_KEY: {"1.0": {"supportedCatalogIds": supported}}}

    card = agent_card()
    extension = card.capabilities.extensions[0]
    print(f"agent card: {extension.uri} {json.dumps(extension.params)}", file=sys.stderr)

    reply = await handle_request("Show me a search form.", metadata, MODEL)
    if reply.text:
        print(f"agent text: {reply.text}", file=sys.stderr)
    for message in reply.messages:
        print(json.dumps(message))


if "--serve" in sys.argv:
    import uvicorn
    from server import build_app

    uvicorn.run(build_app(MODEL), host="127.0.0.1", port=8080)
else:
    asyncio.run(main())
