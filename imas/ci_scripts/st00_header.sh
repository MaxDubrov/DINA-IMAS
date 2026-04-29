#!/bin/bash
#
# MODULE LOADER SCRIPT FOR CI/CD
# ===============================
#
# This script loads environment modules based on the selected toolchain.
# Module versions can be configured via environment variables for easy CI integration.
#
# USAGE:
#   ./st00_header.sh
#
# ENVIRONMENT VARIABLES:
#   TARGET           - Target to use DEBUG or RELEASE
#   TOOLCHAIN        - Toolchain to use (default: foss)
#   COMMON_MODULES   - Common modules for all toolchains (comma-separated)
#   FOSS_MODULES     - FOSS-specific modules (comma-separated)  
#   INTEL_MODULES    - Intel-specific modules (comma-separated)
#
set -e -o pipefail

echo "Loading modules..."

if test -f /etc/profile.d/modules.sh; then
    . /etc/profile.d/modules.sh
else
    . /usr/share/Modules/init/sh
fi
module purge

TOOLCHAIN=${TOOLCHAIN:-foss}

DEFAULT_COMMON_MODULES="iWrap/1.0.0-GCCcore-13.2.0"
DEFAULT_FOSS_MODULES="IMAS/3.39.0-foss-2023b,Viz/2.8.0-foss-2023b,XMLlib/3.3.2-GCC-13.2.0"
DEFAULT_INTEL_MODULES="IMAS/3.39.0-intel-2023b,Viz/2.8.0-intel-2023b,XMLlib/3.3.2-intel-compilers-2023.2.1"

COMMON_MODULES_LIST="${COMMON_MODULES:-$DEFAULT_COMMON_MODULES}"
FOSS_MODULES_LIST="${FOSS_MODULES:-$DEFAULT_FOSS_MODULES}"
INTEL_MODULES_LIST="${INTEL_MODULES:-$DEFAULT_INTEL_MODULES}"

IFS=',' read -ra COMMON_MODULES <<< "$COMMON_MODULES_LIST"
IFS=',' read -ra FOSS_MODULES <<< "$FOSS_MODULES_LIST"
IFS=',' read -ra INTEL_MODULES <<< "$INTEL_MODULES_LIST"

case "$TOOLCHAIN" in
    *foss*)
        echo "... foss toolchain"
        MODULES=("${COMMON_MODULES[@]}")
        MODULES+=("${FOSS_MODULES[@]}")
        export FC=gfortran
        export CC=gcc
        ;;
    *intel*)
        echo "... intel toolchain"
        MODULES=("${COMMON_MODULES[@]}")
        MODULES+=("${INTEL_MODULES[@]}")
        export FC=ifort
        export CC=icc
        ;;
    *)
        echo "... default toolchain"
        MODULES=("${COMMON_MODULES[@]}")
        MODULES+=("${FOSS_MODULES[@]}")
        export FC=gfortran
        export CC=gcc
        ;;
esac

echo "Modules to load:"
echo "${MODULES[@]}" | tr " " "\n"

module load "${MODULES[@]}"
echo "Done loading modules"

export TARGET="${TARGET:-DEBUG}"
export PYTHONPATH=${HOME}/IWRAP_ACTORS:${PYTHONPATH}
export PYTHONPATH=${DINA_ROOT}/tools/pyutil:${PYTHONPATH}

export DINA_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../.." &> /dev/null && pwd)
export GIT_URL=$(git remote get-url origin)
export GIT_COMMIT_ID=$(git rev-parse --verify HEAD)
export GIT_VERSION=$(git describe --tags --abbrev=0)

echo "TOOLCHAIN: $TOOLCHAIN"
echo "TARGET: $TARGET"
echo "DINA_ROOT: $DINA_ROOT"
echo "GIT_URL: $GIT_URL"
echo "GIT_COMMIT_ID: $GIT_COMMIT_ID"
echo "GIT_VERSION: $GIT_VERSION"

