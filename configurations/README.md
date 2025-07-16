# ESPHome Volume Sensor Component

This is a custom ESPHome component designed for advanced sound level and volume detection. It continuously samples audio from an analog microphone, identifies the peak sound amplitude over a configurable time window, and publishes the results as dB, percentage, and raw ADC values for diagnostics.

It is built to be **non-blocking and stable**, allowing for high-frequency sampling (e.g., every 20ms) without interfering with essential network operations like the Wi-Fi connection and Home Assistant API, thanks to its smart polling schedule.

A complete example configuration file, [`volume-sensor.yaml`](./configurations/volume-sensor.yaml), is available in the [`/configurations`](./configurations) directory of this repository for a practical starting point.

## Key Features 🔊

  * **Peak Detection:** Measures sound continuously but only publishes the loudest event within a given time window (e.g., the peak volume in the last 5 seconds).
  * **Stable Polling:** Uses a safe polling pattern that starts with a long interval during Wi-Fi connection and switches to a fast interval only after a stable connection is established.
  * **Flexible Sensitivity Control:** A dynamic sensitivity slider allows you to adjust the sensor's responsiveness in real-time.
  * **Advanced Calibration:** Supports software ADC range calibration to fine-tune the sensor's measurement window.
  * **Detailed Diagnostics:** Provides optional sensors for `signal_max` and `signal_min` values, which are essential for initial hardware setup.

-----

## Step 1: Hardware Setup & Calibration 🛠️

This is the most important step to get meaningful data. The goal is to properly set the **DC bias** of your microphone module to ensure the audio signal has the maximum possible room to oscillate without clipping.

### The Potentiometer's True Role: DC Bias vs. Gain

It's a common misconception, but the potentiometer on most standard KY-038 modules **does not adjust gain** for the analog output. The LM393 chip on the board is a *comparator* and is only used for the separate digital (D0) pin.

For our purpose of using the **analog (A0) pin**, the potentiometer's function is to adjust the **DC bias voltage**. This is the "silent" voltage level that the AC audio signal oscillates around.

### Calibration Process: Centering the Bias

The goal is to set the silent DC bias to the exact center of the ESP's ADC range (\~512 on a 10-bit ADC). This gives the audio signal equal "headroom" to swing up and down, preventing distortion and capturing the full dynamic range of sounds.

1.  **Initial Setup:** Flash your ESP with a configuration that enables `raw_max_sensor` and `raw_min_sensor` (the example YAML below does this). Open the ESPHome logs to monitor the output.
2.  **Ensure a Quiet Environment:** Place the sensor in the quietest possible location for this step.
3.  **Adjust and Monitor:** In silence, the `Raw ADC Max` and `Raw ADC Min` values should be very close to each other. Your goal is to **slowly turn the potentiometer screw** until this resting value is as close as possible to **512**.
4.  Once the resting value is centered at or near 512, your hardware bias is correctly calibrated.

### How to Truly Improve Sensitivity (Granularity)

The standard KY-038 module provides very little, if any, amplification for its analog signal. This means that quiet sounds will produce a very small voltage swing (low amplitude), which can be difficult for the ADC to measure with precision.

To reliably detect quieter sounds and increase the overall resolution of your measurements, you should feed the microphone's output into a dedicated **amplifier circuit** before connecting it to the ESP's analog pin. This is typically done with an **operational amplifier (op-amp)**, such as the classic **LM741** or more modern equivalents, configured as a non-inverting amplifier. This will boost the AC signal, making it much easier for the ADC to read.

-----

## Step 2: Software Configuration (YAML)

After calibrating the hardware, you can fine-tune the sensor's behavior in your YAML file.

### Configuration Parameters

| Parameter | Required | Description |
| :--- | :--- | :--- |
| `pin` | **Yes** | The analog input pin connected to the microphone's output. **Must be an ADC-capable pin** (e.g., `A0` on ESP8266). |
| `update_interval` | **Yes** | The sampling frequency. This is set to a long, safe default (`100s`) and should be changed to a fast interval (e.g., `20ms`) via an `on_connect` automation to ensure Wi-Fi stability. |
| `publish_interval` | No | The interval at which the peak values from the window are published. Default: `5s`. |
| `sampling_duration` | No | The duration of each high-frequency sampling burst. Default: `20ms`. |
| `sensitivity` | No | A value (typically 10-100) that adjusts the measurement range. Higher values make the range smaller, causing the sensor to react more strongly to sound. Default: `50`. |
| `adc_min_calibration` | No | Software calibration. The raw ADC value that corresponds to the minimum of your measurement range. Useful for ignoring noise below a certain threshold. |
| `adc_max_calibration` | No | Software calibration. The raw ADC value that corresponds to the maximum of your measurement range. |
| `db_sensor` | No | Enables a dedicated sensor for the calculated dB value. |
| `percentage_sensor` | No | Enables a dedicated sensor for the calculated volume percentage. |
| `raw_max_sensor` | No | Enables a sensor that reports the peak `signal_max` found in the publishing window. **Essential for hardware calibration.** |
| `raw_min_sensor` | No | Enables a sensor that reports the peak `signal_min` found in the publishing window. **Essential for hardware calibration.** |

### Full Configuration Example

The YAML code below is a complete, best-practice example. You can also find this file at [`/configurations/volume-sensor.yaml`](./configurations/volume-sensor.yaml).

