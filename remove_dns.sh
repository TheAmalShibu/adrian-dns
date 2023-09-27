#!/bin/bash

# Define the path to your BIND zone file
zone_file="/etc/bind/zones/syst3mburn3r.tech.zone"

# Calculate the current timestamp
current_time=$(date +%s)

# Temporary file for storing updated zone content
temp_file="/tmp/zone_temp_file"

# Function to remove A records for subdomains created exactly 3 minutes ago or earlier
remove_old_a_records() {
  while read -r line; do
    if [[ "$line" == *' A '* ]]; then
      subdomain=$(echo "$line" | awk '{print $1}')
      ip=$(echo "$line" | awk '{print $4}')
      timestamp=$(echo "$line" | awk -F ';' '{print $2}')
      timestamp=${timestamp// /}
      if [ -n "$timestamp" ]; then
        if (( current_time - timestamp >= 180 )); then
          # Remove old A records
          sed -i "/$subdomain\s\+A\s\+$ip\s\+;/d" "$temp_file"
        fi
      fi
    fi
  done < "$zone_file"
}

# Copy the zone file to the temporary file
cp "$zone_file" "$temp_file"

# Remove old A records from the temporary file
remove_old_a_records

# Overwrite the original zone file with the updated content
mv "$temp_file" "$zone_file"

# Restart BIND or reload the configuration if necessary
# Replace 'service bind9 restart' with the appropriate command for your system
service bind9 restart

