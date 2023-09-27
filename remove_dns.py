import time
import re

# Define the path to your BIND zone file
zone_file_path = "/etc/bind/zones/syst3mburn3r.tech.zone"

# Function to parse the zone file and return A records created exactly 3 minutes ago
def get_old_a_records(zone_file):
    current_time = time.time()
    old_a_records = []
    
    with open(zone_file, 'r') as f:
        zone_contents = f.read()
    
    # Use regular expressions to find A records with timestamps
    a_record_pattern = r'([^\s]+)\s+A\s+(\d+\.\d+\.\d+\.\d+)\s*;?(\d+)?'
    matches = re.findall(a_record_pattern, zone_contents)
    
    for match in matches:
        subdomain, ip, timestamp = match
        if timestamp:
            timestamp = int(timestamp)
            if current_time - timestamp >= 180:
                old_a_records.append((subdomain, ip))
    
    return old_a_records

# Function to remove A records for subdomains created exactly 3 minutes ago
def remove_old_a_records(zone_file, subdomains):
    with open(zone_file, 'r') as f:
        zone_contents = f.read()
    
    # Remove old A records from the zone_contents
    for subdomain, ip in subdomains:
        a_record_pattern = rf'{subdomain}\s+A\s+{ip}\s*;\s*\d+'
        zone_contents = re.sub(a_record_pattern, '', zone_contents)
    
    # Write the updated zone_contents back to the zone file
    with open(zone_file, 'w') as f:
        f.write(zone_contents)

# Get old A records (created exactly 3 minutes ago)
old_a_records = get_old_a_records(zone_file_path)

# Remove old A records
remove_old_a_records(zone_file_path, old_a_records)

