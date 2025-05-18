#!/bin/bash
#Prerequisites:
OS="$(uname)"

# Check if mcs (Mono C# compiler) is installed
if ! command -v mcs &> /dev/null; then
  echo "mcs not found. Attempting to install Mono..."

  if [[ "$OS" == "Linux" ]]; then
    if [ -f /etc/debian_version ]; then
      sudo apt update
      sudo apt install -y mono-complete
    else
      echo "Unsupported Linux distro. Please install Mono manually."
      exit 1
    fi

  elif [[ "$OS" == "Darwin" ]]; then
    if command -v brew &> /dev/null; then
      brew update
      brew install mono
    else
      echo "Homebrew not found. Please install Homebrew and try again."
      exit 1
    fi

  else
    echo "Unsupported OS: $OS. Please install Mono manually."
    exit 1
  fi

else
  echo "mcs is already installed."
fi

echo "Mono version:"
mcs --version

# File validation
for file in "$@"; do
  if ! mcs -parse "$file" 2>/dev/null; then
    echo "C# syntax error in $file"
    exit 1
  fi
done
echo "C# files passed"
