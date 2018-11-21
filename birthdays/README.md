# Swedish calendar
This is a HomeAssistant component for tracking birthdays, where the state of each birthday is equal to how many days are left. All birthdays are updated at midnight.

## How to setup

1. In your homeassistant config directory, create a new python file. The path should look like this: **my-ha-config-dir/custom_components/birthdays.py**
2. Copy the contents of birthdays.py in this git-repo to your newly created file in HA
3. Set up the component:
~~~~
# Example configuration.yaml entry
birthdays:
  - name: 'Frodo Baggins'
    date_of_birth: 1921-09-22
  - name: 'Bilbo Baggins'
    date_of_birth: 1843-09-22
  - name: Elvis
    date_of_birth: 1935-01-08
~~~~
4. Restart homeassistant
