#!/usr/bin/env bash
NAMES=$(cat .gitmodules | grep 'path = ' | awk '{print $3}')

if ! [ "$1" == '--somerepo' ]; then
  # we will exclude somerepo unless you explicity clone it yourself (a huge download)
  if [ ! -e "lib/deps/SomeRepo/.git" ]; then
    NAMES=$(echo "$NAMES" | grep -v 'SomeRepo')
  fi
fi

set -euxo pipefail
git submodule update --init --recursive --progress --depth=1 --checkout $NAMES
