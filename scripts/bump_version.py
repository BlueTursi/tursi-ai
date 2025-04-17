#!/usr/bin/env python3
"""
Version bumping utility for Tursi.
Usage: python scripts/bump_version.py [major|minor|patch] [--pre-release=alpha|beta|rc] [--pre-number=N]
"""
import argparse
import re
import tomli
import tomli_w
from datetime import datetime
from pathlib import Path

def parse_version(version: str):
    """Parse version string into components."""
    # Match regular versions and pre-releases
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta|rc)\.(\d+))?$", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")

    parts = match.groups()
    return {
        "major": int(parts[0]),
        "minor": int(parts[1]),
        "patch": int(parts[2]),
        "pre_type": parts[3],
        "pre_num": int(parts[4]) if parts[4] else None
    }

def bump_version(current_version: str, bump_type: str, pre_release: str = None, pre_number: int = None) -> str:
    """
    Bump version according to semver rules.

    Args:
        current_version: Current version string
        bump_type: Type of bump (major, minor, patch)
        pre_release: Type of pre-release (alpha, beta, rc)
        pre_number: Pre-release number

    Returns:
        New version string
    """
    parts = parse_version(current_version)

    # Handle regular version bumping
    if bump_type == "major":
        parts["major"] += 1
        parts["minor"] = 0
        parts["patch"] = 0
    elif bump_type == "minor":
        parts["minor"] += 1
        parts["patch"] = 0
    elif bump_type == "patch":
        parts["patch"] += 1

    # Construct new version
    new_version = f"{parts['major']}.{parts['minor']}.{parts['patch']}"

    # Add pre-release if specified
    if pre_release:
        pre_num = pre_number if pre_number is not None else 1
        new_version += f"-{pre_release}.{pre_num}"

    return new_version

def update_pyproject(new_version: str):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")

    with open(pyproject_path, "rb") as f:
        data = tomli.load(f)

    old_version = data["tool"]["poetry"]["version"]
    data["tool"]["poetry"]["version"] = new_version

    with open(pyproject_path, "wb") as f:
        tomli_w.dump(data, f)

    return old_version

def update_changelog(old_version: str, new_version: str):
    """Add new version section to CHANGELOG.md if it doesn't exist."""
    changelog_path = Path("CHANGELOG.md")
    today = datetime.now().strftime("%Y-%m-%d")

    if not changelog_path.exists():
        print("Warning: CHANGELOG.md not found")
        return

    content = changelog_path.read_text()

    # Check if version already exists
    if f"## [{new_version}]" in content:
        print(f"Version {new_version} already exists in CHANGELOG.md")
        return

    # Find the position to insert new version (after the first ## if it exists)
    lines = content.splitlines()
    insert_pos = 0

    for i, line in enumerate(lines):
        if line.startswith("## ["):
            insert_pos = i
            break

    # Prepare new version section
    new_section = f"""## [{new_version}] - {today}
### Added
-

### Changed
-

### Deprecated
-

### Removed
-

### Fixed
-

### Security
-
"""

    # Insert new section
    lines.insert(insert_pos, new_section)
    changelog_path.write_text("\n".join(lines))

def main():
    parser = argparse.ArgumentParser(description="Bump version for Tursi")
    parser.add_argument("bump_type", choices=["major", "minor", "patch"],
                      help="Type of version bump")
    parser.add_argument("--pre-release", choices=["alpha", "beta", "rc"],
                      help="Create a pre-release version")
    parser.add_argument("--pre-number", type=int,
                      help="Pre-release number (defaults to 1)")

    args = parser.parse_args()

    try:
        # Read current version
        with open("pyproject.toml", "rb") as f:
            current_version = tomli.load(f)["tool"]["poetry"]["version"]

        # Calculate new version
        new_version = bump_version(
            current_version,
            args.bump_type,
            args.pre_release,
            args.pre_number
        )

        # Update files
        old_version = update_pyproject(new_version)
        update_changelog(old_version, new_version)

        print(f"Successfully bumped version: {old_version} → {new_version}")
        print("\nNext steps:")
        print("1. Review and update CHANGELOG.md")
        print("2. Commit changes:")
        print(f"   git commit -am 'chore(release): prepare for version {new_version}'")
        print("3. Create and push tag:")
        print(f"   git tag -a v{new_version} -m 'Release v{new_version}'")
        print(f"   git push origin v{new_version}")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
