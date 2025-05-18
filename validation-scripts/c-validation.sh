#!/bin/bash
for file in "$@"; do
  if ! gcc -fsyntax-only "$file" 2>/dev/null; then
    echo "C syntax error in $file"
    exit 1
  fi
done
echo "C files passed"
