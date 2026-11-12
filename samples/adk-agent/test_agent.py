"""Tests for the sample agent. Run: python -I test_agent.py (or pytest)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent import CATALOG_ID, REPO_ROOT, agent_card, handle_request  # noqa: E402
from a2ui.constants import A2UI_RENDERER_CAPABILITIES_KEY  # noqa: E402
from a2ui.core import A2uiError  # noqa: E402
from fake_llm import FakeLlm, reply_from_example  # noqa: E402

EXAMPLE = REPO_ROOT / "v3/examples/search-form.json"


def capabilities(*catalog_ids: str) -> dict:
    return {A2UI_RENDERER_CAPABILITIES_KEY: {"1.0": {"supportedCatalogIds": list(catalog_ids)}}}


def ask(model: FakeLlm, metadata: dict | None):
    return asyncio.run(handle_request("Show me a search form.", metadata, model))


def test_valid_capabilities_give_validated_messages():
    reply = ask(FakeLlm(a2ui_reply=reply_from_example(EXAMPLE)), capabilities(CATALOG_ID))
    assert [next(key for key in message if key != "version") for message in reply.messages] == [
        "createSurface",
        "updateDataModel",
        "updateComponents",
    ]
    assert reply.messages[0]["createSurface"]["catalogId"] == CATALOG_ID


def test_capabilities_without_the_v3_id_give_plain_text():
    model = FakeLlm(a2ui_reply=reply_from_example(EXAMPLE))
    reply = ask(model, capabilities("https://example.com/other-catalog.json"))
    assert (reply.text, reply.messages) == (model.plain_reply, [])


def test_missing_capabilities_give_plain_text():
    model = FakeLlm(a2ui_reply=reply_from_example(EXAMPLE))
    reply = ask(model, None)
    assert (reply.text, reply.messages) == (model.plain_reply, [])


def test_unknown_component_is_rejected():
    bad = reply_from_example(EXAMPLE).replace('"component": "Card"', '"component": "NoSuchWidget"')
    try:
        ask(FakeLlm(a2ui_reply=bad), capabilities(CATALOG_ID))
    except A2uiError:
        return
    raise AssertionError("invalid model output was accepted")


def test_broken_json_is_rejected():
    try:
        ask(FakeLlm(a2ui_reply="<a2ui-json>\n[{\"version\": \n</a2ui-json>"), capabilities(CATALOG_ID))
    except A2uiError:
        return
    raise AssertionError("invalid model output was accepted")


def test_agent_card_lists_the_catalog_id():
    extension = agent_card().capabilities.extensions[0]
    assert extension.params["supportedCatalogIds"] == [CATALOG_ID]


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"ok   {test.__name__}")
    print(f"{len(tests)} tests passed")
