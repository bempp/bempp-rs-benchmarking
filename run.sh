#!/bin/bash

if [[ -z "$PYTHON" ]]; then
  PYTHON="python3"
fi
if [[ -z "$CARGO" ]]; then
  CARGO="cargo"
fi
git pull && \
cd bempp-rs && \
git pull && \
$CARGO update && \
$CARGO criterion --message-format json > output.json && \
cd .. && \
$PYTHON process_results.py && \
$PYTHON push.py && \
git pull && \
$PYTHON make_html.py > plots.html && \
$PYTHON update_website.py plots.html
