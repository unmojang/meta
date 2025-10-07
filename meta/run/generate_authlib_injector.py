import json
import os

import dateutil.parser

from meta.common import (
    ensure_component_dir,
    launcher_path,
    upstream_path,
)
from meta.common.authlib_injector import BASE_DIR, ARTIFACTS_DIR, AGENT_COMPONENT
from meta.model import Agent, MetaVersion, Library, MetaPackage, GradleSpecifier

LAUNCHER_DIR = launcher_path()
UPSTREAM_DIR = upstream_path()

ensure_component_dir(AGENT_COMPONENT)


def main():
    recommended_version: Optional[str] = None

    with open(
        os.path.join(UPSTREAM_DIR, BASE_DIR, "artifacts.json"), "r", encoding="utf-8"
    ) as artifacts_file:
        artifacts = json.load(artifacts_file)

        latest_release_time = None

        for artifact in artifacts:
            version = artifact["version"]
            if artifact["vendor"] == "org.unmojang":
                version += ".unmojang"

            print(f"Processing agent {version}")

            release_time = dateutil.parser.isoparse(artifact["release_time"])

            if artifact["vendor"] == "org.unmojang":
                if latest_release_time is None or release_time > latest_release_time:
                    latest_release_time = release_time
                    recommended_version = version

            v = MetaVersion(
                name="authlib-injector",
                uid=AGENT_COMPONENT,
                version=version,
                release_time=release_time,
            )
            v.type = "release"
            v.additional_agents = [
                Agent(
                    name=GradleSpecifier(
                        group="moe.yushi",
                        artifact="authlibinjector",
                        version=version,
                    ),
                    absoluteUrl=artifact["download_url"],
                )
            ]
            v.write(os.path.join(LAUNCHER_DIR, AGENT_COMPONENT, f"{v.version}.json"))

    package = MetaPackage(uid=AGENT_COMPONENT, name="authlib-injector")
    package.recommended = [recommended_version]
    package.description = "authlib-injector enables you to build a Minecraft authentication system offering all the features that genuine Minecraft has."
    package.project_url = "https://github.com/yushijinhun/authlib-injector"
    package.authors = ["Haowei Wen"]
    package.write(os.path.join(LAUNCHER_DIR, AGENT_COMPONENT, "package.json"))


if __name__ == "__main__":
    main()
