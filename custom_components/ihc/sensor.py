"""Support for IHC sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.unit_system import TEMPERATURE_UNITS

from .const import DOMAIN, IHC_CONTROLLER
from .ihcdevice import IHCDevice


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Load IHC switches based on a config entry."""
    controller_id = entry.unique_id
    data = hass.data[DOMAIN][controller_id]
    ihc_controller = data[IHC_CONTROLLER]
    sensors = []
    if "sensor" in data and data["sensor"]:
        for name, device in data["sensor"].items():
            ihc_id = device["ihc_id"]
            product_cfg = device["product_cfg"]
            product = device["product"]
            unit = product_cfg[CONF_UNIT_OF_MEASUREMENT]
            sensor = IHCSensor(
                ihc_controller,
                controller_id,
                name,
                ihc_id,
                unit,
                product,
            )
            sensors.append(sensor)
        async_add_entities(sensors)


class IHCSensor(IHCDevice, SensorEntity):
    """Implementation of the IHC sensor."""

    def __init__(
        self,
        ihc_controller,
        controller_id,
        name,
        ihc_id: int,
        unit,
        product=None,
    ) -> None:
        """Initialize the IHC sensor."""
        super().__init__(ihc_controller, controller_id, name, ihc_id, product)
        self._state = None
        self._unit_of_measurement = unit

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return (
            SensorDeviceClass.TEMPERATURE
            if self._unit_of_measurement in TEMPERATURE_UNITS
            else None
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def on_ihc_change(self, ihc_id, value):
        """Handle IHC resource change."""
        self._state = value
        self.schedule_update_ha_state()
