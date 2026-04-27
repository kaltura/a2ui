# Kaltura A2UI Catalog

[A2UI](https://a2ui.org) component catalog for [Kaltura Experience Components](https://corp.kaltura.com/).

Published at: **https://kaltura.github.io/a2ui/v1/catalog.json**

## What This Is

This catalog defines Kaltura's custom A2UI components — rich media widgets that AI agents can embed inline in their responses. Clients that support the A2UI protocol use this catalog to render Kaltura Experience Components natively.

### Available Components

| Component | Description | Status |
|-----------|-------------|--------|
| **KalturaPlayer** | Player v7 — DRM, multi-audio, 30+ plugins, captions, analytics, ad insertion | Published |
| KalturaGenie | Conversational AI search widget | Planned |
| KalturaMediaManager | Browsable content library | Planned |
| KalturaAnalytics | Interactive analytics dashboards | Planned |
| KalturaRecorder | Express Recorder for capturing media | Planned |
| KalturaCaptionsEditor | In-browser caption editing | Planned |
| KalturaAvatar | Conversational AI avatar | Planned |
| KalturaContentLab | AI content generation studio | Planned |
| KalturaAgentsWidget | Agent management interface | Planned |
| KalturaVodAvatar | Video-on-demand avatar experience | Planned |
| KalturaChat | Embedded chat interface | Planned |

### Files

```
v1/
├── catalog.json          # Component catalog (JSON Schema)
├── common_types.json     # A2UI common types (from A2UI spec v0.9)
└── examples/
    ├── player_basic.json         # Basic player embed
    └── player_with_title.json    # Player with autoplay and seek
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

The source of truth for catalog schemas lives in the [kaltura-gemini-agent](https://github.com/kaltura/kaltura-gemini-agent) repository at `src/kaltura_agent/ui/catalogs/`. Changes flow: agent repo -> this repo -> GitHub Pages.

## License

Copyright 2026 Kaltura Inc. All rights reserved.
