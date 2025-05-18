#!/bin/bash
for file in "$@"; do
  if ! node -c "$file" 2>/dev/null; then
    echo "JavaScript syntax error in $file"
    exit 1
  fi
done
echo "JavaScript files passed"
