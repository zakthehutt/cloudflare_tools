import sys
import inquirer
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

    choices = [
        'Add Record to All Zones',
        'Delete Record from All Zones',
        'Update Record in All Zones',
        'Search and Replace', 
        'Back'    
    ]

    action_questions = [
        inquirer.List('choice',
            message="What action do you need to perform?",
            choices=choices
            ),
    ]
    action = inquirer.prompt(action_questions)
    choice = action['choice']

    # back
    if choice == choices[4]: 
        return
    # search and replace
    elif choice == choices[3]:
        return
    
    # zones = get_all_zones(headers=headers)
    

if __name__ == "__main__":
    main()