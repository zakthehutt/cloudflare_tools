import requests
import json
import time

# Setup
API_KEY = "YOUR_API_KEY"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"
EMAIL = "YOUR_EMAIL_ADDRESS"

url_zones = "https://api.cloudflare.com/client/v4/zones"
url_dns_zones = "https://api.cloudflare.com/client/v4/zones/{}/dns_records"
url_ssl_type = "https://api.cloudflare.com/client/v4/zones/{}/settings/ssl"


# Define the DNS records to be added
with open("dns_records.txt", "r") as file:
    dns_records = [json.loads(line.strip()) for line in file]

# Open the file and read the domains
with open("domains.txt", "r") as file:
    for line in file:
        domain = line.strip()
        payload_zone = {
            "account": {"id": ACCOUNT_ID},
            "name": domain,
            "type": "full",
        }
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": EMAIL,
            "X-Auth-Key": API_KEY
        }
        response_zone = requests.request("POST", url_zones, json=payload_zone, headers=headers)

        # Proceed if the response is successful
        if response_zone.status_code == 200:
            zone_id = response_zone.json()['result']['id']
            print(f"Successfully created zone for domain: {domain}")
        else:
            print("Failed to create zone for domain:", domain)
            continue

        time.sleep(0.6)  # Pause for 0.6 seconds to limit to 100 requests per 60 seconds

        # Set SSL to strict as this cannot be done during zone creation
        payload_ssl = {
            "value": "strict"
        }
        response_ssl = requests.request("PATCH", url_ssl_type.format(zone_id), json=payload_ssl, headers=headers)

        if response_ssl.status_code == 200:
            print(f"Successfully set SSL to strict for domain: {domain}")
        else:
            print("Failed to set SSL to strict for domain:", domain)
            print("Response content:", response_ssl.text)
        
        time.sleep(0.6) # Pause again to limit the rate

        # Add DNS records to the newly created zone
        for record in dns_records:
            record_copy = record.copy()
            record_copy['name'] = record_copy['name'].replace('@', domain)
            response_record = requests.request("POST", url_dns_zones.format(zone_id), json=record_copy, headers=headers)
            
            if response_record.status_code == 200:
                print(f"Successfully created {record['type']} record for domain: {domain}")
            else:
                print(f"Failed to create {record['type']} record for domain: {domain}")
                print("Response content:", response_record.text)  # Log the response content

            time.sleep(0.6)  # Pause again to limit the rate