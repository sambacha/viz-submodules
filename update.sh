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

# update submodule
git submodule update --init
# set tag for submodules
DEFAULT_TAG=v1.0.0"
# update
git config -f .gitmodules --get-regexp '^submodule\..*\.url$' |
    while read -r KEY MODULE_PATH; do
        NAME="$(echo "${KEY}" | sed 's/^submodule\.\(.*\)\.url$/\1/')"
        if [[ $NAME =~ "v1.0.0" ]]; then
          pushd "${NAME}"
          git checkout -b latest_tag_branch $DEFAULT_TAG                   
          popd
        fi
    done
