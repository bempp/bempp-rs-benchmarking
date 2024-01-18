#!/bin/bash

if [[ -z "$PYTHON" ]]; then
  PYTHON=python3
fi
$PYTHON -m pip install PyGithub
git clone https://github.com/bempp/bempp-rs
cargo install cargo-criterion
