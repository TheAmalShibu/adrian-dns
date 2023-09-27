#!/bin/bash

# Define the path to your BIND zone file
zone_file="/etc/bind/zones/syst3mburn3r.tech.zone"

# Check if the file exists at the specified path
if [ -f "$zone_file" ]; then
  echo "Zone file found at $zone_file"
  
  # Use sed to remove A records from the zone file except for ns1, ns2, and www
  sed -i '/^[[:alnum:]]+[[:space:]]+[Aa][[:space:]]+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/!d; /^(ns1|ns2|www)\s+A\s+/!d' "$zone_file"
  
  echo "A records removed from the zone file, except for ns1, ns2, and www."
else
  echo "Zone file not found at $zone_file"
fi

