#!/bin/bash
# 
# Quickly check that an IPA's signature is valid and satisfies its designated requirement,
# including embedded app bundles.
#
# Also prints signing info to STDOUT. Check that authority is the same and correct.
# .
# Only works on MacOS.
#

set -e

ipa_file=$1
ipa_basename=$(basename "$ipa_file")

tempdir=$(mktemp -d)
echo $tempdir
#trap 'rm -r "$tempdir"' EXIT

function verify_signables() {
  local type="$1"
  local extension="$2"
  echo "Checking for $2..."
  find "Payload" -type "$type" -name "*.$extension" | while IFS= read -r signable; do
      echo "======"
      echo "checking $signable..."
      codesign --verify --verbose "$signable";
      if [[ "$type" == 'd' ]]; then
          codesign --display --verbose=4 --extract-certificates "$signable";
          codesign --verify --verbose=4 --deep "$signable";
      fi
  done;
}

cp "$ipa_file" "$tempdir"
cd "$tempdir"
unzip -qq "$ipa_basename"

verify_signables d "app"
verify_signables f "dylib"
verify_signables f "framework"
verify_signables d "appex"
