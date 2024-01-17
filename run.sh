#!/bin/bash

if [[ -z "$PYTHON" ]]; then
  PYTHON="python3"
fi
git pull && \
cd bempp-rs && \
git pull && \
cargo update && \
cargo criterion --message-format json > output.json && \
cd .. && \
python3 process_results.py && \
python3 push.py && \
git pull && \
python3 make_html.py > plots.html && \
python3 update_website.py plots.html
