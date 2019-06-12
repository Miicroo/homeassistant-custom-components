import asyncio

from datetime import datetime
from datetime import timedelta
from aiohttp import web
import logging
import json
import os

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_RESOURCES, CONF_TYPE, ATTR_ATTRIBUTION
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import Throttle

REQUIREMENTS = ['stravalib==0.10.2']

_LOGGER = logging.getLogger(__name__)

CONF_ACCESS_TOKEN = 'accesstoken'
CONF_ARG = 'arg'
CONF_ATTRIBUTION = 'Data provided by Strava'

# Sensor names
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

# ActivityTotals attribute names
ATTR_TOTAL_ACHIEVEMENT_COUNT = 'achievement_count'
ATTR_TOTAL_COUNT = 'count'
ATTR_TOTAL_DISTANCE = 'distance'
ATTR_TOTAL_ELAPSED_TIME = 'elapsed_time'
ATTR_TOTAL_ELEVATION_GAIN = 'elevation_gain'
ATTR_TOTAL_MOVING_TIME = 'moving_time'

# Sensor types with 4 arguments contain pure data (like ints etc), sensors with 2 arguments are totals. The key of the total is chosen in the arg and taken from TOTALS_TYPES.
SENSOR_TYPES = {
    ATTR_BIGGEST_RIDE_DISTANCE: ['Biggest ride distance', 'mdi:bike', lambda hass: 'm', lambda value, hass: value],
    ATTR_BIGGEST_CLIMB_ELEVATION_GAIN: ['Biggest climb elevation gain', None, lambda hass: 'm', lambda value, hass: value],
    ATTR_RECENT_RIDE_TOTALS: ['Recent ride totals', 'mdi:bike'],
    ATTR_RECENT_RUN_TOTALS: ['Recent run totals', 'mdi:run'],
    ATTR_RECENT_SWIM_TOTALS: ['Recent swim totals', 'mdi:swim'],
    ATTR_YTD_RIDE_TOTALS: ['This year ride totals', 'mdi:bike'],
    ATTR_YTD_RUN_TOTALS: ['This year run totals', 'mdi:run'],
    ATTR_YTD_SWIM_TOTALS: ['This year swim totals', 'mdi:swim'],
    ATTR_ALL_RIDE_TOTALS: ['All ride totals', 'mdi:bike'],
    ATTR_ALL_RUN_TOTALS: ['All run totals', 'mdi:run'],
    ATTR_ALL_SWIM_TOTALS: ['All swim totals', 'mdi:swim']
}

# Possible types for the ActivityTotals
TOTALS_TYPES = {
    ATTR_TOTAL_ACHIEVEMENT_COUNT: [lambda hass: '', lambda value, hass: value[ATTR_TOTAL_ACHIEVEMENT_COUNT]],
    ATTR_TOTAL_COUNT: [lambda hass: '', lambda value, hass: value[ATTR_TOTAL_COUNT]],
    ATTR_TOTAL_DISTANCE: [lambda hass: 'km' if hass.config.units.is_metric else 'mi', lambda value, hass: int(value[ATTR_TOTAL_DISTANCE]/1000) if hass.config.units.is_metric else int(value[ATTR_TOTAL_DISTANCE]*0.000621371192)],
    ATTR_TOTAL_ELAPSED_TIME: [lambda hass: '', lambda value, hass: value[ATTR_TOTAL_ELAPSED_TIME]],
    ATTR_TOTAL_ELEVATION_GAIN: [lambda hass: 'm' if hass.config.units.is_metric else 'ft', lambda value, hass: int(value[ATTR_TOTAL_ELEVATION_GAIN]) if hass.config.units.is_metric else int(value[ATTR_TOTAL_ELEVATION_GAIN]/0.9144)],
    ATTR_TOTAL_MOVING_TIME: [lambda hass: '', lambda value, hass: value[ATTR_TOTAL_MOVING_TIME]]
}

CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_SECRET = 'client_secret'

STRAVA_CONFIG_PATH = 'strava.json'

DATA_CALLBACK = 'strava-callback'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CLIENT_ID): cv.string,
    vol.Required(CONF_CLIENT_SECRET): cv.string,
    vol.Optional(CONF_RESOURCES, default={CONF_TYPE: ATTR_BIGGEST_RIDE_DISTANCE, CONF_ARG: ATTR_TOTAL_DISTANCE}):
        vol.All(cv.ensure_list, [vol.Schema({
            vol.Required(CONF_TYPE): vol.In(SENSOR_TYPES),
            vol.Optional(CONF_ARG): vol.In(TOTALS_TYPES),
        })])
})

