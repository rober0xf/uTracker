#!/bin/bash
if [[ $(pwd) == */app/tests ]]; then
    cd ../../
fi
python -m pytest app/tests/test_post_fighters.py -v
