import requests
import time

BASE_URL = 'https://api.cloudflare.com/client/v4/zones'

REQUESTS_PER_MINUTE = 80
INTERVAL = 60/REQUESTS_PER_MINUTE

# limit request rate, to ensure we don't go over the limit
def rate_limited_request(url, method, **kwargs): 
    time.sleep(INTERVAL)
    response = getattr(requests, method)(url, **kwargs)
    return response

# find the number of zone pages on the server
def get_total_zone_pages(headers, per_page=50):
    params = {
        'per_page': per_page,
        'page': 1
    }
    response = rate_limited_request(
        BASE_URL, 
        'get', 
        headers=headers, 
        params=params
    )
    response_data = response.json()
    if not response_data['success']:
        raise Exception('Failed to fetch zone information (number of pages)')
    
    pages = response_data['result_info']['total_pages']
    return pages


# get all zones from cloudflare account
def get_all_zones(headers, per_page=50):
    pages = get_total_zone_pages(headers=headers)
    zones = []
    for page in range(1,pages+1):
        url = f'{BASE_URL}?page={page}&per_page={per_page}'
        print(f'Retreiving zones from {url}...')

        response = rate_limited_request(
            url, 
            'get',
            headers=headers
        )
        if response.status_code != 200:
            raise Exception(f'Error fetching zones: {response.text}')
        
        response_data = response.json()
        if not response_data['success']:
            raise Exception(f'Failed to fetch zone information from page {page}')
        
        zones.extend(response_data['result'])
    return zones