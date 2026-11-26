"""Checks the v3 and v4 catalogs and examples with the official A2UI Python SDK.

Run: python -I scripts/sdk-check.py [root]

Needs: pip install -r scripts/requirements-sdk.txt
Exits 1 if a catalog does not load or any example is rejected.
"""
import json
import sys
from pathlib import Path

from a2ui.inference_formats.direct_json import DirectJsonFormatFactory
from a2ui.parser import A2uiPart
from a2ui.processor import A2uiGenerator, CatalogConfig

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)

failures = 0
total = 0
for version in ("v3", "v4"):
    catalog_id = f"https://kaltura.github.io/a2ui/{version}/catalog.json"
    try:
        config = CatalogConfig.from_path(str(root / version / "catalog.json"), catalog_id=catalog_id)
        processor = A2uiGenerator([config], inference_format_factory=DirectJsonFormatFactory()).create_processor(
            {"1.0": {"supportedCatalogIds": [catalog_id]}}
        )
    except Exception as error:
        sys.exit(f"{version}/catalog.json: {error}")

    files = sorted((root / version / "examples").glob("*.json"))
    if not files:
        sys.exit(f"{version}/examples: no examples")
    total += len(files)

    for file in files:
        try:
            messages = json.loads(file.read_text(encoding="utf-8"))["messages"]
            parts = processor.parse_response(json.dumps(messages), wrapped=False)
            parsed = [message for part in parts if isinstance(part, A2uiPart) for message in part.a2ui]
            if len(parsed) != len(messages):
                raise ValueError(f"parsed {len(parsed)} of {len(messages)} messages")
            print(f"ok   {version}/{file.name} ({len(parsed)} messages)")
        except Exception as error:
            failures += 1
            print(f"FAIL {version}/{file.name}: {str(error)[:500]}")

if failures:
    sys.exit(f"{failures} of {total} examples failed")
print(f"{total} examples ok")
