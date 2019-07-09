"""Support to interact with Wunderlist."""
import asyncio
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_ACCESS_TOKEN)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_call_later
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)

CONF_CLIENT_ID = 'client_id'
CONF_LIST_NAME = 'list_name'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CLIENT_ID): cv.string,
    vol.Required(CONF_ACCESS_TOKEN): cv.string,
    vol.Required(CONF_LIST_NAME): cv.string,
})

VERSION = '0.0.1'

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    client_id = config[CONF_CLIENT_ID]
    access_token = config[CONF_ACCESS_TOKEN]
    list_name = config[CONF_LIST_NAME]
    entity = WunderlistSensor(hass, access_token, client_id, list_name)

    if not entity.check_credentials():
        _LOGGER.error("Invalid credentials")
        return

    if not entity.check_list_exists():
        _LOGGER.error("Invalid list name: " + list_name)
        return

    async_add_entities([entity])
    await entity.update()

class WunderlistSensor(Entity):

    def __init__(self, hass, access_token, client_id, list_name):
        import wunderpy2

        api = wunderpy2.WunderApi()
        self._client = api.get_client(access_token, client_id)
        self.hass = hass
        self._list_name = list_name
        self._list_id = self._list_by_name(list_name)
        self._state = None
        self.entity_id = 'sensor.wunderlist_{}'.format(slugify(list_name))

    def check_credentials(self):
        """Check if the provided credentials are valid."""
        try:
            self._client.get_lists()
            return True
        except ValueError:
            return False

    def check_list_exists(self):
        return self._list_by_name(self._list_name) is not None

    @property
    def name(self):
        return self._list_name

    @property
    def state(self):
        return self._state

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return 'mdi:wunderlist'

    @property
    def hidden(self):
        """Return hidden if it should not be visible in GUI"""
        return self._state is None or self._state == ""

    def _list_by_name(self, name):
        """Return a list ID by name."""
        lists = self._client.get_lists()
        tmp = [l for l in lists if l["title"] == name]
        if tmp:
            return tmp[0]["id"]
        return None

    async def update(self, *_):
        tasks = self._client.get_tasks(self._list_id)
        self._state = list(map(lambda task: task['title'], tasks))
        await asyncio.wait([self.async_update_ha_state()], loop=self.hass.loop)

        async_call_later(self.hass, 60, self.update)