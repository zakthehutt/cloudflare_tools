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
DMARC_POLICY = 'v=DMARC1;p=reject;sp=reject;'

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


# create dmarc record
def create_dmarc_record(zone_id, zone_name, dmarc_policy):
    url = f'{BASE_URL}/{zone_id}/dns_records'
    data = {
        'type': 'TXT',
        'name': '_dmarc.'+ zone_name,
        'content': dmarc_policy,
        'ttl': 1
    }
    response = rate_limited_request(url, 'post', headers=HEADERS, json=data)
    return response.json()


def main():
    pages = get_total_zone_pages()
    all_zones = get_all_zones(pages)
    print(f'Found {len(all_zones)} zones.')

    for zone in all_zones:
        zone_id = zone['id']
        zone_name = zone['name']
        has_dmarc = False
        print(f'\nProcessing: {zone_name}')

        records = get_dns_records(zone_id)
        for record in records:
            dmarc_name = f'_dmarc.{zone_name}'
            if (record['type'] == 'TXT' and record['name'] == dmarc_name) or (record['type'] == 'TXT' and record['name'] == '_dmarc'):
                has_dmarc = True
        if not has_dmarc:
            print(f'{zone_name} has no DMARC record, now creating...')
            response = create_dmarc_record(zone_id, zone_name, DMARC_POLICY)
            if response['success']:
                print(f"Successfully added DMARC record")
        else:
            print(f'{zone_name} has a DMARC record, skipping')

    
if __name__ == '__main__':
    main()
