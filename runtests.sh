#!/bin/bash

mkdir ~/.basespace

cp test/dotbasespace/*.bash ~/.basespace
cp test/dotbasespace/*.json ~/.basespace

cd data
curl -O https://s3.amazonaws.com/basespace-sdk-unit-test-data/BC-12_S12_L001_R2_001.fastq.gz
cd ..

# ...
cat test/dotbasespace/unit_tests.cfg | sed "s/__ACCESS_TOKEN__/$ACCESS_TOKEN/" > ~/.basespace/unit_tests.cfg
cp ~/.basespace/unit_tests.cfg ~/.basespace/default.cfg


python test/unit_tests.py
