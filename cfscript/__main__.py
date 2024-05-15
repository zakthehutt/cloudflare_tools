import subprocess
import inquirer
import requests

def validate_key(headers):
    url = "https://api.cloudflare.com/client/v4/user"
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def main():
    while True:
        api_key = input('Enter cloudflare api key: ')
        email = input('Enter associated email: ')

        headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json'
        }
  
        if not validate_key(headers=headers):
            print('Failed to connect to cloudflare using provided api key and email.')
        else:
            print('Connection Successful')
            mode_questions = [
                inquirer.List('choice',
                    message="What do you need to modify?",
                    choices=['Zones', 'DNS Records', 'Exit'],
                    ),
            ]
            mode = inquirer.prompt(mode_questions)

            if mode['choice'] == 'Zones':
                subprocess.run(['python', '-m', 'cfscript.zones', email, api_key], check=True)
            elif mode['choice'] == 'DNS Records':
                subprocess.run(['python', '-m', 'cfscript.records', email, api_key], check=True)
            elif mode['choice'] == 'Exit':
                break
    

if __name__ == '__main__':
    main()