# Swedish calendar
This is a HomeAssistant component for showing data about swedish holidays. It uses the api at *api.dryg.net* to generate statistics as sensors. The sensors are checked once per day.

## How to setup

1. In your homeassistant config directory, create a sensor file. The path should look like this: **my-ha-config-dir/custom_components/sensor/swedish_calendar.py**
2. Copy the contents of swedish_calendar.py in this git-repo to your newly created file in HA
3. Set up the sensor:
~~~~
# Example configuration.yaml entry
sensor:
  - platform: swedish_calendar
~~~~
4. Restart homeassistant

### Configuration options
The following sensor types are supported:
~~~~
date
weekday
workfree_day
red_day
week
day_of_week
eve
holiday
day_before_workfree_holiday
name_day
flag_day
~~~~

All sensors are added per default. If a certain sensor isn't available, it will be hidden (for example: type of holiday will be hidden if there is no ongoing holiday). If you do not want a sensor at all, you can manually exclude it:
~~~~
# Example configuration.yaml entry with exclusion
sensor:
  - platform: swedish_calendar
    exclude:
      - date
      - day_before_workfree_holiday
~~~~