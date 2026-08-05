# Smart Plug Multi-Level Light

A Home Assistant helper that represents a physical multi-level lamp connected through a smart plug as a `light` entity.

The integration determines whether the lamp is on from power consumption and identifies its current brightness mode from the measured current.

## Features

- Creates a native Home Assistant `light` entity.
- Determines OFF/ON state from the smart plug power sensor.
- Determines the active mode from current thresholds.
- Exposes the mode as a percentage based on its position in the configured mode list.
- Automatically sorts modes by current threshold.
- Restarts a powered but physically switched-off lamp by cycling the smart plug.
- Includes a Tile-based Lovelace card and registers it automatically.
- Does not draw OFF icon fallbacks; use `ha-mdi-off-fallback` for that.

## Installation with HACS

1. Open **HACS → Integrations**.
2. Open the menu and select **Custom repositories**.
3. Add:

   ```text
   https://github.com/LanKing/ha-smart-plug-multilevel-light
   ```

4. Select category **Integration**.
5. Install **Smart Plug Multi-Level Light**.
6. Restart Home Assistant.
7. Open **Settings → Devices & services → Helpers → Create helper**.
8. Select **Smart Plug Multi-Level Light** and configure the entities and thresholds.

## Lovelace card

The integration serves and registers the bundled card automatically after the first helper is loaded. No Dashboard resource needs to be added manually when Lovelace resources use the default storage mode.

Add the card:

```yaml
type: custom:smart-plug-multilevel-light-card
entity: light.floor_lamp
```

The visual editor also supports changing the name, icon, mode label and percentage display.

When Lovelace resources are explicitly managed in YAML mode, add this resource manually:

```yaml
lovelace:
  resources:
    - url: /api/smart_plug_multilevel_light/smart-plug-multilevel-light-card.js?v=0.6.1
      type: module
```

## How mode detection works

Modes are sorted by current threshold in ascending order. The integration selects the highest threshold that is less than or equal to the measured current.

Example:

| Mode | Threshold |
|---|---:|
| Dim | 0.020 A |
| Low | 0.025 A |
| Medium | 0.030 A |
| High | 0.040 A |

A measured current of `0.028 A` is classified as **Low**.

## Turning the light on

- If the smart plug is OFF, the integration turns it ON.
- If the smart plug is already ON but power consumption indicates that the physical lamp is OFF, the integration turns the plug OFF, waits for the configured reset delay, and turns it ON again.
- If the lamp is already on, no power cycle is performed.

## Updating

Update through HACS and restart Home Assistant. The integration updates the registered card resource URL automatically to invalidate the browser cache.

## License

MIT
