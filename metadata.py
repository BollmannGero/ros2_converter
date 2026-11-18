from collections.abc import Iterable
from pathlib import Path

import yaml


# Validate only the streams whose file columns occur in the CSV index.
EXPECTED_METADATA = {
    "rgb_file": {"rgb_format": "jpeg"},
    "depth_file": {
        "depth_format": "rvl",
        "depth_dtype": "uint16",
        "depth_unit": "mm",
    },
}


def read_metadata(folder: Path) -> dict[str, object]:
    """Read the logger metadata as a YAML mapping."""
    with (folder / "meta.yaml").open(encoding="utf-8") as file:
        metadata = yaml.safe_load(file)
    if not isinstance(metadata, dict):
        raise ValueError("meta.yaml must contain a mapping of keys to values")
    return metadata


def validate_metadata(metadata: dict[str, object], columns: Iterable[str]) -> None:
    """Reject missing or unsupported format declarations for the indexed streams."""
    for column in columns:
        for key, expected in EXPECTED_METADATA.get(column, {}).items():
            if key not in metadata:
                raise ValueError(f"meta.yaml: required field {key} for {column} is missing")
            if metadata[key] != expected:
                raise ValueError(
                    f"meta.yaml: {key}={metadata[key]!r} is not supported; "
                    f"expected: {expected!r}"
                )
