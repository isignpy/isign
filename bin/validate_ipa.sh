#!/bin/bash
# 
# Quickly check that an IPA's signature is valid and satisfies its designated requirement.
# Only works on MacOS.
#

set -e


ipa_file=$1
ipa_basename=$(basename $ipa_file)

tempdir=$(mktemp -d)
cp $ipa_file "$tempdir"
cd "$tempdir"
unzip -qq $ipa_basename
find "Payload" -type d -name "*.app" | while IFS= read -r appdir; do
  echo "checking $appdir..."
  codesign -vv $appdir;
done;

rm -r $tempdir
