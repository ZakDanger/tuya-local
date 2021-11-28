from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_BOOST,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.components.light import COLOR_MODE_BRIGHTNESS
from homeassistant.const import STATE_UNAVAILABLE, TIME_MINUTES

from ..const import WETAIR_WCH750_HEATER_PAYLOAD
from ..helpers import assert_device_properties_set
from ..mixins.climate import TargetTemperatureTests
from ..mixins.select import BasicSelectTests
from ..mixins.sensor import BasicSensorTests
from .base_device_tests import TuyaDeviceTestCase

HVACMODE_DPS = "1"
TEMPERATURE_DPS = "2"
PRESET_DPS = "4"
HVACACTION_DPS = "11"
TIMER_DPS = "19"
COUNTDOWN_DPS = "20"
UNKNOWN21_DPS = "21"
BRIGHTNESS_DPS = "101"


class TestWetairWCH750Heater(
    BasicSelectTests,
    BasicSensorTests,
    TargetTemperatureTests,
    TuyaDeviceTestCase,
):
    __test__ = True

    def setUp(self):
        self.setUpForConfig("wetair_wch750_heater.yaml", WETAIR_WCH750_HEATER_PAYLOAD)
        self.subject = self.entities.get("climate")
        self.setUpTargetTemperature(
            TEMPERATURE_DPS,
            self.subject,
            min=10,
            max=35,
        )
        self.light = self.entities.get("light_display")
        self.setUpBasicSelect(
            TIMER_DPS,
            self.entities.get("select_timer"),
            {
                "0h": "Off",
                "1h": "1 hour",
                "2h": "2 hours",
                "3h": "3 hours",
                "4h": "4 hours",
                "5h": "5 hours",
                "6h": "6 hours",
                "7h": "7 hours",
                "8h": "8 hours",
                "9h": "9 hours",
                "10h": "10 hours",
                "11h": "11 hours",
                "12h": "12 hours",
                "13h": "13 hours",
                "14h": "14 hours",
                "15h": "15 hours",
                "16h": "16 hours",
                "17h": "17 hours",
                "18h": "18 hours",
                "19h": "19 hours",
                "20h": "20 hours",
                "21h": "21 hours",
                "22h": "22 hours",
                "23h": "23 hours",
                "24h": "24 hours",
            },
        )
        self.setUpBasicSensor(
            COUNTDOWN_DPS, self.entities.get("sensor_timer"), unit=TIME_MINUTES
        )

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE,
        )

    def test_icon(self):
        self.dps[HVACMODE_DPS] = True
        self.assertEqual(self.subject.icon, "mdi:radiator")

        self.dps[HVACMODE_DPS] = False
        self.assertEqual(self.subject.icon, "mdi:radiator-disabled")

    def test_temperatre_unit_retrns_device_temperatre_unit(self):
        self.assertEqual(
            self.subject.temperature_unit, self.subject._device.temperature_unit
        )

    def test_target_temperature_in_af_mode(self):
        self.dps[TEMPERATURE_DPS] = 25
        self.dps[PRESET_DPS] = "mod_antiforst"
        self.assertEqual(self.subject.target_temperature, None)

    async def test_legacy_set_temperature_with_preset_mode(self):
        async with assert_device_properties_set(
            self.subject._device, {PRESET_DPS: "mod_antiforst"}
        ):
            await self.subject.async_set_temperature(preset_mode=PRESET_AWAY)

    async def test_legacy_set_temperature_with_both_properties(self):
        async with assert_device_properties_set(
            self.subject._device,
            {TEMPERATURE_DPS: 25, PRESET_DPS: "mod_max12h"},
        ):
            await self.subject.async_set_temperature(
                preset_mode=PRESET_BOOST, temperature=25
            )

    async def test_set_target_temperature_fails_in_anti_frost(self):
        self.dps[PRESET_DPS] = "mod_antiforst"

        with self.assertRaisesRegex(
            AttributeError, "temperature cannot be set at this time"
        ):
            await self.subject.async_set_target_temperature(25)

    def test_current_temperature_not_supported(self):
        self.assertIsNone(self.subject.current_temperature)

    def test_hvac_mode(self):
        self.dps[HVACMODE_DPS] = True
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_HEAT)

        self.dps[HVACMODE_DPS] = False
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_OFF)

        self.dps[HVACMODE_DPS] = None
        self.assertEqual(self.subject.hvac_mode, STATE_UNAVAILABLE)

    def test_hvac_modes(self):
        self.assertCountEqual(self.subject.hvac_modes, [HVAC_MODE_OFF, HVAC_MODE_HEAT])

    async def test_turn_on(self):
        async with assert_device_properties_set(
            self.subject._device,
            {HVACMODE_DPS: True},
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_HEAT)

    async def test_trn_off(self):
        async with assert_device_properties_set(
            self.subject._device,
            {HVACMODE_DPS: False},
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_OFF)

    def test_preset_mode(self):
        self.dps[PRESET_DPS] = "mod_free"
        self.assertEqual(self.subject.preset_mode, PRESET_COMFORT)

        self.dps[PRESET_DPS] = "mod_max12h"
        self.assertEqual(self.subject.preset_mode, PRESET_BOOST)

        self.dps[PRESET_DPS] = "mod_antiforst"
        self.assertEqual(self.subject.preset_mode, PRESET_AWAY)

    def test_preset_modes(self):
        self.assertCountEqual(self.subject.preset_modes, ["comfort", "boost", "away"])

    async def test_set_preset_mode_to_comfort(self):
        async with assert_device_properties_set(
            self.subject._device,
            {PRESET_DPS: "mod_free"},
        ):
            await self.subject.async_set_preset_mode(PRESET_COMFORT)

    async def test_set_preset_mode_to_boost(self):
        async with assert_device_properties_set(
            self.subject._device,
            {PRESET_DPS: "mod_max12h"},
        ):
            await self.subject.async_set_preset_mode(PRESET_BOOST)

    async def test_set_preset_mode_to_away(self):
        async with assert_device_properties_set(
            self.subject._device,
            {PRESET_DPS: "mod_antiforst"},
        ):
            await self.subject.async_set_preset_mode(PRESET_AWAY)

    def test_device_state_attributes(self):
        self.dps[TIMER_DPS] = "1h"
        self.dps[COUNTDOWN_DPS] = 20
        self.dps[UNKNOWN21_DPS] = 21

        self.assertDictEqual(
            self.subject.device_state_attributes,
            {
                "timer": "1h",
                "countdown": 20,
                "unknown_21": 21,
            },
        )

    def test_light_supported_color_modes(self):
        self.assertCountEqual(
            self.light.supported_color_modes,
            [COLOR_MODE_BRIGHTNESS],
        )

    def test_light_color_mode(self):
        self.assertEqual(self.light.color_mode, COLOR_MODE_BRIGHTNESS)

    def test_light_icon(self):
        self.assertEqual(self.light.icon, None)

    def test_light_is_on(self):
        self.dps[BRIGHTNESS_DPS] = "level0"
        self.assertEqual(self.light.is_on, False)

        self.dps[BRIGHTNESS_DPS] = "level1"
        self.assertEqual(self.light.is_on, True)
        self.dps[BRIGHTNESS_DPS] = "level2"
        self.assertEqual(self.light.is_on, True)
        self.dps[BRIGHTNESS_DPS] = "level3"
        self.assertEqual(self.light.is_on, True)
        # Test the case where device is not ready does not cause errors that
        # would prevent initialization.
        self.dps[BRIGHTNESS_DPS] = None
        self.assertEqual(self.light.is_on, False)

    def test_light_brightness(self):
        self.dps[BRIGHTNESS_DPS] = "level0"
        self.assertEqual(self.light.brightness, 0)

        self.dps[BRIGHTNESS_DPS] = "level1"
        self.assertEqual(self.light.brightness, 85)

        self.dps[BRIGHTNESS_DPS] = "level2"
        self.assertEqual(self.light.brightness, 170)

        self.dps[BRIGHTNESS_DPS] = "level3"
        self.assertEqual(self.light.brightness, 255)

    def test_light_state_attributes(self):
        self.assertEqual(self.light.device_state_attributes, {})

    async def test_light_turn_on(self):
        async with assert_device_properties_set(
            self.light._device, {BRIGHTNESS_DPS: "level3"}
        ):
            await self.light.async_turn_on()

    async def test_light_turn_off(self):
        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level0"},
        ):
            await self.light.async_turn_off()

    async def test_light_brightness_to_low(self):
        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level1"},
        ):
            await self.light.async_turn_on(brightness=85)

    async def test_light_brightness_to_mid(self):
        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level2"},
        ):
            await self.light.async_turn_on(brightness=170)

    async def test_light_brightness_to_high(self):
        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level3"},
        ):
            await self.light.async_turn_on(brightness=255)

    async def test_light_brightness_to_off(self):
        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level0"},
        ):
            await self.light.async_turn_on(brightness=0)

    async def test_toggle_turns_the_light_on_when_it_was_off(self):
        self.dps[BRIGHTNESS_DPS] = "level0"

        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level3"},
        ):
            await self.light.async_toggle()

    async def test_toggle_turns_the_light_off_when_it_was_on(self):
        self.dps[BRIGHTNESS_DPS] = "level2"

        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level0"},
        ):
            await self.light.async_toggle()

    async def test_light_brightness_snaps(self):
        async with assert_device_properties_set(
            self.light._device,
            {BRIGHTNESS_DPS: "level1"},
        ):
            await self.light.async_turn_on(brightness=100)
