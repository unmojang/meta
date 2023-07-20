#!/usr/bin/env bash
set -e

BASEDIR=$(dirname "$0")
cd "${BASEDIR}" || exit 1
BASEDIR=$(pwd)
BASEDIR_ESCAPED="$(printf '%q' "$BASEDIR")"

source config.sh
if [ -f config/config_local.sh ]; then
    source config/config_local.sh
fi

set -x

if [ ! -d "${UPSTREAM_DIR}" ]; then
    GIT_SSH_COMMAND="ssh -i ${BASEDIR_ESCAPED}/config/upstream.key" git clone "${UPSTREAM_REPO}" "${UPSTREAM_DIR}"
fi

if [ ! -d "${LAUNCHER_DIR}" ]; then
    GIT_SSH_COMMAND="ssh -i ${BASEDIR_ESCAPED}/config/launcher.key" git clone "${LAUNCHER_REPO}" "${LAUNCHER_DIR}"
fi
