#!/bin/bash

source ~/.profile

script_dir=$(dirname "$0")
python3 $script_dir/update_website.py
