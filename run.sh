#!/bin/bash

cd bempp-rs
git pull
cargo update
cargo criterion --message-format json > output.json
cd ..
python3 process_results.py
python3 push.py
