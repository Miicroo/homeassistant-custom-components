import asyncio

from datetime import datetime
from datetime import timedelta
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_MONITORED_CONDITIONS, ATTR_ATTRIBUTION)
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['stravalib==0.9.4']

_LOGGER = logging.getLogger(__name__)

ATTR_BIGGEST_RIDE_DISTANCE = 'biggest_ride_distance'
ATTR_BIGGEST_CLIMB_ELEVATION_GAIN = 'biggest_climb_elevation_gain'

ATTR_RECENT_RIDE_TOTALS = 'recent_ride_totals'
ATTR_RECENT_RUN_TOTALS = 'recent_run_totals'
ATTR_RECENT_SWIM_TOTALS = 'recent_swim_totals'
ATTR_YTD_RIDE_TOTALS = 'ytd_ride_totals'
ATTR_YTD_RUN_TOTALS = 'ytd_run_totals'
ATTR_YTD_SWIM_TOTALS = 'ytd_swim_totals'
ATTR_ALL_RIDE_TOTALS = 'all_ride_totals'
ATTR_ALL_RUN_TOTALS = 'all_run_totals'
ATTR_ALL_SWIM_TOTALS = 'all_swim_totals'

CONF_ATTRIBUTION = 'Data provided by Strava'
CONF_ACCESS_TOKEN = 'accesstoken'

SENSOR_TYPES = {
    ATTR_BIGGEST_RIDE_DISTANCE: ['Biggest ride distance', 'mdi:bike', 'm', False, lambda x: x],
    ATTR_BIGGEST_CLIMB_ELEVATION_GAIN: ['Biggest climb elevation gain', None, 'm', False, lambda x: x],
    ATTR_RECENT_RIDE_TOTALS: ['Recent ride totals', 'mdi:bike', 'm', True, lambda x: x['distance']],
    ATTR_RECENT_RUN_TOTALS: ['Recent run totals', 'mdi:run', 'm', True, lambda x: x['distance']],
    ATTR_RECENT_SWIM_TOTALS: ['Recent swim totals', 'mdi:swim', 'm', True, lambda x: x['distance']],
    ATTR_YTD_RIDE_TOTALS: ['This year ride totals', 'mdi:bike', 'm', True, lambda x: x['distance']],
    ATTR_YTD_RUN_TOTALS: ['This year run totals', 'mdi:run', 'm', True, lambda x: x['distance']],
    ATTR_YTD_SWIM_TOTALS: ['This year swim totals', 'mdi:swim', 'm', True, lambda x: x['distance']],
    ATTR_ALL_RIDE_TOTALS: ['All ride totals', 'mdi:bike', 'm', True, lambda x: x['distance']],
    ATTR_ALL_RUN_TOTALS: ['All run totals', 'mdi:run', 'm', True, lambda x: x['distance']],
    ATTR_ALL_SWIM_TOTALS: ['All swim totals', 'mdi:swim', 'm', True, lambda x: x['distance']]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ACCESS_TOKEN): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[ATTR_BIGGEST_RIDE_DISTANCE]):
        vol.All(cv.ensure_list, vol.Length(min=1), [vol.In(SENSOR_TYPES)])
})


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the Strava sensor."""
    devices = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        devices.append(StravaSensor(hass, sensor_type))
    async_add_devices(devices)

    accesstoken = config.get(CONF_ACCESS_TOKEN)
    strava_data = StravaData(hass, accesstoken, devices)

    yield from strava_data.fetch_data()

class StravaSensor(Entity):
    """Representation of a Strava sensor."""

    def __init__(self, hass, sensor_type):
        """Initialize the sensor."""
        self._name = SENSOR_TYPES[sensor_type][0]
        self._icon = SENSOR_TYPES[sensor_type][1]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][2]
        self._include_state_in_attributes = SENSOR_TYPES[sensor_type][3]
        self._state_transformer = SENSOR_TYPES[sensor_type][4]
        self._state = None
        self.type = sensor_type
        self.hass = hass
        self.entity_id = 'sensor.strava_{}'.format(sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        if not self._state:
            return None
            
        return self._state_transformer(self._state)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return other details about the sensor state."""
        attr = {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
        }
        
        if self._state and self._include_state_in_attributes:
            attr.update(self._state)

        return attr

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def set_state(self, new_state):
        self._state = new_state
    
class StravaData:
    """Implementation of the Strava data retriever."""

    def __init__(self, hass, accesstoken, devices):
        """Initialize the sensor."""
        self.hass = hass
        
        from stravalib import Client
        self._strava_client = Client(access_token=accesstoken)
        self._athlete = self._strava_client.get_athlete()

        self._devices = devices
        self._athlete_stats = None

    @asyncio.coroutine
    def fetch_data(self, *_):
        """Get the departure board."""
        athlete_stats = self._strava_client.get_athlete_stats(athlete_id=self._athlete.id)
        self._athlete_stats = athlete_stats.to_dict()

        yield from self.update_devices()
        async_call_later(self.hass, 2*60, self.fetch_data)

    @asyncio.coroutine
    def update_devices(self, *_):
        if not self._athlete_stats:
            return
        
        tasks = []
        for sensor_type in self._athlete_stats:
            for device in self._devices:
                if device.type == sensor_type:
                    device.set_state(self._athlete_stats[sensor_type])
                    tasks.append(device.async_update_ha_state())

        if tasks:
            yield from asyncio.wait(tasks, loop=self.hass.loop)
