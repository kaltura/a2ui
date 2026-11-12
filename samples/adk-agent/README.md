# ADK sample agent for the Kaltura A2UI catalog

A small [Google ADK](https://github.com/google/adk-python) agent that answers with A2UI 1.0 surfaces from the [v3 catalog](../../v3/catalog.json). It runs with a fake model, so it needs no API key and no network after `pip install`.

## What it shows

| Step | Where |
|---|---|
| Loads the catalog and keeps one folder per catalog id (`catalog.json` and `examples/`) | `agent.py`, `CATALOG_FOLDERS` and `load_generators` |
| Builds the A2UI processor per request from the client's `a2uiRendererCapabilities` | `agent.py`, `create_processor` |
| Replies in plain text when the client does not list the v3 catalog id | `agent.py`, `handle_request` |
| Lists the catalog id in the A2A AgentCard (A2UI extension, `supportedCatalogIds`) | `agent.py`, `agent_card` |
| Direct JSON output: the model writes `<a2ui-json>` blocks and the SDK validates them | `agent.py`, `processor.parse_response` |
| A2A server: AgentCard at `/.well-known/agent-card.json`, `message/send` on `/` | `server.py` |
| Fake ADK model that returns a v3 example | `fake_llm.py` |

`server.py` serves the agent over A2A (`python main.py --serve`). The client sends its catalogs in message metadata under `a2uiRendererCapabilities`, and each A2UI message comes back as its own data part.

## Run it

Needs Python 3.11 or newer. Tested on 3.12. Run these in `samples/adk-agent/`, inside a clone of this repo (the agent reads `../../v3`).

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

Valid A2UI messages print to stdout, one JSON object per line. The card and the agent text go to stderr.

```sh
.venv/bin/python main.py --plain   # client without the v3 id: plain text, no messages
.venv/bin/python main.py --serve   # A2A server on http://127.0.0.1:8080
.venv/bin/python -I test_agent.py  # tests, plain asserts (pytest also works)
```

## Use a real model

In `main.py`, change the `MODEL` line:

```python
MODEL = "gemini-3.5-flash"
```

Set `GOOGLE_API_KEY` first. Any model id that ADK supports works. The real-model path is not exercised by the tests or CI.

## Security

- Model output is untrusted. `handle_request` always validates it with the SDK and raises `A2uiError` if it fails. Never send unvalidated output to a client.
- Never put a Kaltura Session (KS) in a message. The host adds it.
- The prompt tells the model not to invent Kaltura IDs. Without that line, a real model made up a `partnerId` and a `uiconfId`.
