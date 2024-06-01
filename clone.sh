#!/usr/bin/env bash
set -ex

if [ -f config.sh ]; then
    source config.sh
fi

if [ ! -d "${META_UPSTREAM_DIR}" ]; then
    git clone "${META_UPSTREAM_REPO}" "${META_UPSTREAM_DIR}"
fi

if [ ! -d "${META_LAUNCHER_DIR}" ]; then
    git clone "${META_LAUNCHER_REPO}" "${META_LAUNCHER_DIR}"
fi
