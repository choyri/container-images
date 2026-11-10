#!/bin/sh
set -eu

fail() {
    printf '[warp] Error: %s\n' "$*" >&2
    exit 1
}

# Require an explicit mount so container recreation preserves registration.
awk '$5 == "/var/lib/cloudflare-warp" { found = 1 } END { exit !found }' \
    /proc/self/mountinfo ||
    fail 'Mount a named volume or host directory at /var/lib/cloudflare-warp.'
write_probe=$(mktemp /var/lib/cloudflare-warp/.write-test.XXXXXX 2>/dev/null) ||
    fail '/var/lib/cloudflare-warp must be writable.'
rm -f "$write_probe"
[ -c /dev/net/tun ] || fail 'Provide a TUN device with --device /dev/net/tun.'
[ -r /etc/3proxy/3proxy.cfg ] || fail 'Cannot read /etc/3proxy/3proxy.cfg.'

# Disable Mesh NAT initialization and prevent connector registration.
export SRCNAT_ENABLED=false
unset MESH_NODE_TOKEN

children=

# Stop each service group, including the upstream entrypoint's children.
stop_services() {
    for pid in $children; do
        kill -TERM "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || :
    done
    attempt=0
    while [ "$attempt" -lt 10 ]; do
        alive=false
        for pid in $children; do
            if kill -0 "-$pid" 2>/dev/null; then alive=true; fi
        done
        [ "$alive" = true ] || break
        sleep 1
        attempt=$((attempt + 1))
    done
    for pid in $children; do
        kill -KILL "-$pid" 2>/dev/null || :
        wait "$pid" 2>/dev/null || :
    done
    children=
}

trap stop_services EXIT
trap 'exit 0' HUP INT TERM

cli() {
    timeout -k 2 5 warp-cli --accept-tos --no-ansi "$@"
}

# A successful status call means the daemon is ready, not yet connected.
wait_for_warp() {
    condition=$1
    attempts=$2
    while [ "$attempts" -gt 0 ]; do
        for pid in $children; do
            kill -0 "$pid" 2>/dev/null || fail 'A service exited during WARP initialization.'
        done
        if status=$(cli status 2>/dev/null); then
            if [ "$condition" = ready ] ||
                printf '%s\n' "$status" | grep -q '^Status update: Connected$'; then
                return
            fi
        fi
        sleep 2
        attempts=$((attempts - 1))
    done
    fail "Timed out waiting for WARP to be $condition. Check logs and outbound connectivity."
}

if [ ! -f /var/lib/cloudflare-warp/reg.json ]; then
    printf '[warp] Registering a WARP client.\n'
    mkdir -p /run/dbus
    setsid /usr/bin/dbus-daemon --system --nofork --nopidfile &
    children="$!"
    setsid /usr/bin/warp-svc &
    children="$children $!"
    wait_for_warp ready 30
    timeout -k 5 60 warp-cli --accept-tos --no-ansi registration new
    [ -s /var/lib/cloudflare-warp/reg.json ] || fail 'Registration did not create reg.json.'
    stop_services
else
    [ -s /var/lib/cloudflare-warp/reg.json ] || fail 'Saved reg.json is empty.'
    printf '[warp] Using the saved registration.\n'
fi

# The upstream entrypoint reuses the existing registration and starts WARP.
setsid /entrypoint &
children="$!"
wait_for_warp connected 60

setsid /usr/local/bin/3proxy /etc/3proxy/3proxy.cfg &
children="$children $!"
printf '[warp] WARP connected; starting HTTP :3128 and SOCKS5 :1080 proxies.\n'

# Monitor the foreground services, not transient timeout helpers adopted by PID 1.
while :; do
    for pid in $children; do
        if ! kill -0 "$pid" 2>/dev/null; then
            result=0
            wait "$pid" || result=$?
            printf '[warp] A service exited with status %s; stopping the container.\n' "$result" >&2
            [ "$result" -ne 0 ] || result=1
            exit "$result"
        fi
    done
    sleep 2
done
