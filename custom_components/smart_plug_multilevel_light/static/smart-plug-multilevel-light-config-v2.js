(() => {
  const DOMAIN = "smart_plug_multilevel_light";

  const isModesSelector = (selector) => {
    const object = selector?.selector?.object;
    return Boolean(
      object?.multiple &&
      object?.label_field === "name" &&
      object?.description_field === "current" &&
      object?.fields?.name &&
      object?.fields?.current
    );
  };

  const findCurrentSensor = (selector) => {
    try {
      const selectorHost = selector.getRootNode()?.host;
      const formHost = selectorHost?.getRootNode?.()?.host;
      return String(formHost?.data?.current_sensor || "");
    } catch (_) {
      return "";
    }
  };

  const stateToAmps = (state) => {
    if (!state || ["unknown", "unavailable"].includes(state.state)) return null;
    const numeric = Number(state.state);
    if (!Number.isFinite(numeric)) return null;
    const unit = String(state.attributes?.unit_of_measurement || "A").trim();
    if (unit === "mA") return numeric / 1000;
    if (unit === "µA" || unit === "uA") return numeric / 1000000;
    if (unit === "kA") return numeric * 1000;
    return numeric;
  };

  const custom = (selector, key, fallback = key) => {
    const value = window.SPML_I18N?.t(selector.hass, key);
    return !value || value === key ? fallback : value;
  };

  const common = (selector, key, fallback) =>
    window.SPML_I18N?.common(selector.hass, key, fallback) ??
    selector.hass?.localize?.(key) ??
    fallback;

  const unavailableText = (selector) =>
    selector.hass?.localize?.("state.default.unavailable") ||
    selector.hass?.localize?.("ui.common.unavailable") ||
    "unavailable";

  const modeNameHelp = (selector) => {
    const language = String(selector.hass?.language || "en").toLowerCase();
    return language.startsWith("ru")
      ? "Например: High, Medium, Low или Dim."
      : "For example: High, Medium, Low, or Dim.";
  };

  const thresholdHelp = (selector) => {
    const text = custom(
      selector,
      "threshold_help",
      "We recommend setting the threshold about 15% below the measured current because lamp consumption can vary slightly between measurements."
    );
    return text
      .replace(/10\s?%/g, "15%")
      .replace(/۱۰\s?٪/g, "۱۵٪")
      .replace(/١٠\s?٪/g, "١٥٪")
      .replace(/१०\s?%/g, "१५%")
      .replace(/১০\s?%/g, "১৫%")
      .replace(/๑๐\s?%/g, "๑๕%");
  };

  const measuredActionText = (selector) =>
    `${common(selector, "ui.common.apply", "Apply")} ${custom(selector, "measured_current", "measured current")} −15%`;

  const getModesHelperText = (selector) => {
    const localize = selector?.hass?.localize?.bind(selector.hass);
    if (!localize) return "";
    return (
      localize(`component.${DOMAIN}.options.step.init.data_description.modes`) ||
      localize(`component.${DOMAIN}.config.step.settings.data_description.modes`) ||
      ""
    );
  };

  const ensureModesHelper = (selector) => {
    if (!selector?.shadowRoot || !isModesSelector(selector)) return;

    const text = getModesHelperText(selector);
    if (!text) return;

    let helper = selector.shadowRoot.querySelector(".spml-modes-helper");
    if (!helper) {
      helper = document.createElement("ha-input-helper-text");
      helper.className = "spml-modes-helper";
      const container = selector.shadowRoot.querySelector(".items-container");
      if (container) container.insertAdjacentElement("afterend", helper);
      else selector.shadowRoot.append(helper);
    }
    helper.textContent = text;
  };

  const walkShadowRoots = (root, callback) => {
    if (!root?.querySelectorAll) return;
    for (const selector of root.querySelectorAll("ha-selector-object")) callback(selector);
    for (const element of root.querySelectorAll("*")) {
      if (element.shadowRoot) walkShadowRoots(element.shadowRoot, callback);
    }
  };

  const refreshModesHelpers = () => walkShadowRoots(document, ensureModesHelper);

  customElements.whenDefined("ha-selector-object").then(() => {
    const ctor = customElements.get("ha-selector-object");
    const proto = ctor?.prototype;
    if (proto && !proto.__spmlHelperPatched) {
      const originalUpdated = proto.updated;
      proto.updated = function (...args) {
        const result = originalUpdated?.apply(this, args);
        queueMicrotask(() => ensureModesHelper(this));
        return result;
      };
      proto.__spmlHelperPatched = true;
    }
    refreshModesHelpers();
    setTimeout(refreshModesHelpers, 100);
    setTimeout(refreshModesHelpers, 500);
    setTimeout(refreshModesHelpers, 1500);
  });

  const openEditor = (selector, index = null) => {
    const editing = index !== null;
    const existing = editing && Array.isArray(selector.value) ? selector.value[index] || {} : {};
    const dialog = document.createElement("ha-dialog");
    dialog.setAttribute(
      "header-title",
      common(selector, editing ? "ui.common.edit" : "ui.common.add", editing ? "Edit" : "Add")
    );
    dialog.setAttribute("prevent-scrim-close", "");

    const body = document.createElement("div");
    body.innerHTML = `
      <style>
        .spml-editor{display:flex;flex-direction:column;gap:24px;min-width:0}
        .spml-field{display:flex;flex-direction:column;gap:8px}
        .spml-label{font-size:14px;font-weight:500;color:var(--primary-text-color)}
        .spml-label.spml-invalid{color:var(--error-color)}
        .spml-threshold-head{display:flex;align-items:center;justify-content:space-between;gap:16px}
        .spml-measured{color:var(--secondary-text-color);font-size:14px;text-align:right}
        .spml-input-wrap{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:10px}
        .spml-input{box-sizing:border-box;width:100%;min-height:56px;padding:0 16px;border:1px solid var(--outline-color,var(--divider-color));border-radius:12px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit;font-size:16px;outline:none}
        .spml-input:focus{border:2px solid var(--primary-color);padding:0 15px}
        .spml-unit{color:var(--secondary-text-color);font-size:16px}
        .spml-helper{color:var(--secondary-text-color);font-size:12px;line-height:1.45}
        .spml-inline-action{border:0;background:transparent;padding:0;margin:0;color:var(--primary-color);font:inherit;font-size:12px;font-weight:500;cursor:pointer;text-decoration:underline;text-underline-offset:2px}
        .spml-inline-action:disabled{opacity:.5;cursor:default}
      </style>
      <div class="spml-editor">
        <div class="spml-field">
          <label class="spml-label spml-name-label" for="spml-name">${common(selector, "ui.common.name", "Name")}</label>
          <input id="spml-name" class="spml-input spml-name" type="text" required autocomplete="off" />
          <div class="spml-helper">${modeNameHelp(selector)}</div>
        </div>
        <div class="spml-field">
          <div class="spml-threshold-head">
            <label class="spml-label spml-current-label" for="spml-current">${custom(selector, "current_threshold", "Current threshold")}</label>
            <span class="spml-measured"></span>
          </div>
          <div class="spml-input-wrap">
            <input id="spml-current" class="spml-input spml-current" type="number" min="0" step="0.001" required inputmode="decimal" />
            <span class="spml-unit">A</span>
          </div>
          <div class="spml-helper">${thresholdHelp(selector)} <button type="button" class="spml-inline-action">${measuredActionText(selector)}</button></div>
        </div>
      </div>`;

    const footer = document.createElement("ha-dialog-footer");
    footer.slot = "footer";
    footer.innerHTML = `
      <ha-button class="spml-cancel" appearance="plain" slot="secondaryAction">${common(selector, "ui.common.cancel", "Cancel")}</ha-button>
      <ha-button class="spml-save" slot="primaryAction">${common(selector, editing ? "ui.common.save" : "ui.common.add", editing ? "Save" : "Add")}</ha-button>`;

    dialog.append(body, footer);
    document.body.append(dialog);

    const nameInput = body.querySelector(".spml-name");
    const currentInput = body.querySelector(".spml-current");
    const nameLabel = body.querySelector(".spml-name-label");
    const currentLabel = body.querySelector(".spml-current-label");
    const measured = body.querySelector(".spml-measured");
    const applyMeasured = body.querySelector(".spml-inline-action");
    nameInput.value = existing.name ?? "";
    currentInput.value = existing.current ?? "";

    const clearInvalid = (label) => label?.classList.remove("spml-invalid");
    const markInvalid = (label) => label?.classList.add("spml-invalid");

    nameInput.addEventListener("input", () => clearInvalid(nameLabel));
    currentInput.addEventListener("input", () => clearInvalid(currentLabel));

    const entityId = findCurrentSensor(selector);
    let measuredValue = null;
    let unsubscribe = null;
    let closed = false;

    const renderMeasured = (state) => {
      measuredValue = stateToAmps(state);
      applyMeasured.disabled = measuredValue === null;
      measured.textContent = measuredValue === null
        ? `${custom(selector, "measured_current", "Measured current")}: ${unavailableText(selector)}`
        : `${custom(selector, "measured_current", "Measured current")}: ${measuredValue.toFixed(3).replace(/0+$/, "").replace(/\.$/, "")} A`;
    };

    renderMeasured(entityId ? selector.hass?.states?.[entityId] : undefined);
    if (entityId && selector.hass?.connection?.subscribeEvents) {
      selector.hass.connection.subscribeEvents((event) => {
        if (event?.data?.entity_id === entityId) renderMeasured(event.data.new_state);
      }, "state_changed").then((unsub) => {
        if (closed) {
          try { unsub(); } catch (_) {}
          return;
        }
        unsubscribe = unsub;
      }).catch(() => {});
    }

    applyMeasured.addEventListener("click", () => {
      if (measuredValue === null) return;
      currentInput.value = String(Number((measuredValue * 0.85).toFixed(3)));
      currentInput.dispatchEvent(new Event("input", { bubbles: true }));
      currentInput.focus();
      currentInput.select();
    });

    const close = () => { dialog.open = false; };
    footer.querySelector(".spml-cancel")?.addEventListener("click", close);

    const save = () => {
      clearInvalid(nameLabel);
      clearInvalid(currentLabel);

      const name = String(nameInput.value || "").trim();
      const current = Number(currentInput.value);
      const nameValid = Boolean(name) && nameInput.checkValidity();
      const currentValid = currentInput.checkValidity() && Number.isFinite(current);

      const invalidInputs = [];
      if (!nameValid) {
        markInvalid(nameLabel);
        invalidInputs.push(nameInput);
      }
      if (!currentValid) {
        markInvalid(currentLabel);
        invalidInputs.push(currentInput);
      }
      if (invalidInputs.length) {
        invalidInputs[0].focus();
        return;
      }

      const next = Array.isArray(selector.value) ? selector.value.slice() : [];
      const item = { name, current };
      if (editing) next[index] = item; else next.push(item);
      next.sort((a, b) => Number(a.current) - Number(b.current));
      selector.dispatchEvent(new CustomEvent("value-changed", { detail: { value: next }, bubbles: true, composed: true }));
      close();
    };

    footer.querySelector(".spml-save")?.addEventListener("click", save);
    body.addEventListener("keydown", (event) => {
      if (event.key === "Enter") { event.preventDefault(); save(); }
    });
    dialog.addEventListener("closed", () => {
      closed = true;
      try { unsubscribe?.(); } catch (_) {}
      dialog.remove();
    }, { once: true });
    dialog.open = true;
    requestAnimationFrame(() => nameInput.focus());
  };

  document.addEventListener("click", (event) => {
    const path = event.composedPath?.() || [];
    const selector = path.find((node) => node?.tagName?.toLowerCase?.() === "ha-selector-object");
    if (!selector || !isModesSelector(selector)) return;

    const button = path.find((node) => node?.tagName?.toLowerCase?.() === "ha-button");
    const iconButton = path.find((node) => node?.tagName?.toLowerCase?.() === "ha-icon-button");
    if (!button && !iconButton) return;

    if (iconButton && iconButton.item === undefined) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    if (iconButton && Number.isInteger(Number(iconButton.index))) {
      openEditor(selector, Number(iconButton.index));
    } else if (button) {
      openEditor(selector, null);
    }
  }, true);
})();