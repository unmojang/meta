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


LEGACY_RELEASE_TIMES = {
    1: "2018-06-28T21:14:02+08:00",
    2: "2018-06-28T21:14:02+08:00",
    3: "2018-06-28T21:14:02+08:00",
    4: "2018-06-28T21:14:02+08:00",
    6: "2018-06-28T21:14:02+08:00",
    7: "2018-06-28T21:15:12+08:00",
    8: "2018-06-28T21:26:23+08:00",
    9: "2018-06-28T21:28:04+08:00",
    10: "2018-06-28T21:28:14+08:00",
    11: "2018-06-28T21:28:23+08:00",
    12: "2018-06-28T21:28:29+08:00",
    13: "2018-06-28T21:28:35+08:00",
    14: "2018-06-28T21:28:42+08:00",
    15: "2018-06-28T21:28:49+08:00",
    16: "2018-06-28T21:28:55+08:00",
    17: "2018-06-28T21:29:00+08:00",
    18: "2018-06-29T13:25:41+00:00",
    19: "2018-09-30T13:17:16+00:00",
    20: "2018-10-20T13:43:43+00:00",
    21: "2018-10-20T13:49:31+00:00",
    22: "2018-11-23T16:11:54+00:00",
    23: "2018-11-24T17:16:56+00:00",
    24: "2018-12-31T13:03:32+00:00",
    25: "2019-01-19T15:40:25+00:00",
    26: "2019-02-14T05:26:31+00:00",
    27: "2020-04-10T16:05:12+00:00",
    28: "2020-04-29T02:46:56+00:00",
    29: "2020-06-20T14:30:17Z",
    30: "2020-08-15T03:08:38Z",
    31: "2020-08-23T07:06:55Z",
    32: "2020-08-27T04:21:52Z",
    33: "2020-09-11T23:27:27Z",
    34: "2020-10-17T17:18:31Z",
    35: "2021-05-14T06:55:24Z",
    36: "2021-06-11T10:34:18Z",
    37: "2021-06-11T19:55:54Z",
    38: "2021-06-13T22:05:49Z",
    39: "2021-08-20T20:30:11Z",
    40: "2021-11-18T13:49:40Z",
    41: "2022-03-11T05:48:00Z",
    42: "2022-03-15T18:07:46Z",
    43: "2022-04-20T17:21:18Z",
    44: "2022-05-03T13:42:48Z",
    45: "2022-06-06T18:02:59Z",
    46: "2022-07-02T06:06:24Z",
    47: "2022-07-14T11:37:08Z",
    48: "2022-08-04T16:53:00Z",
    49: "2022-08-05T17:11:21Z",
    50: "2023-03-25T10:42:43Z",
    51: "2023-06-11T18:47:31Z",
}


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

                if "release_time" in artifact:
                    release_time = dateutil.parser.isoparse(artifact["release_time"])
                elif build_number in LEGACY_RELEASE_TIMES:
                    release_time = LEGACY_RELEASE_TIMES[build_number]
                else:
                    continue

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
