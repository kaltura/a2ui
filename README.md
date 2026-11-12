# Kaltura A2UI Catalog

[A2UI](https://a2ui.org) component catalog for [Kaltura Experience Components](https://corp.kaltura.com/): a Player, flashcards, charts, a media manager and more, as widgets an agent can place in a reply.

**Current catalog: https://kaltura.github.io/a2ui/v3/catalog.json** (A2UI 1.0). The renderers live in [kaltura-a2ui-components](https://github.com/kaltura/kaltura-a2ui-components). Live demo: https://kaltura.github.io/kaltura-a2ui-components/.

| Folder | Catalog id | A2UI protocol | Renderer release |
|---|---|---|---|
| `v3/` | `https://kaltura.github.io/a2ui/v3/catalog.json` | 1.0 | [kaltura-a2ui-components 0.7.x](https://github.com/kaltura/kaltura-a2ui-components/releases/tag/v0.7.0) on `@a2ui/react` and `@a2ui/web_core` 0.15 |
| `v2/`, `v1/` | Same pattern | 0.9 and older | Stay online unchanged. Do not use them for new agents |

## Components (v3)

The 18 basic A2UI components, plus:

| Component | Description |
|-----------|-------------|
| **KalturaPlayer** | Plays one entry or a playlist, with an optional start time and clip end |
| **KalturaFlashcards** | Flashcard deck with optional video clips |
| **KalturaChart** | Bar, line, area, pie and other charts from literal data |
| KalturaMediaManager | Browse and pick entries |
| KalturaAnalytics | Analytics dashboard view |
| KalturaRecorder | Express Recorder |
| KalturaCaptionsEditor | Caption editing |
| KalturaAvatar | Conversational AI avatar |
| KalturaGenie | Conversational AI search |
| KalturaContentLab | AI content generation |
| KalturaAgentsWidget | Agent management |
| KalturaVodAvatar | Video-on-demand avatar |

Props never carry a Kaltura Session (KS). The host app supplies it in code. Props are listed in [docs/components.md](https://github.com/kaltura/kaltura-a2ui-components/blob/main/docs/components.md).

## Files

```
v3/
├── catalog.json          # Catalog (JSON Schema 2020-12), 18 basic + 12 Kaltura components
├── common_types.json     # Shared A2UI types, byte copy from @a2ui/web_core 0.15
└── examples/             # 12 message lists: {name, description, messages}
```

## Use it in an agent

1. Advertise the catalog id in the AgentCard.
2. Read `a2uiRendererCapabilities` from the client and answer in plain text when the id is missing.
3. Send A2UI 1.0 messages whose `createSurface.catalogId` is the catalog id.
4. Treat what the model returns as untrusted. Validate it against `catalog.json` before you send it.

`catalog.json` has an `instructions` field written for the model. Pass it into your prompt.

A runnable example on Google ADK is in [samples/adk-agent](samples/adk-agent/README.md). It runs offline with a fake model. `scripts/sdk-check.py` checks the catalog and examples with the official A2UI Python SDK in CI.

## Checks

`npm run validate` runs on every pull request and before every deploy:

- v3 passes the A2UI 1.0 catalog meta-schema (`catalog_definition.json`).
- `common_types.json` is the file from `@a2ui/web_core`.
- Every example is a valid list of agent-to-renderer messages for this catalog.
- Every `catalogId` equals its publish URL.

## Update the catalog

`v3/catalog.json` is the `kaltura_catalog.json` asset of a kaltura-a2ui-components release. Never edit it by hand.

```bash
gh release download vX.Y.Z --repo kaltura/kaltura-a2ui-components --pattern kaltura_catalog.json --pattern common_types.json --dir /tmp/asset
cp /tmp/asset/kaltura_catalog.json v3/catalog.json && cp /tmp/asset/common_types.json v3/common_types.json
npm run validate
```

Open a pull request. After the merge, `deploy-pages.yml` publishes to GitHub Pages. Check the served bytes with `curl -fsSL https://kaltura.github.io/a2ui/v3/catalog.json | cmp - /tmp/asset/kaltura_catalog.json`.

## License

Apache-2.0. See [LICENSE](LICENSE).
