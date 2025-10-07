import json
import os
import zipfile
import re

import requests
import dateutil.parser

from github import Github
from github import Auth

from meta.common import (
    upstream_path,
    ensure_upstream_dir,
    default_session,
)
from meta.common.authlib_injector import BASE_DIR
from meta.model.fabric import FabricJarInfo

UPSTREAM_DIR = upstream_path()

ensure_upstream_dir(BASE_DIR)

sess = default_session()

auth = Auth.Token(os.environ["GITHUB_TOKEN"])

g = Github(auth=auth)


def main():
    artifacts = []

    r = sess.get("https://authlib-injector.yushi.moe/artifacts.json")
    r.raise_for_status()
    authlib_injector_artifacts = r.json()
    for artifact in authlib_injector_artifacts["artifacts"]:
        version = artifact["version"]
        build_number = artifact["build_number"]
        r = sess.get(f"https://authlib-injector.yushi.moe/artifact/{build_number}.json")
        r.raise_for_status()
        version_json = r.json()
        artifacts.append(
            {
                "vendor": "moe.yushi",
                "version": version,
                "release_time": version_json["release_time"],
                "download_url": version_json["download_url"],
            }
        )

    for release in g.get_repo("unmojang/authlib-injector").get_releases():
        version = re.sub(r"^v", "", release.tag_name)
        jar_asset = None
        jar_asset_name = f"unmojang-injector-{version}.jar"
        for asset in release.get_assets():
            if asset.name == jar_asset_name:
                jar_asset = asset
        if jar_asset is None:
            raise ValueError(
                f"no asset found for release {release.url} with name {jar_asset_name}"
            )
        artifacts.append(
            {
                "vendor": "org.unmojang",
                "version": version,
                "release_time": release.created_at.isoformat(),
                "download_url": asset.browser_download_url,
            }
        )

    artifacts = list(
        reversed(
            sorted(artifacts, key=lambda a: dateutil.parser.isoparse(a["release_time"]))
        )
    )

    with open(
        os.path.join(UPSTREAM_DIR, BASE_DIR, f"artifacts.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(artifacts, f, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
