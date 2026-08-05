"""Build the immutable wheel selector consumed by Beyond VRM."""

import hashlib
import json
import re
import sys
from pathlib import Path


WHEEL_PATTERN = re.compile(
    r"^pyopenjtalk-(?P<version>.+)-cp310-cp310-"
    r"(?P<platform>.+)\.whl$"
)


def platform_key(platform_tag):
    if platform_tag == "win_amd64":
        return "windows-x86_64-cp310"
    if platform_tag.endswith("_x86_64"):
        system = "macos" if platform_tag.startswith("macosx_") else "linux"
        return f"{system}-x86_64-cp310"
    if platform_tag.endswith("_arm64") and platform_tag.startswith("macosx_"):
        return "macos-arm64-cp310"
    raise ValueError(f"Unsupported release wheel platform: {platform_tag}")


def main():
    wheel_directory = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()
    wheels = {}
    version = ""
    for wheel in sorted(wheel_directory.glob("*.whl")):
        match = WHEEL_PATTERN.match(wheel.name)
        if not match:
            raise ValueError(f"Unexpected release wheel: {wheel.name}")
        current_version = match.group("version")
        if version and current_version != version:
            raise ValueError("Release wheels do not share one package version")
        version = current_version
        key = platform_key(match.group("platform"))
        if key in wheels:
            raise ValueError(f"Duplicate wheel for {key}")
        wheels[key] = {
            "filename": wheel.name,
            "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        }
    expected = {
        "linux-x86_64-cp310",
        "macos-arm64-cp310",
        "macos-x86_64-cp310",
        "windows-x86_64-cp310",
    }
    if set(wheels) != expected:
        raise ValueError(f"Incomplete platform matrix: {sorted(wheels)}")
    output_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "package": "pyopenjtalk",
                "version": version,
                "wheels": wheels,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
