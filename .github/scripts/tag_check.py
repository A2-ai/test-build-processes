#!/usr/bin/env python3
"""
Verify that the Cargo.toml version matches the Git tag.

This script ensures that releases are properly versioned by comparing
the version in Cargo.toml with the provided Git tag.
"""

import sys
import re
from pathlib import Path


def extract_version_from_tag(tag: str) -> str:
    """
    Extract version string from a Git tag.

    Expects tags in format: v1.2.3, v1.2.3-pre, v1.2.3-alpha.1, etc.
    """
    # Remove 'v' prefix if present
    if tag.startswith('v'):
        tag = tag[1:]

    # Extract version part (everything before any prerelease suffix)
    # For example: "1.2.3-pre" -> "1.2.3"
    match = re.match(r'^(\d+\.\d+\.\d+)', tag)
    if not match:
        raise ValueError(f"Invalid tag format: {tag}. Expected format: v1.2.3")

    return match.group(1)


def get_cargo_version() -> str:
    """Read version from Cargo.toml using simple regex parsing."""
    cargo_toml_path = Path("Cargo.toml")

    if not cargo_toml_path.exists():
        raise FileNotFoundError("Cargo.toml not found in current directory")

    with open(cargo_toml_path, "r") as f:
        content = f.read()

    # Look for version = "x.y.z" in the [package] section
    # This regex looks for 'version' followed by '=' and captures the quoted string
    match = re.search(r'^\s*version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)

    if not match:
        raise ValueError("Version not found in Cargo.toml")

    return match.group(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: tag_check.py <git-tag>", file=sys.stderr)
        print("Example: tag_check.py v0.1.0", file=sys.stderr)
        sys.exit(1)

    git_tag = sys.argv[1]

    try:
        # Extract version from tag
        tag_version = extract_version_from_tag(git_tag)
        print(f"Tag version: {tag_version}")

        # Get version from Cargo.toml
        cargo_version = get_cargo_version()
        print(f"Cargo.toml version: {cargo_version}")

        # Compare versions
        if tag_version == cargo_version:
            print(f"✓ Version match: {tag_version}")
            sys.exit(0)
        else:
            print(f"✗ Version mismatch!", file=sys.stderr)
            print(f"  Tag:        v{tag_version}", file=sys.stderr)
            print(f"  Cargo.toml: {cargo_version}", file=sys.stderr)
            print("", file=sys.stderr)
            print("Please update Cargo.toml version to match the tag.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
