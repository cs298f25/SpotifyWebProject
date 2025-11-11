#!/bin/bash

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install npm spotify node module
# TODO: Add npm install spotify-web-api-node. You may need to install node.js first.

# Install dependencies
pip install -r requirements.txt