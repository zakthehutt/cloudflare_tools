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

# the old content to replace and the new content to use
old_cname_content = 'server.osamweb.com'
new_cname_content = '@'

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


# get all zones from cloudflare account
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

# update cname record to new content
def update_cname_record(zone_id, record_id, name, new_content):
    url = f'{BASE_URL}/{zone_id}/dns_records/{record_id}'
    data = {
        'type': 'CNAME',
        'name': name,
        'content': new_content
    }
    response = rate_limited_request(url, 'put', json=data)
    if response.status_code != 200:
        raise Exception(f'Error updating DNS record {record_id} in zone {zone_id}: {response.text}')
    print(f'Successfully updated CNAME record {name} to point to {new_content}')

def main():
    pages = get_total_zone_pages()
    zones = get_all_zones(pages)
    print(f'Found {len(zones)} zones.')

    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']
        print(f'Processing zone: {zone_name} ({zone_id})')
        records = get_dns_records(zone_id)
        # for each record
        for record in records:
            # if content of the CNAME needs to be replaced, update
            if record['type'] == 'CNAME' and record['content'] == old_cname_content:
                print(f'Updating CNAME record {record['name']} in zone {zone_name}')
                update_cname_record(zone_id, record['id'], record['name'], new_cname_content)
            # else, skip the record
            else:
                print(f'Skipping record {record['name']} due to different content')

if __name__ == '__main__':
    main()
