> [!TIP]
> This is a test TIP alert.

<sub>🇷🇺&nbsp;<a href="docs/README_RU.md">Р⁠у⁠с⁠с⁠к⁠и⁠й</a></sub>

<a href="https://www.home-assistant.io/"><img src="https://img.shields.io/badge/Home%20Assistant-Helper-41BDF5?logo=homeassistant&logoColor=white" alt="Home Assistant"></a>
<a href="https://hacs.xyz/"><img src="https://img.shields.io/badge/HACS-Integration-41BDF5" alt="HACS"></a>
<a href="https://github.com/LanKing/ha-smart-plug-multilevel-light/releases"><img src="https://img.shields.io/github/v/release/LanKing/ha-smart-plug-multilevel-light?label=release&cacheSeconds=300" alt="Latest release"></a>
<a href="https://github.com/LanKing/ha-smart-plug-multilevel-light/releases"><img src="https://img.shields.io/github/downloads/LanKing/ha-smart-plug-multilevel-light/total?label=downloads&cacheSeconds=300" alt="Downloads"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/LanKing/ha-smart-plug-multilevel-light?cacheSeconds=300" alt="License"></a>

> This integration combines a lamp without digital controls and a smart plug into a single Home Assistant entity. It determines the lamp's state and current brightness mode from power consumption, displays them in a card, and can turn on a lamp that was switched off with its own button by briefly cutting and restoring power through the smart plug.

# 🔌 Smart Plug Multi-Level Light

![Card mode examples](docs/ha-smart-plug-multilevel-light-card-modes-v4.png)

**✨ Features and highlights:**

* Creates a native Home Assistant `light` entity compatible with automations, scripts, and the standard HA interface;
* Turns the lamp on correctly regardless of how it was switched off: if power was cut through the smart plug, it simply turns the plug on; if the lamp was switched off with its own button while the plug remained on, it performs a power cycle;
* Automatically determines the lamp's current mode from its measured stable power consumption;
* Provides a simple configuration flow in which you name the modes supported by your lamp and the integration learns the stable power consumption of each mode;
* Reads power in real time during initial setup, so you only need to switch the lamp to the next mode and press the test button;
* Filters out unstable power readings, preventing the card indicator from changing erratically when power fluctuates within one mode or even briefly matches another mode;
* Supports any number of modes;
* Builds the card on top of the native Home Assistant Tile Card while preserving its geometry, background, hover effects, dimensions, typography, and standard actions;
* Represents the current brightness visually through color intensity;
* Calculates brightness linearly relative to the maximum power value and can optionally round the calculated brightness to the nearest 5% for cleaner percentage display;
* Provides flexible control over the card's displayed information and appearance;
* Allows only a power sensor belonging to the selected smart plug to be chosen;
* Allows the power-cycle delay to be configured for different lamp and plug models;
* Allows the power threshold below which the lamp is considered off to be configured;
* Localizes the interface for 64 Home Assistant locales.


## 🗜 Hardware setup

You will need:

1. A smart plug that exposes power control (`switch`) and power measurement (`sensor` with `device_class: power`) to HA. Both entities must belong to the same device and be enabled.
2. A non-smart lamp that turns on automatically when power is supplied and, ideally, has several brightness modes.

