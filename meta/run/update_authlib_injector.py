import json
import os
import zipfile

import requests

from meta.common import (
    upstream_path,
    ensure_upstream_dir,
    default_session,
)
from meta.common.authlib_injector import BASE_DIR, ARTIFACTS_DIR
from meta.model.fabric import FabricJarInfo

UPSTREAM_DIR = upstream_path()

ensure_upstream_dir(BASE_DIR)
ensure_upstream_dir(ARTIFACTS_DIR)

sess = default_session()


def get_json_file(path, url):
    with open(path, "w", encoding="utf-8") as f:
        r = sess.get(url)
        r.raise_for_status()
        print(f"AUTHLIB-INJECTOR DEBUG {r.headers}")
        version_json = r.json()
        json.dump(version_json, f, sort_keys=True, indent=4)
        return version_json


def main():
    artifacts = get_json_file(
        os.path.join(UPSTREAM_DIR, BASE_DIR, "artifacts.json"),
        "https://authlib-injector.yushi.moe/artifacts.json",
    )

    for artifact in artifacts["artifacts"]:
        build_number = artifact["build_number"]
        print(f"Processing artifact {build_number}")
        get_json_file(
            os.path.join(UPSTREAM_DIR, ARTIFACTS_DIR, f"{build_number}.json"),
            f"https://authlib-injector.yushi.moe/artifact/{build_number}.json",
        )


if __name__ == "__main__":
    main()
