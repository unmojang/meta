import datetime
import json
import os

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
    latest_version: Optional[str] = None

    with open(
        os.path.join(UPSTREAM_DIR, BASE_DIR, "artifacts.json"), "r", encoding="utf-8"
    ) as artifacts_file:
        artifacts = json.load(artifacts_file)
        latest_build = 0
        for artifact_info in artifacts["artifacts"]:
            build_number = artifact_info["build_number"]
            print(f"Processing agent {build_number}")
            with open(
                os.path.join(UPSTREAM_DIR, ARTIFACTS_DIR, f"{build_number}.json"),
                "r",
                encoding="utf-8",
            ) as artifact_file:
                artifact = json.load(artifact_file)
                version = artifact["version"]

                latest_build = max(latest_build, build_number)
                if latest_build == build_number:
                    latest_version = version

                v = MetaVersion(
                    name="authlib-injector",
                    uid=AGENT_COMPONENT,
                    version=version,
                    release_time=datetime.datetime.now(),
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
                v.write(
                    os.path.join(LAUNCHER_DIR, AGENT_COMPONENT, f"{v.version}.json")
                )

    package = MetaPackage(uid=AGENT_COMPONENT, name="authlib-injector")
    package.recommended = [latest_version]
    package.description = "authlib-injector enables you to build a Minecraft authentication system offering all the features that genuine Minecraft has."
    package.project_url = "https://github.com/yushijinhun/authlib-injector"
    package.authors = ["Haowei Wen"]
    package.write(os.path.join(LAUNCHER_DIR, AGENT_COMPONENT, "package.json"))


if __name__ == "__main__":
    main()
