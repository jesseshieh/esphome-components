# Reubertt's ESPHome Components

Welcome to my personal collection of custom components for ESPHome. This repository serves as a central place where I publish and maintain the components I create for my own projects and for the community.

-----

## 🚀 How to Use

To use a component from this repository in your ESPHome project, add the following configuration to your device's YAML file, replacing `component_name` with the actual name of the component you wish to use (e.g., `volume_sensor`).

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/Reubertt/esphome-components
      components: [component_name]
```

-----

## 📦 Available Components

### 1\. Volume Sensor (`volume_sensor`)

An advanced sound level sensor for ESP8266/ESP32 that continuously samples an analog microphone to detect the **peak amplitude** over a configurable time window.

  - It intelligently separates high-frequency sampling from low-frequency publishing to capture momentary sound spikes without overwhelming your network or interfering with Wi-Fi connectivity.
  - The component is highly configurable, featuring real-time sensitivity adjustments, software calibration, and detailed diagnostic sensors to help with initial hardware setup.

**Example Usage:**

```yaml
sensor:
  - platform: volume_sensor
    pin: A0
    publish_interval: 5s
    sensitivity: 50
    db_sensor:
      name: "Volume DB"
    percentage_sensor:
      name: "Volume Percent"
```

*(More components will be listed here as they are added to the repository.)*

-----

## ⚙️ Example Configurations

You can find complete, working example configurations for each component in the **[/configurations](./configurations/)** directory. These files provide a practical and tested starting point for your own projects and include detailed calibration guides.

## Legacy Configurations

The **[/configurations/legacy](./configurations/legacy/)** directory contains updated versions of code that I may have previously posted on other platforms, such as the Home Assistant Community Forum. If you are looking for the most recent version of my older, publicly shared projects, you will likely find them here.

## 🐞 Issues & Suggestions

If you encounter any bugs, have questions, or would like to suggest an improvement for a component, please feel free to **[open an issue](https://github.com/Reubertt/esphome-components/issues)** in this repository.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
