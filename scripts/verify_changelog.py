#!/usr/bin/env python3
"""
Verify that CHANGELOG.md has been updated with the current version.
This script is used as a pre-commit hook to ensure changelog updates
are not forgotten when making changes.
"""

import os
import sys
import re
import tomli

def get_current_version():
    """Get the current version from pyproject.toml."""
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
    return pyproject["tool"]["poetry"]["version"]

def get_latest_changelog_version():
    """Get the latest version from CHANGELOG.md."""
    if not os.path.exists("CHANGELOG.md"):
        return None

    with open("CHANGELOG.md", "r") as f:
        content = f.read()

    # Look for version headers in the format ## [x.y.z]
    version_pattern = r"##\s*\[(\d+\.\d+\.\d+(?:-\w+(?:\.\d+)?)?)\]"
    matches = re.findall(version_pattern, content)

    return matches[0] if matches else None

def main():
    current_version = get_current_version()
    changelog_version = get_latest_changelog_version()

    if not changelog_version:
        print("Error: No version entries found in CHANGELOG.md")
        print("Please add an entry for version", current_version)
        sys.exit(1)

    if current_version != changelog_version:
        print(f"Error: Version mismatch between pyproject.toml ({current_version}) "
              f"and CHANGELOG.md ({changelog_version})")
        print("\nPlease update CHANGELOG.md with the current version and its changes.")
        print("Example format:")
        print(f"\n## [{current_version}] - YYYY-MM-DD")
        print("### Added")
        print("- New features")
        print("\n### Changed")
        print("- Updates to existing functionality")
        print("\n### Fixed")
        print("- Bug fixes")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
