#!/bin/sh
set -eu

pidof 3proxy >/dev/null
timeout -k 2 5 warp-cli --accept-tos --no-ansi status |
    grep -q '^Status update: Connected$'
