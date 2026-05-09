import hashlib
import io
import json
import os
import zipfile

import requests

from meta.common import (
    upstream_path,
    ensure_upstream_dir,
    default_session,
)
from meta.common.loki import BASE_DIR, RELEASES_DIR

UPSTREAM_DIR = upstream_path()

ensure_upstream_dir(BASE_DIR)
ensure_upstream_dir(RELEASES_DIR)

sess = default_session()

GITHUB_API = "https://api.github.com/repos/unmojang/Loki/releases"


def verify_loki_jar(jar_bytes: bytes) -> bool:
    with zipfile.ZipFile(io.BytesIO(jar_bytes)) as jar:
        return "org/unmojang/loki/Loki.class" in jar.namelist()


def main():
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = sess.get(GITHUB_API, headers=headers, params={"per_page": 100})
    r.raise_for_status()
    releases = r.json()

    for release in releases:
        tag = release["tag_name"]
        version = tag.lstrip("v")
        published_at = release["published_at"]

        jar_name = f"Loki-{version}.jar"
        download_url = None
        for asset in release["assets"]:
            if asset["name"] == jar_name:
                download_url = asset["browser_download_url"]
                break

        if not download_url:
            print(f"Skipping {version}: no asset named {jar_name}")
            continue

        out_path = os.path.join(UPSTREAM_DIR, RELEASES_DIR, f"{version}.json")
        if os.path.exists(out_path):
            print(f"Skipping {version}: already cached")
            continue

        print(f"Downloading and verifying Loki {version}...")
        jar_response = requests.get(download_url, headers=headers)
        jar_response.raise_for_status()
        jar_bytes = jar_response.content

        if not verify_loki_jar(jar_bytes):
            print(f"Skipping {version}: JAR does not contain a recognised Loki class")
            continue

        sha256 = hashlib.sha256(jar_bytes).hexdigest()
        size = len(jar_bytes)

        release_info = {
            "version": version,
            "download_url": download_url,
            "published_at": published_at,
            "sha256": sha256,
            "size": size,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(release_info, f, sort_keys=True, indent=4)

        print(f"Stored Loki {version}")


if __name__ == "__main__":
    main()
