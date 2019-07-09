# Wunderlist
This is a HomeAssistant sensor for showing list tasks from Wunderlist. The sensor is checked once per minute.

## Installation

### Manual
1. In your homeassistant config directory, create a new directory. The path should look like this: **my-ha-config-dir/custom_components/wunderlist**
2. Download the contents of the following files (from src) to the new directory:
    * sensor.py
    * \_\_init\_\_.py
    * manifest.json

### Custom updater
If you are using [custom_updater](https://github.com/custom-components/custom_updater) you can use the following config to add wunderlist:

```
custom_updater:
  track:
    - components
  component_urls:
    - https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/wunderlist/custom_components.json
```
(Taken from [custom_updater documentation](https://custom-components.github.io/custom_updater/components))

## Configuration
See the [official HomeAssistant Wunderlist page](https://www.home-assistant.io/components/wunderlist/) for how to obtain client id and access token.

Set up the sensor in `configuration.yaml`:
~~~~
# Example configuration.yaml entry
sensor:
  - platform: wunderlist
    client_id: !secret wunderlist_client_id
    access_token: !secret wunderlist_access_token
    list_name: inbox
~~~~

Restart homeassistant