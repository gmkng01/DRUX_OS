#!/bin/bash

python -m venv example

source example/bin/activate

pip install pandas requests bs4

example/bin/python mirrorlist_script.py