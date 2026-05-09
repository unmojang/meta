import io
import json
import os
import zipfile

from github import Auth, Github, GithubRetry

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

REPO_SLUG = "unmojang/Loki"


def verify_loki_jar(jar_bytes: bytes) -> bool:
    with zipfile.ZipFile(io.BytesIO(jar_bytes)) as jar:
        return "org/unmojang/loki/Loki.class" in jar.namelist()


def main():
    token = os.environ.get("GITHUB_TOKEN")
    auth = Auth.Token(token) if token else None
    gh = Github(auth=auth, retry=GithubRetry())
    repo = gh.get_repo(REPO_SLUG)

    for release in repo.get_releases():
        tag = release.tag_name
        version = tag.lstrip("v")
        published_at = release.published_at.isoformat()

        jar_name = f"Loki-{version}.jar"
        download_url = None
        for asset in release.get_assets():
            if asset.name == jar_name:
                download_url = asset.browser_download_url
                break

        if not download_url:
            print(f"Skipping {version}: no asset named {jar_name}")
            continue

        out_path = os.path.join(UPSTREAM_DIR, RELEASES_DIR, f"{version}.json")
        if os.path.exists(out_path):
            print(f"Skipping {version}: already cached")
            continue

        print(f"Downloading and verifying Loki {version}...")
        jar_response = sess.get(download_url)
        jar_response.raise_for_status()
        jar_bytes = jar_response.content

        if not verify_loki_jar(jar_bytes):
            print(f"Skipping {version}: JAR does not contain a recognised Loki class")
            continue

        release_info = {
            "version": version,
            "download_url": download_url,
            "published_at": published_at,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(release_info, f, sort_keys=True, indent=4)

        print(f"Stored Loki {version}")


if __name__ == "__main__":
    main()
