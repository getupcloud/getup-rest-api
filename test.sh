#!/bin/bash

export PYTHONPATH="$PWD:$PWD/tests:$PYTHONPATH"
for PARAM; do
	if [ -e "$PARAM" ]; then
		TESTS+="$PARAM "
	else
		FLAGS+="$PARAM "
	fi
done

if [ ${#TESTS} -eq 0 ]; then
	TESTS="tests/test_*.py"
fi
test -ex
export CONFIG_FILE=$PWD/tests/test.conf
for test_file in $TESTS; do
	#if [ -e tests/${test_file%.py}.conf ]; then
	#	export CONFIG_FILE=$PWD/tests/${test_file%.py}.conf
	#else
	#	export CONFIG_FILE=$PWD/tests/test.conf
	#fi
	py.test $FLAGS $test_file
done