> I used a [Tuya TS011F plug (in a Girier enclosure)](https://www.zigbee2mqtt.io/devices/TS011F_plug_3.html). At the start of my experiments, several Girier plugs were unsuitable because their measurements were inaccurate, but this model worked even though it also came in a Girier enclosure.

### 👨‍🔬 An important setting I applied to my plug

> My plug cannot report readings to HA automatically and supports only polling at a configured interval. Its default interval was 60 seconds. Set it to 1 second; otherwise, mode changes will take a very long time to appear.

The following instructions apply only to plugs connected through Zigbee2MQTT. Other users should configure the update frequency for their own setup:

1. Open **Home Assistant → Zigbee2MQTT**. If Zigbee2MQTT is not in the sidebar, open **Settings → Apps → Zigbee2MQTT → Open Web UI**.
2. Open **Devices**.
3. Select the required plug.
4. Open the **Settings (specific)** tab.
5. Set **Measurement poll interval** to 1 s.


<a id="installation"></a>
## 📦 Installation

### 🛍 Installation through HACS

ℹ️ [What is HACS and how do I install it?](https://github.com/LanKing/ha-tools/blob/main/appendix-what-is-hacs/README.md)

🚀 [Try adding the repository using this link](https://my.home-assistant.io/redirect/hacs_repository/?owner=LanKing&repository=ha-smart-plug-multilevel-light&category=integration). If your HA instance supports this method, click **Add** in the window that opens, then click **Download** in the lower-right corner. If the installation succeeds, you can skip the remaining installation steps and go directly to [Quick start](#getting-started).

#### 1. Add the repository

Until the repository is included in the default HACS catalog, add it as a custom repository:

1. Open **HACS → Integrations**.
2. Open the menu in the upper-right corner and select **Custom repositories**.
3. Add:

```text
https://github.com/LanKing/ha-smart-plug-multilevel-light
```

4. Select **Integration** as the type and click **Add**.

> Adding the repository only makes the integration available in HACS. To install it, open its page separately and click **Download**.

#### 2. Install the integration

1. Find `Smart Plug Multi-Level Light` in HACS.
2. Open the integration and click **Download**.
3. Fully restart Home Assistant after installation.

<a id="manual-installation"></a>
### 🧑‍💻 Installation without HACS

1. On the repository page, click **Code → Download ZIP**.
2. Extract the archive.
3. Copy this folder:

```text
custom_components/smart_plug_multilevel_light
```

to the Home Assistant configuration directory:

```text
/config/custom_components/smart_plug_multilevel_light
```

The final path to `manifest.json` must be:

```text
/config/custom_components/smart_plug_multilevel_light/manifest.json
```

4. Fully restart Home Assistant.

> Do not copy the outer repository folder into `custom_components`. The `smart_plug_multilevel_light` folder itself must be directly inside `custom_components`.

The card is bundled with the integration, so HACS is not required to install it. After you copy the files manually, restart Home Assistant, and create the first helper, the integration serves the card's JavaScript file and automatically registers it in dashboard resources when the default `storage` mode is used. In YAML resource mode, register the card manually as described below.

<a id="getting-started"></a>
## 🚀 Quick start after installation

### 🛠 Configuration

1. Open **[Settings → Devices & services → Helpers](https://my.home-assistant.io/redirect/helpers/)** and click **Create helper**.
2. Select **Smart Plug Multi-Level Light**.
3. Select the smart plug connected to the lamp. Only plugs for which Home Assistant detects a power sensor on the same device are shown.
4. On the next step, configure the lamp:
   - **Light name** — the name of the entity to be created, for example `FloorLamp`;
   - **Power sensor** — the plug's power sensor.
5. Under **🔅 Brightness modes**, add at least one brightness mode by clicking **Add**.<br />
<img src="docs/modes-edit.png" width="50%"/><br />
Switch the lamp with its physical button, enter the mode name, and click **Test stable power**. Once a stable value has been measured, click **Apply**.

6. After adding the first mode, repeat these steps for all remaining modes. The result should look similar to this:<br />
<img src="docs/modes-list.png" width="50%"/>
7. Save the helper. Home Assistant creates a new `light` entity, for example `light.FloorLamp`.

### 🧩 Lovelace card

1. Open the required dashboard, enter edit mode, and click **Add card**.
2. Select **Smart Plug Multi-Level Light**, specify the created `light` entity, and save the card.

If the card is not available in the list, you may be using [Lovelace YAML resource mode](#yaml-lovelace-mode).

### 🎨 Visual effects

#### Card settings

Open the dashboard containing the card, enter edit mode, and click **Edit** on the required card.

Expand **Content** to access these settings:

- **Show mode name** — shows or hides the current mode name, such as Dim, Low, Medium, or High.
- **Show percentage** — shows or hides the calculated brightness percentage.

Expand **Interactions** to access:

- **Always show icon background** — keeps the circular icon background visible even when its separate action is disabled.

🚫 If, like me, you use a custom card icon that does not appear crossed out when the entity is off, I recommend my other plugin, [Mdi Off Fallback](https://github.com/LanKing/ha-mdi-off-fallback), which fixes this visual issue.

#### Round brightness to 5%

Open **[Settings → Devices & services → Helpers](https://my.home-assistant.io/redirect/helpers/)**, find the previously created **Smart Plug Multi-Level Light** helper, and open its settings. Enable or disable **Round brightness to 5% (may look nicer)**.

When enabled, the calculated percentage is rounded to the nearest 5%, for example: 33% → 35%, 67% → 65%.

Rounding affects only the displayed percentage and the card's visual intensity. It does not change mode detection or lamp operation. Rounding is disabled by default.


## 🧩 Lovelace card details

Available parameters:

| Parameter | Type | Default | Purpose |
|---|---|---:|---|
| `entity` | string | required | entity created by the integration |
| `name` | string | entity name | overrides the name shown on the card |
| `icon` | string | entity icon | overrides the icon |
| `show_mode` | boolean | `true` | shows the mode name |
| `show_percentage` | boolean | `true` | shows the synthetic percentage |
| `icon_tap_action` | action | `more-info` | additional action when the icon is tapped |
| `always_show_icon_background` | boolean | `false` | always shows the circular icon background, even when `None` is selected for `icon_tap_action` |

Complete example:

```yaml
type: custom:smart-plug-multilevel-light-card
entity: light.floor_lamp
name: Floor lamp
icon: mdi:floor-lamp
show_mode: true
show_percentage: true
icon_tap_action:
  action: more-info
always_show_icon_background: false
```


<a id="yaml-lovelace-mode"></a>
### Lovelace YAML resource mode

> You most likely do not use this mode. If the card works and you have not encountered any problems, skip this section.

If your `configuration.yaml` explicitly contains:

```yaml
lovelace:
  resource_mode: yaml
```

Home Assistant does not allow the integration to modify the resource list automatically. In this case, add the resource manually:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /api/smart_plug_multilevel_light/smart-plug-multilevel-light-card.js?v=0.10.9
      type: module
```

After making the change, reload the Lovelace resources or restart Home Assistant.

<a id="troubleshooting"></a>
## 🧯 Troubleshooting

### The integration does not appear in the helper list

**Likely cause:** the path is incorrect or Home Assistant was not restarted.

Check that this file exists:

```text
/config/custom_components/smart_plug_multilevel_light/manifest.json
```

Then fully restart Home Assistant and check the logs for `smart_plug_multilevel_light` errors.

### The plug list is empty

The integration shows only `switch` entities associated with devices that also expose an enabled sensor with `device_class: power`.

Check under **[Settings → Devices & services → Entities](https://my.home-assistant.io/redirect/entities/)**:

- Do the `switch` and power sensor belong to the same device?
- Is the power sensor enabled?
- Is its `device_class` set correctly?
- Does it have a numeric state?

### Creation stops with a missing power sensor message

After you select a plug, the integration checks for a power sensor again. The error occurs if the sensor was removed, disabled, moved to another device, or no longer has `device_class: power`.

### The lamp is shown as Off while the plug is on

Check the power sensor value. The virtual lamp is considered off at `0 W`; with a positive value, it should be detected as `on`.

### The lamp is shown as On while it is physically off

Make sure the selected power sensor actually reports `0 W` when the lamp is switched off with its own button.

### The wrong mode is detected

Check **🐞 Last measures** in the settings and the `power_history`, `power_history_modes`, `power_sample_interval_seconds`, and `selected_power_mode` attributes. `power_history` contains the most recent recorded power values, `power_history_modes` contains the mode assigned to each value using the configured thresholds, `power_sample_interval_seconds` is the periodic sampling interval, and `selected_power_mode` is the currently confirmed mode.

### The card does not appear in the list

Automatic registration occurs only after at least one configured helper has been loaded and only when resources use `storage` mode. It does not matter whether the integration was installed through HACS or manually.

Check **[Settings → Dashboards → ⋮ → Resources](https://my.home-assistant.io/redirect/lovelace_resources/)**. The following URL must be present:

```text
/api/smart_plug_multilevel_light/smart-plug-multilevel-light-card.js?v=0.10.9
```

In YAML mode, [add the resource manually](#yaml-lovelace-mode).

### The old card is still displayed after an update

1. Fully restart Home Assistant.
2. Reload the page while clearing the browser cache.
3. Check the version number in the dashboard resource URL.
4. In the mobile app, fully close and reopen the frontend.

## 🗑 Removal

1. Delete all **Smart Plug Multi-Level Light** helpers under **[Settings → Devices & services → Helpers](https://my.home-assistant.io/redirect/helpers/)**.
2. Remove the integration through HACS, or manually delete this folder:

```text
/config/custom_components/smart_plug_multilevel_light
```

3. Check **[Settings → Dashboards → ⋮ → Resources](https://my.home-assistant.io/redirect/lovelace_resources/)** and manually remove the card resource if it remains:

```text
/api/smart_plug_multilevel_light/smart-plug-multilevel-light-card.js?v=0.10.9
```

4. Fully restart Home Assistant.
5. If necessary, reload the page while clearing the frontend cache.


## 📄 License

This project is distributed under the [MIT License](LICENSE).
