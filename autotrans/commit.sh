#!/bin/bash

set -x
git config user.name github-actions[bot]
git config user.email 41898282+github-actions[bot]@users.noreply.github.com
git add -f autotrans/cache.json contents/japanese-auto
git commit -m "update translation"
git push -f
