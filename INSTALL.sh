#!/bin/bash

set -e

warn() {
    echo "$@" 1>&2;
}

brew_install() {
    # brew is stupid and returns an error if the package was already installed
    # bash is also stupid and makes it hard to capture stderr
    local package_name=$1 
    local retval=0
    local tmp_error=$(mktemp)
    if ! brew install "$package_name" 2>"$tmp_error"; then
        if ! grep "is already installed" "$tmp_error"; then
            retval=1
        fi
    fi
    cat "$tmp_error"
    echo "brew install $package_name result: $retval"
    return "$retval"
}

mac_setup() {
    brew_install "python@2"
    brew_install "openssl@1.1"
    brew_install libffi
    brew_install libimobiledevice
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
