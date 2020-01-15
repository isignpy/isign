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
trap 'rm -r "$tempdir"' EXIT

cp "$ipa_file" "$tempdir"
cd "$tempdir"
unzip -qq "$ipa_basename"
find "Payload" -type d -name "*.app" | while IFS= read -r appdir; do
  find "$appdir" -name "*.dylib" | while IFS= read -r dylib; do
      echo "checking $dylib..."
      codesign --verify --verbose "$dylib";
  done;
  find "$appdir" -type d -name "*.framework" | while IFS= read -r framework; do
      echo "checking $framework..."
      codesign --verify --verbose "$framework";
  done;
  echo "checking $appdir..."
  codesign --display --verbose=4 "$appdir";
  codesign --verify --verbose=4 --deep "$appdir";
done;
