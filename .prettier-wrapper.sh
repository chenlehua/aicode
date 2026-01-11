#!/bin/bash
# Wrapper script for prettier to handle paths correctly
cd w1/project-alpha/frontend
for file in "$@"; do
  # Remove the w1/project-alpha/frontend/ prefix if present
  relative_file="${file#w1/project-alpha/frontend/}"
  if [ -f "$relative_file" ]; then
    npx prettier --write "$relative_file"
  fi
done
