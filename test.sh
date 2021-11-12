#!/bin/sh
cd test
py.test --log-cli-level=10 -s test_findCPcli.py
