#! /bin/bash

if [ "$1" = "all" ]; then
	# Until I get the telegraph running on not-Pis,
	# don't run tests requiring GPIO by default.
	python3 -m unittest `find test -name "test_*.py"`
else
	python3 -m unittest test.test_commonFunctions test.telegraph.test_destinationConfig
fi
