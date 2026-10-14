# Kaltura A2UI Catalog

[A2UI](https://a2ui.org) component catalog for [Kaltura Experience Components](https://corp.kaltura.com/).

Published at: **https://kaltura.github.io/a2ui/v2/catalog.json** (current). `v1` stays online for agents that still use it.

The renderers for this catalog live in [kaltura-a2ui-components](https://github.com/kaltura/kaltura-a2ui-components). `v2` is a copy of the `kaltura_catalog.json` asset of one of its releases.

## What This Is

This catalog defines Kaltura's custom A2UI components — rich media widgets that AI agents can embed inline in their responses. Clients that support the A2UI protocol use this catalog to render Kaltura Experience Components natively.

### Available Components (v2)

The 18 basic A2UI components, plus:

| Component | Description |
|-----------|-------------|
| **KalturaPlayer** | Plays one entry, with an optional start time and clip end |
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

Props never carry a Kaltura Session (KS). The host app supplies it in code. See each component's props in [docs/components.md](https://github.com/kaltura/kaltura-a2ui-components/blob/main/docs/components.md).

### Files

```
v2/
├── catalog.json          # Current catalog (JSON Schema), 18 basic + 12 Kaltura components
└── examples/             # Player, clip, flashcards and chart messages
v1/                       # Legacy. Kaltura components only, with a `ks` prop
├── catalog.json
├── common_types.json
└── examples/
```

## How It Works

1. The [Kaltura Agent](https://github.com/kaltura/kaltura-gemini-agent) advertises this catalog in its AgentCard
2. Clients request catalog negotiation during session setup
3. The agent emits declarative A2UI JSON referencing this catalog's components
4. Clients render the components using their registered implementations

See the [A2UI specification](https://a2ui.org) for protocol details.

## Publishing

This catalog is automatically published to GitHub Pages when:
- Changes are pushed to `main` in this repository
- The Kaltura Agent's CI pipeline syncs catalog updates from the source of truth

The source of truth for `v2` is the [kaltura-a2ui-components](https://github.com/kaltura/kaltura-a2ui-components) release asset `kaltura_catalog.json`. After each release, copy it to `v2/catalog.json`.

`v1` is synced from the [kaltura-gemini-agent](https://github.com/kaltura/kaltura-gemini-agent) repository (`src/kaltura_agent/ui/catalogs/`). Changes flow: agent repo -> this repo -> GitHub Pages.

## License

Copyright 2026 Kaltura Inc. All rights reserved.
