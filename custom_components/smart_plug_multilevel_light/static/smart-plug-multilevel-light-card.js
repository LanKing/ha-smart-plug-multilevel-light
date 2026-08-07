class SmartPlugMultiLevelLightCardEditor extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._config = null;
    this._form = null;
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    this._config = {
      show_mode: true,
      show_percentage: true,
      always_show_icon_background: false,
      icon_tap_action: { action: "more-info" },
      ...config,
    };
    this._render();
  }

  _schema() {
    return [
      { name: "entity", required: true, selector: { entity: { domain: "light" } } },
      {
        type: "expandable",
        name: "content",
        title: "Content",
        flatten: true,
        schema: [
          { name: "name", selector: { text: {} } },
          {
            name: "icon",
            selector: { icon: {} },
            context: { icon_entity: "entity" },
          },
          { name: "show_mode", selector: { boolean: {} } },
          { name: "show_percentage", selector: { boolean: {} } },
        ],
      },
      {
        type: "expandable",
        name: "interactions",
        title: "Interactions",
        flatten: true,
        schema: [
          {
            name: "icon_tap_action",
            selector: { ui_action: { default_action: "more-info" } },
          },
          { name: "always_show_icon_background", selector: { boolean: {} } },
        ],
      },
    ];
  }

  _computeLabel(schema) {
    return ({
      entity: "Entity",
      name: "Name",
      icon: "Icon",
      show_mode: "Show mode name",
      show_percentage: "Show percentage",
      always_show_icon_background: "Always show icon background",
      icon_tap_action: "Icon tap behavior",
    })[schema.name];
  }

  _computeHelper(schema) {
    return ({
      show_mode:
        "Shows the brightness mode name detected from the configured current thresholds, for example Dim, Low, Medium, or High.",
      show_percentage:
        "Shows a synthetic brightness percentage derived from the mode position. For four modes this is 25%, 50%, 75%, and 100%. It is not measured light output and does not control brightness.",
      always_show_icon_background:
        "Home Assistant normally shows the circular icon background only when the icon has its own action. Enable this option to keep the background visible even when Icon tap behavior is set to Nothing.",
    })[schema.name];
  }

  async _render() {
    if (!this._hass || !this._config) return;

    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.addEventListener("value-changed", (event) => {
        event.stopPropagation();
        const config = { ...event.detail.value };
        this._config = config;
        this.dispatchEvent(new CustomEvent("config-changed", {
          detail: { config },
          bubbles: true,
          composed: true,
        }));
      });
      this.shadowRoot.replaceChildren(this._form);
    }

    this._form.hass = this._hass;
    this._form.data = this._config;
    this._form.schema = this._schema();
    this._form.computeLabel = (schema) => this._computeLabel(schema);
    this._form.computeHelper = (schema) => this._computeHelper(schema);

    await this._form.updateComplete;
    requestAnimationFrame(() => this._alignBooleanControls());
  }

  _allDeep(selector, root = this.shadowRoot) {
    if (!root) return [];
    const matches = [...root.querySelectorAll(selector)];
    for (const element of root.querySelectorAll("*")) {
      if (element.shadowRoot) {
        matches.push(...this._allDeep(selector, element.shadowRoot));
      }
    }
    return matches;
  }

  _alignBooleanControls() {
    for (const selector of this._allDeep("ha-selector-boolean")) {
      const formfield = selector.shadowRoot?.querySelector("ha-formfield");
      if (!formfield) continue;
      formfield.spaceBetween = false;
      formfield.requestUpdate?.();
    }
  }
}

if (!customElements.get("smart-plug-multilevel-light-card-editor")) {
  customElements.define(
    "smart-plug-multilevel-light-card-editor",
    SmartPlugMultiLevelLightCardEditor
  );
}

