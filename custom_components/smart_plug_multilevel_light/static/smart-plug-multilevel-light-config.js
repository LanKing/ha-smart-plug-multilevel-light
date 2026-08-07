class SmartPlugModesSelector extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._selector = null;
    this._value = [];
    this._label = "Brightness modes";
    this._helper = "";
    this._disabled = false;
    this._dialog = null;
    this.attachShadow({ mode: "open" });
  }

  set hass(value) {
    this._hass = value;
  }

  get hass() {
    return this._hass;
  }

  set selector(value) {
    this._selector = value;
    this._render();
  }

  get selector() {
    return this._selector;
  }

  set value(value) {
    this._value = Array.isArray(value) ? value : [];
    this._render();
  }

  get value() {
    return this._value;
  }

  set label(value) {
    this._label = value || "Brightness modes";
    this._render();
  }

  get label() {
    return this._label;
  }

  set helper(value) {
    this._helper = value || "";
    this._render();
  }

  get helper() {
    return this._helper;
  }

  set disabled(value) {
    this._disabled = Boolean(value);
    this._render();
  }

  get disabled() {
    return this._disabled;
  }

  set required(_) {}
  set narrow(_) {}
  set name(_) {}
  set placeholder(_) {}
  set context(_) {}
  set localizeValue(_) {}

  _isRu() {
    return String(this._hass?.language || "").toLowerCase().startsWith("ru");
  }

  _t(key) {
    const ru = {
      add: "Добавить",
      edit: "Изменить",
      delete: "Удалить",
      cancel: "Отмена",
      save: "Сохранить",
      add_mode: "Добавить режим",
      edit_mode: "Изменить режим",
      mode_name: "Название режима",
      current_threshold: "Порог тока",
      measured_current: "Измеренный ток",
      unavailable: "недоступен",
      refresh: "Обновить",
      required_name: "Введите название режима",
      required_current: "Введите корректный ток",
    };
    const en = {
      add: "Add",
      edit: "Edit",
      delete: "Delete",
      cancel: "Cancel",
      save: "Save",
      add_mode: "Add mode",
      edit_mode: "Edit mode",
      mode_name: "Mode name",
      current_threshold: "Current threshold",
      measured_current: "Measured current",
      unavailable: "unavailable",
      refresh: "Refresh",
      required_name: "Enter a mode name",
      required_current: "Enter a valid current",
    };
    return (this._isRu() ? ru : en)[key];
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  _currentSensor() {
    try {
      const selectorHost = this.getRootNode()?.host;
      const formHost = selectorHost?.getRootNode?.()?.host;
      const fromForm = formHost?.data?.current_sensor;
      if (fromForm) return String(fromForm);
    } catch (_) {}
    return String(this._selector?.smart_plug_modes?.current_sensor || "");
  }

  _measuredCurrent() {
    const entityId = this._currentSensor();
    const state = entityId ? this._hass?.states?.[entityId] : undefined;
    if (!state || ["unknown", "unavailable"].includes(state.state)) return null;
    const value = Number(state.state);
    return Number.isFinite(value) ? value : null;
  }

  _formatCurrent(value) {
    if (value === null) return `${this._t("measured_current")}: ${this._t("unavailable")}`;
    return `${this._t("measured_current")}: ${value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "")} A`;
  }

  _emitValue(value) {
    this._value = value;
    this.dispatchEvent(
      new CustomEvent("value-changed", {
        detail: { value },
        bubbles: true,
        composed: true,
      })
    );
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._selector || this._dialog) return;

    const items = this._value
      .map(
        (item, index) => `
          <div class="item">
            <div class="item-text">
              <div class="item-name">${this._escape(item?.name)}</div>
              <div class="item-current">${this._escape(item?.current)} A</div>
            </div>
            <div class="item-actions">
              <ha-button class="edit" data-index="${index}" appearance="plain" ${this._disabled ? "disabled" : ""}>${this._t("edit")}</ha-button>
              <ha-button class="delete" data-index="${index}" appearance="plain" ${this._disabled ? "disabled" : ""}>${this._t("delete")}</ha-button>
            </div>
          </div>`
      )
      .join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:block; }
        .label { font-size:14px; font-weight:500; margin-bottom:8px; }
        .list { display:flex; flex-direction:column; gap:8px; margin-bottom:12px; }
        .item { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:10px 12px; border:1px solid var(--divider-color); border-radius:12px; }
        .item-text { min-width:0; }
        .item-name { font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .item-current { color:var(--secondary-text-color); font-size:13px; margin-top:2px; }
        .item-actions { display:flex; gap:2px; flex-shrink:0; }
        .helper { color:var(--secondary-text-color); font-size:12px; margin-top:8px; line-height:1.4; }
      </style>
      <div class="label">${this._escape(this._label)}</div>
      <div class="list">${items}</div>
      <ha-button class="add" ${this._disabled ? "disabled" : ""}>${this._t("add")}</ha-button>
      ${this._helper ? `<div class="helper">${this._escape(this._helper)}</div>` : ""}
    `;

    this.shadowRoot.querySelector(".add")?.addEventListener("click", () => this._openEditor(null));
    for (const button of this.shadowRoot.querySelectorAll(".edit")) {
      button.addEventListener("click", () => this._openEditor(Number(button.dataset.index)));
    }
    for (const button of this.shadowRoot.querySelectorAll(".delete")) {
      button.addEventListener("click", () => {
        const index = Number(button.dataset.index);
        const next = this._value.slice();
        next.splice(index, 1);
        this._emitValue(next);
      });
    }
  }

  _openEditor(index) {
    if (this._disabled || this._dialog) return;

    const editing = index !== null;
    const existing = editing ? this._value[index] || {} : {};
    const dialog = document.createElement("ha-dialog");
    dialog.setAttribute("header-title", editing ? this._t("edit_mode") : this._t("add_mode"));
    dialog.setAttribute("prevent-scrim-close", "");

    const body = document.createElement("div");
    body.innerHTML = `
      <style>
        .editor { display:flex; flex-direction:column; gap:20px; min-width:0; }
        .threshold-header { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:6px; }
        .threshold-label { font-size:14px; font-weight:500; }
        .measured { display:flex; align-items:center; justify-content:flex-end; gap:8px; color:var(--secondary-text-color); font-size:13px; text-align:right; }
        .current-wrap { display:grid; grid-template-columns:minmax(0,1fr) auto; align-items:center; gap:8px; }
        .unit { color:var(--secondary-text-color); }
        .error { min-height:18px; color:var(--error-color); font-size:12px; }
      </style>
      <div class="editor">
        <ha-textfield class="name" label="${this._escape(this._t("mode_name"))}" required></ha-textfield>
        <div>
          <div class="threshold-header">
            <div class="threshold-label">${this._escape(this._t("current_threshold"))}</div>
            <div class="measured">
              <span class="measured-value"></span>
              <ha-button class="refresh" appearance="plain">${this._escape(this._t("refresh"))}</ha-button>
            </div>
          </div>
          <div class="current-wrap">
            <ha-textfield class="current" type="number" min="0" step="0.001" required></ha-textfield>
            <span class="unit">A</span>
          </div>
        </div>
        <div class="error"></div>
      </div>
    `;

    const footer = document.createElement("ha-dialog-footer");
    footer.slot = "footer";
    footer.innerHTML = `
      <ha-button class="cancel" appearance="plain" slot="secondaryAction">${this._escape(this._t("cancel"))}</ha-button>
      <ha-button class="save" slot="primaryAction">${this._escape(editing ? this._t("save") : this._t("add"))}</ha-button>
    `;

    dialog.append(body, footer);
    this.shadowRoot.append(dialog);
    this._dialog = dialog;

    const nameInput = body.querySelector(".name");
    const currentInput = body.querySelector(".current");
    const measuredNode = body.querySelector(".measured-value");
    const errorNode = body.querySelector(".error");

    nameInput.value = existing.name ?? "";
    currentInput.value = existing.current ?? "";

    const refreshMeasured = () => {
      measuredNode.textContent = this._formatCurrent(this._measuredCurrent());
    };
    refreshMeasured();

    body.querySelector(".refresh")?.addEventListener("click", (event) => {
      event.preventDefault();
      refreshMeasured();
    });

    const close = () => {
      dialog.open = false;
    };

    footer.querySelector(".cancel")?.addEventListener("click", close);
    footer.querySelector(".save")?.addEventListener("click", () => {
      const name = String(nameInput.value || "").trim();
      const current = Number(currentInput.value);
      if (!name) {
        errorNode.textContent = this._t("required_name");
        nameInput.focus();
        return;
      }
      if (!Number.isFinite(current) || current < 0) {
        errorNode.textContent = this._t("required_current");
        currentInput.focus();
        return;
      }

      const next = this._value.slice();
      const item = { name, current };
      if (editing) next[index] = item;
      else next.push(item);
      next.sort((a, b) => Number(a.current) - Number(b.current));
      this._emitValue(next);
      close();
    });

    dialog.addEventListener("closed", () => {
      dialog.remove();
      if (this._dialog === dialog) this._dialog = null;
      this._render();
    });

    dialog.open = true;
    requestAnimationFrame(() => nameInput.focus());
  }

  reportValidity() {
    return Array.isArray(this._value) && this._value.length > 0;
  }
}

if (!customElements.get("ha-selector-smart_plug_modes")) {
  customElements.define("ha-selector-smart_plug_modes", SmartPlugModesSelector);
}
