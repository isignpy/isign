#!/bin/bash


ipa_file=$1

function warn() {
  echo "$@" 1>&2
}

if [[ -z $APP_STORE_USERNAME ]] || [[ -z $APP_STORE_PASSWORD ]]; then
  warn "Must have APP_STORE_USERNAME and APP_STORE_PASSWORD in environment. Consult isign docs/submit.md";
  exit 1;
fi

if which "xcrun"; then 
  warn "found xcrun...";
else
  warn "Can't find xcrun. Run \`xcode-select -r\` ?";
  exit 1;
fi

function altool_cmd() {
  local command="$1"
  xcrun altool "--$command" --file "$ipa_file" --username "$APP_STORE_USERNAME" --password "$APP_STORE_PASSWORD"
}

function validate() {
  altool_cmd "validate-app"
}

function upload() {
  altool_cmd "upload-app"
}

validate && upload;