class SmartPlugMultiLevelLightCard extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this.config = null;
    this._tile = null;
    this._building = null;
    this.attachShadow({ mode: "open" });
  }

  static getStubConfig(hass, entities) {
    const entity = (entities || []).find((id) => {
      const state = hass?.states?.[id];
      return id.startsWith("light.") && state?.attributes?.configured_modes;
    });
    return {
      entity: entity || "",
      show_mode: true,
      show_percentage: true,
      always_show_icon_background: false,
      icon_tap_action: { action: "more-info" },
    };
  }

  static getConfigElement() {
    return document.createElement("smart-plug-multilevel-light-card-editor");
  }

  setConfig(config) {
    if (!config?.entity) throw new Error("entity is required");
    this.config = {
      show_mode: true,
      show_percentage: true,
      always_show_icon_background: false,
      icon_tap_action: { action: "more-info" },
      ...config,
    };
    this._syncTile();
  }

  set hass(hass) {
    this._hass = hass;
    this._syncTile();
  }

  getCardSize() { return 1; }
  getGridOptions() { return { columns: 6, rows: 1, min_columns: 6, min_rows: 1 }; }

  async _ensureTile() {
    if (this._tile) return this._tile;
    if (this._building) return this._building;

    this._building = (async () => {
      const helpers = await window.loadCardHelpers();
      const tile = await helpers.createCardElement({ type: "tile", entity: this.config.entity });
      this.shadowRoot.replaceChildren(tile);
      this._tile = tile;
      this._building = null;
      return tile;
    })();

    return this._building;
  }

  _stateContent(state) {
    if (!state || state.state !== "on") return undefined;
    const mode = state.attributes.mode;
    if (this.config.show_mode && this.config.show_percentage !== false) {
      return mode ? ["mode", "brightness_display"] : "brightness_display";
    }
    if (this.config.show_mode && mode) return "mode";
    if (this.config.show_percentage !== false) return "brightness_display";
    return undefined;
  }

  _nativeConfig(state) {
    const cfg = {
      type: "tile",
      entity: this.config.entity,
      tap_action: { action: "toggle" },
      hold_action: { action: "more-info" },
      icon_tap_action: this.config.icon_tap_action || { action: "more-info" },
    };

    if (this.config.name) cfg.name = this.config.name;
    if (this.config.icon) cfg.icon = this.config.icon;
    const stateContent = this._stateContent(state);
    if (stateContent) cfg.state_content = stateContent;
    return cfg;
  }

  _visualState(realState) {
    if (!realState) return realState;

    const isOn = realState.state === "on";
    const pct = Math.max(0, Math.min(100, Number(realState.attributes.brightness_pct ?? 0)));
    const visualPct = isOn ? 40 + 0.6 * pct : 0;
    const brightness = isOn
      ? Math.max(1, Math.round(visualPct * 255 / 100))
      : undefined;

    const t = visualPct / 100;
    const gamma = 1.0;
    const floor = 0.10;
    const scale = floor + (1 - floor) * Math.pow(t, gamma);
    const baseRgb = [255, 137, 14];
    const visualRgb = baseRgb.map((channel) => Math.max(1, Math.round(channel * scale)));

    const rgbToHs = ([r8, g8, b8]) => {
      const r = r8 / 255, g = g8 / 255, b = b8 / 255;
      const max = Math.max(r, g, b), min = Math.min(r, g, b);
      const d = max - min;
      let h = 0;
      if (d !== 0) {
        if (max === r) h = 60 * (((g - b) / d) % 6);
        else if (max === g) h = 60 * (((b - r) / d) + 2);
        else h = 60 * (((r - g) / d) + 4);
      }
      if (h < 0) h += 360;
      const sat = max === 0 ? 0 : (d / max) * 100;
      return [Math.round(h * 10) / 10, Math.round(sat * 10) / 10];
    };
    const visualHs = rgbToHs(visualRgb);

    const attributes = {
      ...realState.attributes,
      brightness_display: isOn ? `${Math.round(pct)}%` : undefined,
      supported_color_modes: ["hs"],
      color_mode: isOn ? "hs" : null,
    };

    if (isOn) {
      attributes.brightness = brightness;
      attributes.rgb_color = visualRgb;
      attributes.hs_color = visualHs;
    } else {
      delete attributes.brightness;
      delete attributes.rgb_color;
      delete attributes.hs_color;
    }

    return {
      ...realState,
      attributes,
    };
  }

  _visualHass(realState) {
    const visualState = this._visualState(realState);
    if (!visualState) return this._hass;

    return {
      ...this._hass,
      states: {
        ...this._hass.states,
        [this.config.entity]: visualState,
      },
    };
  }

  _allDeep(selector, root) {
    if (!root) return [];
    const matches = [...root.querySelectorAll(selector)];
    for (const element of root.querySelectorAll("*")) {
      if (element.shadowRoot) {
        matches.push(...this._allDeep(selector, element.shadowRoot));
      }
    }
    return matches;
  }

  async _syncIconBackground(tile) {
    await tile.updateComplete;
    await new Promise((resolve) => requestAnimationFrame(resolve));

    const forceBackground = this.config.always_show_icon_background === true;
    for (const tileIcon of this._allDeep("ha-tile-icon", tile.shadowRoot)) {
      const container = tileIcon.shadowRoot?.querySelector(".container");
      if (!container) continue;
      container.classList.toggle(
        "background",
        forceBackground || tileIcon.interactive === true
      );
    }
  }

  async _syncTile() {
    if (!this.config || !this._hass) return;

    const realState = this._hass.states[this.config.entity];
    const tile = await this._ensureTile();

    tile.setConfig(this._nativeConfig(realState));
    tile.hass = this._visualHass(realState);
    await this._syncIconBackground(tile);
  }
}

if (!customElements.get("smart-plug-multilevel-light-card")) {
  customElements.define("smart-plug-multilevel-light-card", SmartPlugMultiLevelLightCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "smart-plug-multilevel-light-card")) {
  window.customCards.push({
    type: "smart-plug-multilevel-light-card",
    name: "Smart Plug Multi-Level Light",
    description: "Native Home Assistant Tile Card for a smart-plug multi-level light. Visual color follows brightness percentage and OFF icon handling is delegated to ha-mdi-off-fallback.",
    preview: true,
    getEntitySuggestion: (hass, entityId) => {
      if (!entityId?.startsWith("light.")) return null;
      const state = hass.states[entityId];
      if (!state || !("configured_modes" in state.attributes)) return null;
      return {
        config: {
          type: "custom:smart-plug-multilevel-light-card",
          entity: entityId,
          show_mode: true,
          show_percentage: true,
          always_show_icon_background: false,
          icon_tap_action: { action: "more-info" },
        },
      };
    },
  });
}
