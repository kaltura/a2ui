"""Checks the v3 catalog and examples with the official A2UI Python SDK.

Run: python -I scripts/sdk-check.py [root]

Needs: pip install -r scripts/requirements-sdk.txt
Exits 1 if the catalog does not load or any example is rejected.
"""
import json
import sys
from pathlib import Path

from a2ui.inference_formats.direct_json import DirectJsonFormatFactory
from a2ui.parser import A2uiPart
from a2ui.processor import A2uiGenerator, CatalogConfig

CATALOG_ID = "https://kaltura.github.io/a2ui/v3/catalog.json"
RENDERER_CAPABILITIES = {"1.0": {"supportedCatalogIds": [CATALOG_ID]}}

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)

try:
    config = CatalogConfig.from_path(str(root / "v3/catalog.json"), catalog_id=CATALOG_ID)
    processor = A2uiGenerator([config], inference_format_factory=DirectJsonFormatFactory()).create_processor(
        RENDERER_CAPABILITIES
    )
except Exception as error:
    sys.exit(f"v3/catalog.json: {error}")

files = sorted((root / "v3/examples").glob("*.json"))
if not files:
    sys.exit("v3/examples: no examples")

failures = 0
for file in files:
    try:
        messages = json.loads(file.read_text(encoding="utf-8"))["messages"]
        parts = processor.parse_response(json.dumps(messages), wrapped=False)
        parsed = [message for part in parts if isinstance(part, A2uiPart) for message in part.a2ui]
        if len(parsed) != len(messages):
            raise ValueError(f"parsed {len(parsed)} of {len(messages)} messages")
        print(f"ok   {file.name} ({len(parsed)} messages)")
    except Exception as error:
        failures += 1
        print(f"FAIL {file.name}: {str(error)[:500]}")

if failures:
    sys.exit(f"{failures} of {len(files)} examples failed")
print(f"{len(files)} examples ok")
