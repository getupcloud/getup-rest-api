#!/bin/bash

if [ -z "$AUTHUSER" -o -z "$AUTHTOKEN" ]; then
	echo Missing credentials: AUTHUSER=\"$AUTHUSER\" - AUTHTOKEN=\"$AUTHTOKEN\"
	exit 1
fi

print_json ()
{
	for json_file; do
		echo "-- response content ($json_file) --"
		python -c "import pprint, json; pprint.pprint(json.loads(open(\"$json_file\").read()))"
	done
}

request ()
{
	expected=$1
	path=$2
	shift 2
	cmd="curl -k --user $AUTHUSER:$AUTHTOKEN https://broker.getupcloud.com/broker/rest$path $@"
	echo "  -- $cmd"
	status=`$cmd --silent -o test-request-$$.log -w '%{http_code}'`
	echo "  -- expecting status $expected, got $status"
	[ $status -eq $expected ]
}

fail ()
{
	echo ---------
	print_json test-request-$$.log
	echo
	echo ---------
	echo -e "$@"
	exit 1
}

DOM=testdom
APP=testapp
CART=mysql-5.1

trap "rm -f test-request-$$.log" EXIT

if ! request 404 /domains/$DOM; then
	fail "Domain \"$DOM\" already exists? Try to remove it first.
	  \$ curl -kv --user \"$AUTHUSER:$AUTHTOKEN\" https://broker.getupcloud.com/broker/rest/domains/$DOM -X DELETE --data force=true"
fi

test_broker()
{
	echo testing domain create
	request 201 /domains --data id=$DOM || fail Error creating domain
	echo testing domain retrieve
	request 200 /domains/$DOM || fail Error retrieving domain
	echo testing application create
	request 201 /domains/$DOM/applications --data "name=$APP&cartridge=php-5.3&scale=true" || fail Error creating application
	echo testing application retrieve
	request 200 /domains/$DOM/applications/$APP || fail Error retrieving application
	cp test-request-$$.log test-app.log

	echo testing cartridge create
	request 201 /domains/$DOM/applications/$APP/cartridges --data "name=$CART" || fail Error creating cartridge
	echo testing cartridge retrieve
	request 200 /domains/$DOM/applications/$APP/cartridges/$CART || fail Error retrieving application

	echo testing application scale-up
	request 200 /domains/$DOM/applications/$APP/events --data 'event=scale-up' || fail Error scalling-up application
	echo testing application scale-up '(again)'
	request 200 /domains/$DOM/applications/$APP/events --data 'event=scale-up' || fail Error scalling-up application '(again)'
	echo testing application scale-down
	request 200 /domains/$DOM/applications/$APP/events --data 'event=scale-down' || fail Error scalling-down application
	echo testing application scale-down '(again)'
	request 200 /domains/$DOM/applications/$APP/events --data 'event=scale-down' || fail Error scalling-down application '(again)'

	echo testing cartridge destroy
	request 200 /domains/$DOM/applications/$APP/cartridges/$CART -X DELETE || fail Error destroying cartridge
	echo testing application destroy
	request 204 /domains/$DOM/applications/$APP -X DELETE || fail Error destroying application
	echo testing domain destroy
	request 204 /domains/$DOM -X DELETE || ail Error destroying domain
	#print_json test-app.log
	rm -f test-app.log
}

time test_broker
