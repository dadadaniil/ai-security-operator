#!/bin/bash
for file in "$@"; do
  if ! javac "$file" 2>/dev/null; then
    echo "Java syntax error in $file"
    exit 1
  fi
done
echo "Java files passed"
