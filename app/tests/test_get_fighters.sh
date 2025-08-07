#!/bin/bash
if [[ $(pwd) == */app/tests ]]; then
    cd ../../
fi
python -m pytest app/tests/test_get_fighters.py -v
