import requests
import time

# config
API_KEY = 'YOUR_API_KEY'
EMAIL = 'YOUR_EMAIL'
HEADERS = {
    'X-Auth-Email': EMAIL,
    'X-Auth-Key': API_KEY,
    'Content-Type': 'application/json'
}
BASE_URL = 'https://api.cloudflare.com/client/v4/zones'
MX_RECORD = 'YOUR_MX_RECORD'
SPF_POLICY = "YOUR_SPF_POLICY"

requests_per_minute = 80
interval = 60/requests_per_minute

# limit request rate, to ensure we don't go over the limit
def rate_limited_request(url, method, **kwargs): 
    time.sleep(interval)
    response = getattr(requests, method)(url, **kwargs)
    return response

# find the number of zone pages on the server
def get_total_zone_pages(per_page=50):
    params = {
        'per_page': per_page,
        'page': 1
    }
    response = rate_limited_request(
        BASE_URL, 
        'get', 
        headers=HEADERS, 
        params=params
    )
    response_data = response.json()
    if not response_data['success']:
        raise Exception('Failed to fetch zone information (number of pages)')
    
    pages = response_data['result_info']['total_pages']
    return pages


# get all zones from cloudflare
def get_all_zones(pages, per_page=50):
    zones = []
    for page in range(1,pages+1):
        url = f'{BASE_URL}?page={page}&per_page={per_page}'
        print(f'Retreiving zones from {url}...')

        response = rate_limited_request(
            url, 
            'get',
            headers=HEADERS,
        )
        if response.status_code != 200:
            raise Exception(f'Error fetching zones: {response.text}')
        
        response_data = response.json()
        if not response_data['success']:
            raise Exception(f'Failed to fetch zone information from page {page}')
        
        zones.extend(response_data['result'])
    return zones


# get all dns records from zone
def get_dns_records(zone_id):
    url = f'{BASE_URL}/{zone_id}/dns_records'
    records = []

    print(f'Fetching records...')
    response = rate_limited_request(
        url, 
        'get', 
        headers=HEADERS
    )
    if response.status_code != 200:
        raise Exception(f'Error fetching DNS records for zone {zone_id}: {response.text}')
    
    response_data = response.json()
    if not response_data['success']:
        raise Exception(f'Failed to fetch DNS information from zone {zone_id}: {response.text}')
    
    records.extend(response_data['result'])
    return records

# create spf record
def create_spf_record(zone_id, zone_name, spf_policy):
    url = f'{BASE_URL}/{zone_id}/dns_records'
    data = {
        'type': 'TXT',
        'name': zone_name,
        'content': spf_policy,
        'ttl': 1
    }
    response = rate_limited_request(url, 'post', headers=HEADERS, json=data)
    return response.json()

# delete spf record
def delete_spf_record(zone_id, record_id):
    url = f'{BASE_URL}/{zone_id}/dns_records/{record_id}'
    response = rate_limited_request(url, 'delete', headers=HEADERS)
    return response.json()

# replace spf record
def replace_spf_record(zone_id, zone_name, spf_policy):
    records = get_dns_records(zone_id)
    for record in records:
        if record['type'] == 'TXT' and 'spf' in record['content']:
            print(f'Replacing SPF record for {zone_name}...')
            delete_response = delete_spf_record(zone_id, record['id'])
            if delete_response['success']:
                create_response = create_spf_record(zone_id, zone_name, spf_policy)
                if create_response['success']:
                    print(f"Successfully replaced SPF record for {zone_name}")
                else:
                    print(f"Failed to create new SPF record for {zone_name}")
            else:
                print(f"Failed to delete existing SPF record for {zone_name}")

def main():
    pages = get_total_zone_pages()
    all_zones = get_all_zones(pages)
    print(f'Found {len(all_zones)} zones.')

    for zone in all_zones:
        zone_id = zone['id']
        zone_name = zone['name']
        has_mx = False
        print(f'\nProcessing: {zone_name}')

        records = get_dns_records(zone_id)
        for record in records:
            if record['type'] == 'MX' and record['content'] == MX_RECORD:
                has_mx = True
        if has_mx:
            print(f'{zone_name} has the MX record, now replacing SPF...')
            replace_spf_record(zone_id, zone_name, SPF_POLICY)
        else:
            print(f'{zone_name} does not have the MX record, skipping')
    
if __name__ == '__main__':
    main()