VERSION = '0.0.1'

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the Strava sensors."""
    from stravalib import Client
    client = Client()

    @asyncio.coroutine
    def _read_config():
        if not os.path.isfile(config_path):
            return None
        with open(config_path, 'r') as auth_file:
            config = json.load(auth_file)
            if config['client_id'] == client_id:
                return config['access_token']

    @asyncio.coroutine
    def _write_config(access_token):
        with open(config_path, 'w') as auth_file:
            json.dump({
                'client_id': client_id,
                'access_token': access_token,
            }, auth_file)

    @asyncio.coroutine
    def _add_devices(access_token):
        devices = []
        for resource in config.get(CONF_RESOURCES):
            sensor_type = resource[CONF_TYPE]
            is_simple_sensor = len(SENSOR_TYPES[sensor_type]) == 4
            if CONF_ARG not in resource:
                resource[CONF_ARG] = ATTR_TOTAL_DISTANCE

            name = SENSOR_TYPES[sensor_type][0]
            icon = SENSOR_TYPES[sensor_type][1]
            if is_simple_sensor:
                unit_of_measurement_lambda = SENSOR_TYPES[sensor_type][2]
                state_transformer_lambda = SENSOR_TYPES[sensor_type][3]
            else:
                total_type = resource[CONF_ARG]
                unit_of_measurement_lambda = TOTALS_TYPES[total_type][0]
                state_transformer_lambda = TOTALS_TYPES[total_type][1]

            devices.append(StravaSensor(hass=hass, sensor_type=sensor_type, name=name, icon=icon, unit_of_measurement_lambda=unit_of_measurement_lambda, state_transformer_lambda=state_transformer_lambda))

        strava_data = StravaData(hass, access_token, devices)
        yield from strava_data.fetch_data()
        return async_add_devices(devices)

    @asyncio.coroutine
    def initialize_callback(code):
        """Handle OAuth callback from Strava authorization flow."""
        access_token = client.exchange_code_for_token(
            client_id=client_id, client_secret=client_secret, code=code)
        yield from _write_config(access_token)
        yield from _add_devices(access_token)
        configurator.async_request_done(request_id)

    hass.http.register_view(StravaAuthCallbackView())

    client_id = config.get(CONF_CLIENT_ID)
    client_secret = config.get(CONF_CLIENT_SECRET)

    config_path = hass.config.path(STRAVA_CONFIG_PATH)

    access_token = yield from _read_config()
    if access_token is not None:
        yield from _add_devices(access_token)
    else:
        callback_url = '{}{}'.format(
            hass.config.api.base_url, StravaAuthCallbackView.url)
        authorize_url = client.authorization_url(
            client_id=client_id, redirect_uri=callback_url)

        configurator = hass.components.configurator
        request_id = configurator.async_request_config(
            'Strava',
            description='Authorization required for Strava account.',
            link_name='Authorize Home Assistant',
            link_url=authorize_url,
            entity_picture='/local/icons/logo_strava.png')

    hass.data[DATA_CALLBACK] = initialize_callback
    return True

class StravaAuthCallbackView(HomeAssistantView):
    """Web view that handles OAuth authentication and redirection flow."""
    requires_auth = False
    url = '/api/strava/callback'
    name = 'api:strava:callback'

    @callback
    def get(self, request):  # pylint: disable=no-self-use
        """Handle browser HTTP request."""
        hass = request.app['hass']
        params = request.query
        response = web.HTTPFound('/states')

        if 'code' not in params:
            _LOGGER.error(
                'Error authorizing Strava: %s',
                params.get('error', 'invalid response'))
        elif DATA_CALLBACK not in hass.data:
            _LOGGER.error('Configuration request not found')
        else:
            code = params['code']
            initialize_callback = hass.data[DATA_CALLBACK]
            hass.async_add_job(initialize_callback(code))

        return response

class StravaSensor(Entity):
    """Representation of a Strava sensor."""

    def __init__(self, hass, sensor_type, name, icon, unit_of_measurement_lambda, state_transformer_lambda):
        """Initialize the sensor."""
        self.hass = hass
        self.type = sensor_type
        self._name = name
        self._icon = icon
        self._unit_of_measurement = unit_of_measurement_lambda
        self._state_transformer = state_transformer_lambda
        self._state = None
        self.entity_id = 'sensor.strava_{}'.format(sensor_type)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        if not self._state:
            return None

        return self._state_transformer(self._state, self.hass)

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return self._icon

    @property
    def device_state_attributes(self):
        attr = {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
        }

        if self._state and isinstance(self._state, dict):
            attr.update(self._state)

        return attr

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement(self.hass)

    def set_state(self, new_state):
        self._state = new_state

class StravaData:
    """Implementation of the Strava data retriever."""

    def __init__(self, hass, accesstoken, devices):
        self.hass = hass

        from stravalib import Client
        from stravalib.util import limiter
        self._strava_client = Client(access_token=accesstoken, rate_limiter=limiter.DefaultRateLimiter())
        self._athlete = self._strava_client.get_athlete()
        self._accesstoken = accesstoken

        self._devices = devices
        self._athlete_stats = None

    @asyncio.coroutine
    def fetch_data(self, *_):
        """Get the athlete stats."""
        stats_fetched_ok = False
        from requests.exceptions import ConnectionError
        try:
            athlete_stats = self._strava_client.get_athlete_stats(athlete_id=self._athlete.id)
            stats_fetched_ok = True
        except:
           _LOGGER.warn("Failed to get athlete stats, re-initiating client")

           from stravalib import Client
           from stravalib.util import limiter
           self._strava_client = Client(access_token=self._accesstoken, rate_limiter=limiter.DefaultRateLimiter())

        if stats_fetched_ok:
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
