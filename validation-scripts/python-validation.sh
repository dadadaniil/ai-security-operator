#!/bin/bash
for file in "$@" ; do
  if ! python -c "import importlib.util; spec = importlib.util.spec_from_file_location('mod', '$file'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)" 2>/dev/null; then
    echo "Python syntax/import error in $file"
    exit 1
  fi
done
echo "Python files passed"
