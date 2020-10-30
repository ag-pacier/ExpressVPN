#!/bin/bash
#Health check for the VPN
result=$(expressvpn status)
if [[ "$result"==*"Connected to"* ]] ; then exit 0 ; else exit 1 ; fi