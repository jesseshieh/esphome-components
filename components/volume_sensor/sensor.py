import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_ID, CONF_PIN, CONF_SENSITIVITY, CONF_NAME

CONF_SAMPLING_DURATION = "sampling_duration"
CONF_PUBLISH_INTERVAL = "publish_interval"
CONF_ADC_MIN_CALIBRATION = "adc_min_calibration"
CONF_ADC_MAX_CALIBRATION = "adc_max_calibration"
CONF_RAW_MAX_SENSOR = "raw_max_sensor"
CONF_RAW_MIN_SENSOR = "raw_min_sensor"
CONF_PERCENTAGE_SENSOR = "percentage_sensor"
CONF_DB_SENSOR = "db_sensor"

volume_sensor_ns = cg.esphome_ns.namespace("volume_sensor")
VolumeSensor = volume_sensor_ns.class_("VolumeSensor", sensor.Sensor, cg.PollingComponent)

CONFIG_SCHEMA = sensor.sensor_schema(VolumeSensor).extend({
    cv.GenerateID(): cv.declare_id(VolumeSensor),
    cv.Required(CONF_PIN): cv.string,
    cv.Optional(CONF_SAMPLING_DURATION, default="20ms"): cv.positive_time_period_milliseconds,
    cv.Optional(CONF_PUBLISH_INTERVAL, default="5s"): cv.positive_time_period_milliseconds,
    cv.Optional(CONF_SENSITIVITY, default=50): cv.float_,
    cv.Optional(CONF_ADC_MIN_CALIBRATION): cv.int_range(min=0, max=1023),
    cv.Optional(CONF_ADC_MAX_CALIBRATION): cv.int_range(min=0, max=1023),
    cv.Optional(CONF_RAW_MAX_SENSOR): sensor.sensor_schema(
        unit_of_measurement="adc",
        icon="mdi:arrow-up-box",
        accuracy_decimals=0,
    ),
    cv.Optional(CONF_RAW_MIN_SENSOR): sensor.sensor_schema(
        unit_of_measurement="adc",
        icon="mdi:arrow-down-box",
        accuracy_decimals=0,
        ),
    cv.Optional(CONF_PERCENTAGE_SENSOR): sensor.sensor_schema(
        unit_of_measurement="%",
        icon="mdi:volume-high",
        accuracy_decimals=0,
    ),
    cv.Optional(CONF_DB_SENSOR): sensor.sensor_schema(
        unit_of_measurement="dB",
        icon="mdi:waveform",
        accuracy_decimals=1,
    ),
}).extend(cv.polling_component_schema("100s"))

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    cg.add(var.set_pin(cg.RawExpression(config[CONF_PIN])))
    cg.add(var.set_sensitivity(config[CONF_SENSITIVITY]))
    cg.add(var.set_sampling_duration(config[CONF_SAMPLING_DURATION]))
    cg.add(var.set_publish_interval(config[CONF_PUBLISH_INTERVAL]))

    if CONF_ADC_MIN_CALIBRATION in config:
        cg.add(var.set_adc_min_calibration(config[CONF_ADC_MIN_CALIBRATION]))
    if CONF_ADC_MAX_CALIBRATION in config:
        cg.add(var.set_adc_max_calibration(config[CONF_ADC_MAX_CALIBRATION]))

    if raw_max_config := config.get(CONF_RAW_MAX_SENSOR):
        sens = await sensor.new_sensor(raw_max_config)
        cg.add(var.set_raw_max_sensor(sens))
    if raw_min_config := config.get(CONF_RAW_MIN_SENSOR):
        sens = await sensor.new_sensor(raw_min_config)
        cg.add(var.set_raw_min_sensor(sens))
    if percentage_config := config.get(CONF_PERCENTAGE_SENSOR):
        sens = await sensor.new_sensor(percentage_config)
        cg.add(var.set_percentage_sensor(sens))

    if db_config := config.get(CONF_DB_SENSOR):
        sens = await sensor.new_sensor(db_config)
        cg.add(var.set_db_sensor(sens))
    elif CONF_NAME in config:
        await sensor.register_sensor(var, config)