
function getup()
{
	local $*
	local BASE_URL='http://api.getupcloud.com/'
	if [ -n "$app" ]; then
		if [ "${app/-}" == "$app" ]; then
			echo 'missing parameter: [APP]-[DOMAIN]'
			return 1
		fi
		local d=${app#*-}
		local a=${app%-*}
		local TOP="domain/$d/app/$a"
	elif [ -n "$dom" ]; then
		local TOP="domain/$dom"
	else
		echo "missing 'app' or 'dom'"
		return 1
	fi

	if [ -n "$tail" -a "${tail:0:1}" != '/' ]; then
		tail="/$tail"
	fi
	METHOD="${method:+-X ${method^^}}"
	DATA="${data:+--data $data}"
	set -x
	curl -v -H "Authorization: Token $token" $METHOD $BASE_URL$TOP$tail $DATA
	set +x 2>/dev/null
}

function getup-dom()
{
	local t=$1; shift
	getup dom=$t token=$TOKEN $@
}

function getup-app()
{
	local t=$1; shift
	getup app=$t token=$TOKEN $@
}

function getup-app-new()
{
	local t=$1; shift
	getup app=$t token=$TOKEN method=POST data="$@"
}

function getup-app-del()
{
	local t=$1; shift
	getup app=$t token=$TOKEN method=DELETE $@
}

function getup-app-scale()
{
	local t=$1 scale=$2; shift 2
	if [ "$scale" != up -a "$scale" != down ]; then
		if ! [[ $scale =~ ^[0-9]+$ ]]; then
			echo "invalid scale offset: $scale"
			echo "valid parameters: up | down | [number]"
			return 1
		fi
	fi
	getup app=$t token=$TOKEN method=POST tail="/scale" data="to=$scale"
}

echo getup-tool started
