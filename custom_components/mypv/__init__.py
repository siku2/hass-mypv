"""Integration ELWA myPV."""

from httpcore import TimeoutException

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceEntry

from .communicate import MypvCommunicator
from .const import COMM_HUB, DEV_IP, DOMAIN

# List of platforms to support. There should be a matching .py file for each
PLATFORMS: list[str] = [
    "binary_sensor",
    "button",
    "number",
    "sensor",
    "switch",
]


async def async_setup(hass: HomeAssistant, config):
    """Platform setup, do nothing."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config[DOMAIN])
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Load the saved entities."""

    try:
        comm = MypvCommunicator(hass, entry)
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = comm
        await comm.initialize()

        await comm.async_refresh()

        if not comm.last_update_success:
            raise ConfigEntryNotReady(
                f"Update of myPV device at {entry.data[DEV_IP]} failed"
            )

        hass.data[DOMAIN][entry.entry_id] = {
            COMM_HUB: comm,
        }

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except (TimeoutError, TimeoutException) as ex:
        raise ConfigEntryNotReady(
            f"Timeout while connecting to myPV device at {entry.data[DEV_IP]}"
        ) from ex
    except Exception as ex:
        raise ConfigEntryNotReady(
            f"Error while setting up myPV device at {entry.data[DEV_IP]}"
        ) from ex
    else:
        return True


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
