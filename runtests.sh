#!/bin/bash

set -e

mkdir ~/.basespace

cp test/dotbasespace/*.bash ~/.basespace
cp test/dotbasespace/*.json ~/.basespace

cd data
curl -O https://s3.amazonaws.com/basespace-sdk-unit-test-data/BC-12_S12_L001_R2_001.fastq.gz
cd ..

# ...
cat test/dotbasespace/unit_tests.cfg | sed "s/__ACCESS_TOKEN__/$ACCESS_TOKEN/" > ~/.basespace/unit_tests.cfg
cp ~/.basespace/unit_tests.cfg ~/.basespace/default.cfg

pip install pyflakes

echo
echo "Static analysis warnings from pyflakes:"
echo
# exclude doc directory because those files are auto-generated
find .  \( -path ./doc -o -path ./src/build \) -prune -o -name '*.py' -print | xargs pyflakes || true

# TODO add stricter flake8 checking here
# (checks for proper formatting of code in compliance with PEP8)


echo
echo "Unit test output:"
echo


python test/unit_tests.py


exit $?
