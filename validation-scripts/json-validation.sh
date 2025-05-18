#!/bin/bash
for file in "$@"; do
  if ! jq empty "$file" 2>/dev/null; then
    echo "JSON syntax error in $file"
    exit 1
  fi
done
echo "JSON files passed"
