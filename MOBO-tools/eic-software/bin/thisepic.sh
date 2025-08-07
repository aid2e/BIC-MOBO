#!/bin/sh

export DETECTOR=epic
export DETECTOR_PATH=/w/eic-scshelf2104/users/dereka/aid2e/dRICH-MOBO/MOBO-tools/eic-software/share/epic
export DETECTOR_CONFIG=${1:-epic}
export DETECTOR_VERSION=v0.0.0-unknown

## Warn is not the right name (this script is sourced, hence $1)
if [[ "$(basename ${BASH_SOURCE[0]})" != "thisepic.sh" ]]; then
        echo "Warning: This script will cease to exist at '$(realpath --no-symlinks ${BASH_SOURCE[0]})'."
        echo "         Please use the version at '$(realpath --no-symlinks $(dirname ${BASH_SOURCE[0]})/bin/thisepic.sh)'."
fi

## Export detector libraries
if [[ "$(uname -s)" = "Darwin" ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        export DYLD_LIBRARY_PATH="/w/eic-scshelf2104/users/dereka/aid2e/dRICH-MOBO/MOBO-tools/eic-software/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
else
        export LD_LIBRARY_PATH="/w/eic-scshelf2104/users/dereka/aid2e/dRICH-MOBO/MOBO-tools/eic-software/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
