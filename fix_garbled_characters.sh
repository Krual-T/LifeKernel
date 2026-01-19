#!/usr/bin/env bash
set -euo pipefail

profile=""
if [ -n "${ZSH_VERSION-}" ]; then
  profile="$HOME/.zshrc"
else
  profile="$HOME/.bashrc"
fi

marker="# LifeKernel: ensure UTF-8 locale"
snippet=$'\n# LifeKernel: ensure UTF-8 locale\nexport LANG=${LANG:-en_US.UTF-8}\nexport LC_ALL=${LC_ALL:-en_US.UTF-8}\n'

if [ -f "$profile" ] && grep -q "$marker" "$profile"; then
  echo "UTF-8 locale config already present in $profile"
else
  printf "%s" "$snippet" >> "$profile"
  echo "Added UTF-8 locale config to $profile"
fi

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
