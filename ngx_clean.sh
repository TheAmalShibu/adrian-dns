#!/bin/bash

# Define the directory path
nginx_sites_enabled="/etc/nginx/sites-enabled/"

# Loop through files in the directory
for file in "$nginx_sites_enabled"*
do
  # Check if the file is not the default or syst3mburn3r.tech.conf
  if [ "$(basename "$file")" != "default" ] && [ "$(basename "$file")" != "syst3mburn3r.tech.conf" ]; then
    # Check if the file is older than 5 minutes
    if [ "$(find "$file" -type f -mmin +5 2>/dev/null)" ]; then
      echo "Removing old file: $file"
      rm -f "$file"
    fi
  fi
done

