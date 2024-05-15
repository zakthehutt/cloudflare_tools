import sys
from cfscript.get_zones import get_all_zones

def main():
    if len(sys.argv) > 1:
        email = sys.argv[1]
        api_key = sys.argv[2]

    headers = {
    'X-Auth-Email': email,
    'X-Auth-Key': api_key,
    'Content-Type': 'application/json'
    }

    zones = get_all_zones(headers=headers)
    

if __name__ == "__main__":
    main()