```yaml
# This automation is CRUCIAL for stability.
# It starts sampling slowly, then speeds up after Wi-Fi connects.
wifi:
  # ... (your Wi-Fi credentials) ...
  on_connect:
    then:
      - logger.log: "WiFi connected. Starting fast sampling."
      - component.resume:
          id: volume_sensor_main # The ID of your volume_sensor component
          update_interval: 20ms # The fast sampling interval

sensor:
  - platform: volume_sensor
    id: volume_sensor_main
    internal: true # The main component is just a controller.
    pin: A0

    # Start with a very long interval to allow Wi-Fi to connect reliably.
    # The 'on_connect' automation above will override this.
    update_interval: 100s

    # Publish the peak value found every 5 seconds.
    publish_interval: 5s

    # Each sample burst lasts 20ms. The next burst starts immediately.
    sampling_duration: 20ms

    # --- Measurement Configuration ---
    sensitivity: 50
    # Use calibration to narrow the focus to your sensor's actual operating range,
    # determined after completing the hardware calibration in Step 1.
    adc_min_calibration: 200
    adc_max_calibration: 900

    # --- Child Sensors ---
    db_sensor:
      name: "Volume DB"

    raw_max_sensor:
      name: "Raw ADC Max"

    raw_min_sensor:
      name: "Raw ADC Min"

    percentage_sensor:
      name: "Volume Percent"

# ... (anothers sensors or sliders) ...
```

-----

## Step 3 (Optional): Optimize for Performance

Once you have completed the hardware and software calibration and are satisfied with the sensor's performance, you can disable the diagnostic `raw` sensors to gain a slight performance improvement.

The component's code is optimized to only execute logic for enabled sensors. By disabling `raw_max_sensor` and `raw_min_sensor`, you prevent the code from needing to store and publish these values, freeing up a small amount of CPU time and memory.

To do this, simply comment out or delete the `raw_max_sensor` and `raw_min_sensor` sections from your YAML file:

```yaml
sensor:
  - platform: volume_sensor
    id: volume_sensor_main
    # ... (all your other settings) ...

    db_sensor:
      name: "Volume DB"

    # raw_max_sensor: <-- Comment out or delete this block
    #   name: "Raw ADC Max"

    # raw_min_sensor: <-- Comment out or delete this block
    #   name: "Raw ADC Min"

    percentage_sensor:
      name: "Volume Percent"
```

-----

## How It Works (Theory)

### Hardware Principle: The AC Wave

An analog sound module (like the KY-038) produces an **AC (Alternating Current)** audio signal that oscillates around a central **DC (Direct Current) bias voltage**.

  * In **silence**, the output is just the stable DC bias (ideally half the ESP's ADC voltage, or \~512).
  * When there is **sound**, the voltage oscillates above and below this bias.
  * The **loudness** corresponds to the **amplitude** of this AC wave, which is the difference between its highest peak and lowest valley (`signal_max - signal_min`).

### Software Logic: Peak-Hold & Publish

The component's code uses a "hybrid" polling model to capture peak sound events effectively:

1.  **High-Frequency Sampling:** The component's `update()` function is called very frequently (e.g., every 20ms). Each time, it performs a quick sampling burst to measure the `current_amplitude` of the sound.
2.  **Peak-Hold Logic:** This `current_amplitude` is compared to a value stored in memory (`max_amplitude_in_window_`). If the new amplitude is louder, the component updates its memory with the new peak amplitude and also saves the exact `signal_max` and `signal_min` values from that specific moment.
3.  **Low-Frequency Publishing:** A separate internal timer checks when it's time to publish (e.g., every 5 seconds). When this timer expires, the component takes the final stored peak values, calculates the dB and percentage, and publishes all sensor data. It then resets the peak values to zero to begin monitoring the next time window.

-----

## Example Automation: Loud Noise Notification

Once you have the sensor reporting data to Home Assistant, you can use it to trigger automations. Here is a simple but powerful example that sends a notification to your phone if a loud noise is detected for a sustained period.

### Prerequisites

  * The `volume_sensor` component fully configured and integrated with Home Assistant.
  * The [Home Assistant Companion App](https://www.home-assistant.io/integrations/mobile_app/) installed and the `notify` service configured for your device.

### Home Assistant Automation YAML

You can add this directly to your `automations.yaml` file or create it using the Automation Editor in the UI.

```yaml
alias: "Alert on Sustained Loud Noise"
description: "Sends a notification if the volume is above 80% for 10 seconds."
trigger:
  - platform: numeric_state
    entity_id: sensor.volume_percent
    # The threshold: trigger when volume goes above 80%.
    above: 80
    # The duration: the noise must be sustained for 10 seconds to avoid
    # false alarms from short events like a door slamming.
    for:
      seconds: 10

condition:
  # (Optional) You can add conditions here. For example, only run this
  # automation if you are not at home.
  # - condition: state
  #   entity_id: group.all_persons
  #   state: 'not_home'

action:
  - service: notify.mobile_app_your_phone_name # <-- CHANGE THIS to your notify service
    data:
      title: "Loud Noise Detected!"
      message: "A loud noise has been detected. The current volume is {{ trigger.to_state.state | round(0) }}%."
      data:
        # This helps group notifications on your phone
        tag: "loud-noise-alert"

mode: single # Ensures the automation doesn't run multiple times for the same event
```

### How to Customize This Automation

  * **Threshold (`above: 80`):** Adjust this value up or down depending on what you consider a "loud" event in your environment. Watch the sensor's history in Home Assistant to find a good value.
  * **Duration (`for: seconds: 10`):** Increase this time to be less sensitive to shorter noises, or decrease it to be more reactive.
  * **Action (`service: notify.mobile_app_...`):** Change this to your specific `notify` service. You can also change the action entirely, for example, to turn on a light (`light.turn_on`), flash a smart bulb, or play a message on a smart speaker.