#!/usr/bin/env bash
python3 -m coverage run --append $1 --unit-test > /dev/null
exit $?
