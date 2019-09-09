#!/bin/bash

set -e

warn() {
    echo "$@" 1>&2;
}

mac_setup() {
    brew install "python@2"
    brew install "openssl@1.1"
    brew install libffi
    brew install libimobiledevice
}

linux_setup() {
    sudo apt-get install -y ideviceinstaller
    sudo apt-get install -y libimobiledevice-utils
}

platform="$(uname -s)"
if [[ "$platform" == 'Darwin' ]]; then
    mac_setup
elif [[ "$platform" == 'Linux' ]]; then
    linux_setup
else
    warn "Sorry, I don't know how to install on $platform.";
    exit 1;
fi;
