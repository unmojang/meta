import json
import os
from typing import Optional

import dateutil.parser

from meta.common import (
    ensure_component_dir,
    launcher_path,
    upstream_path,
)
from meta.common.loki import RELEASES_DIR, AGENT_COMPONENT
from meta.model import Agent, MetaVersion, MetaPackage, GradleSpecifier

LAUNCHER_DIR = launcher_path()
UPSTREAM_DIR = upstream_path()

ensure_component_dir(AGENT_COMPONENT)


def main():
    releases_dir = os.path.join(UPSTREAM_DIR, RELEASES_DIR)

    latest_version: Optional[str] = None
    latest_time = None

    for filename in os.listdir(releases_dir):
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(releases_dir, filename), "r", encoding="utf-8") as f:
            release = json.load(f)

        version = release["version"]
        release_time = dateutil.parser.isoparse(release["published_at"])

        if latest_time is None or release_time > latest_time:
            latest_time = release_time
            latest_version = version

        v = MetaVersion(
            name="Loki",
            uid=AGENT_COMPONENT,
            version=version,
            release_time=release_time,
        )
        v.type = "release"
        v.additional_agents = [
            Agent(
                name=GradleSpecifier(
                    group="org.unmojang",
                    artifact="Loki",
                    version=version,
                ),
                absoluteUrl=release["download_url"],
            )
        ]
        v.write(os.path.join(LAUNCHER_DIR, AGENT_COMPONENT, f"{version}.json"))
        print(f"Generated Loki {version}")

    package = MetaPackage(uid=AGENT_COMPONENT, name="Loki")
    package.recommended = [latest_version] if latest_version else []
    package.description = (
        "Patch (nearly) any Minecraft version to use custom API servers"
    )
    package.project_url = "https://github.com/unmojang/Loki"
    package.authors = ["unmojang"]
    package.write(os.path.join(LAUNCHER_DIR, AGENT_COMPONENT, "package.json"))


if __name__ == "__main__":
    main()
