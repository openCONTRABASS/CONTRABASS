#!/bin/sh
py.test --log-cli-level=10 -s test/test_core/test_CobraMetabolicModel.py
py.test --log-cli-level=10 -s test/test_cli/test_contrabass_cli.py 

