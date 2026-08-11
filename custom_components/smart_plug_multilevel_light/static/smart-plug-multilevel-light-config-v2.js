(() => {
  const DOMAIN = "smart_plug_multilevel_light";

  const isModesSelector = (selector) => {
    const object = selector?.selector?.object;
    return Boolean(
      object?.multiple &&
      object?.label_field === "name" &&
      object?.description_field === "power" &&
      object?.fields?.name &&
      object?.fields?.power
    );
  };

  const findFormData = (selector) => {
    try {
      const selectorHost = selector.getRootNode()?.host;
      const formHost = selectorHost?.getRootNode?.()?.host;
      return formHost?.data || {};
    } catch (_) {
      return {};
    }
  };

  const findPowerSensor = (selector) => String(findFormData(selector)?.power_sensor || "");

  const findSampleCount = (selector) => {
    const value = Number(findFormData(selector)?.power_history_samples ?? 5);
    if (!Number.isFinite(value)) return 5;
    return Math.max(1, Math.min(100, Math.round(value)));
  };

  const stateToWatts = (state) => {
    if (!state || ["unknown", "unavailable"].includes(state.state)) return null;
    const numeric = Number(state.state);
    if (!Number.isFinite(numeric)) return null;
    const unit = String(state.attributes?.unit_of_measurement || "W").trim();
    if (unit === "mW") return numeric / 1000;
    if (unit === "kW") return numeric * 1000;
    if (unit === "MW") return numeric * 1000000;
    return numeric;
  };

  const formatWatts = (value) =>
    Number(value).toFixed(2).replace(/0+$/, "").replace(/\.$/, "");

  const custom = (selector, key, fallback = key) => {
    const value = window.SPML_I18N?.t(selector.hass, key);
    return !value || value === key ? fallback : value;
  };

  const common = (selector, key, fallback) =>
    window.SPML_I18N?.common(selector.hass, key, fallback) ??
    selector.hass?.localize?.(key) ??
    fallback;

  const modeNameHelp = (selector) =>
    custom(selector, "mode_name_help", "For example: High, Medium, Low, or Dim.");

  const getModesHelperText = (selector) => {
    const localize = selector?.hass?.localize?.bind(selector.hass);
    if (!localize) return "";
    return (
      localize(`component.${DOMAIN}.options.step.init.data_description.modes`) ||
      localize(`component.${DOMAIN}.config.step.settings.data_description.modes`) ||
      ""
    );
  };

  const renderDebugSamples = (selector) => {
    if (!selector?.shadowRoot || !isModesSelector(selector)) return;
    const debug = selector.shadowRoot.querySelector(".spml-debug-measures");
    if (!debug) return;

    const entityId = findPowerSensor(selector);
    const value = stateToWatts(entityId ? selector.hass?.states?.[entityId] : undefined);
    const maxItems = findSampleCount(selector);
    const samples = Array.isArray(selector.__spmlDebugSamples)
      ? selector.__spmlDebugSamples
      : [];
    samples.push(value === null ? "—" : formatWatts(value));
    selector.__spmlDebugSamples = samples.slice(-maxItems);
    debug.textContent = `${custom(selector, "last_measures_debug", "Last measures (debug)")}: [${selector.__spmlDebugSamples.join(", ")}]`;
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

    let debug = selector.shadowRoot.querySelector(".spml-debug-measures");
    if (!debug) {
      debug = document.createElement("div");
      debug.className = "spml-debug-measures";
      debug.style.cssText = "margin-top:6px;color:var(--secondary-text-color);font-size:12px;line-height:1.45;";
      helper.insertAdjacentElement("afterend", debug);
    }

    if (!selector.__spmlDebugTimer) {
      selector.__spmlDebugSamples = [];
      renderDebugSamples(selector);
      selector.__spmlDebugTimer = setInterval(() => {
        if (!selector.isConnected) {
          clearInterval(selector.__spmlDebugTimer);
          selector.__spmlDebugTimer = null;
          return;
        }
        renderDebugSamples(selector);
      }, 1000);
    }
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
        .spml-current{color:var(--secondary-text-color);font-size:12px;text-align:right}
        .spml-input-wrap{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:10px}
        .spml-input{box-sizing:border-box;width:100%;min-height:56px;padding:0 16px;border:1px solid var(--outline-color,var(--divider-color));border-radius:12px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit;font-size:16px;outline:none}
        .spml-input:focus{border:2px solid var(--primary-color);padding:0 15px}
        .spml-unit{color:var(--secondary-text-color);font-size:16px}
        .spml-helper{color:var(--secondary-text-color);font-size:12px;line-height:1.45}
        .spml-test{display:flex;flex-wrap:wrap;align-items:center;gap:8px;color:var(--secondary-text-color);font-size:12px;line-height:1.45}
        .spml-inline-action{border:0;background:transparent;padding:0;margin:0;color:var(--primary-color);font:inherit;font-size:12px;font-weight:500;cursor:pointer;text-decoration:underline;text-underline-offset:2px}
        .spml-inline-action:disabled{opacity:.5;cursor:default}
        .spml-test-result{color:var(--primary-text-color);font-weight:500}
      </style>
      <div class="spml-editor">
        <div class="spml-field">
          <label class="spml-label spml-name-label" for="spml-name">${common(selector, "ui.common.name", "Name")}</label>
          <input id="spml-name" class="spml-input spml-name" type="text" required autocomplete="off" />
          <div class="spml-helper">${modeNameHelp(selector)}</div>
        </div>
        <div class="spml-field">
          <div class="spml-threshold-head">
            <label class="spml-label spml-power-label" for="spml-power">${custom(selector, "power_threshold", "Power threshold")}</label>
            <span class="spml-current"></span>
          </div>
          <div class="spml-input-wrap">
            <input id="spml-power" class="spml-input spml-power" type="number" min="0" step="0.1" required inputmode="decimal" />
            <span class="spml-unit">W</span>
          </div>
          <div class="spml-test">
            <span class="spml-test-status">${custom(selector, "stable_power_prompt", "Please enable the preset on your light fixture and press")}</span>
            <button type="button" class="spml-inline-action spml-test-action">${custom(selector, "test_stable_power", "Test stable power")}</button>
            <button type="button" class="spml-inline-action spml-apply" hidden>${common(selector, "ui.common.apply", "Apply")}</button>
            <button type="button" class="spml-inline-action spml-repeat" hidden>${custom(selector, "repeat_test", "Repeat test")}</button>
          </div>
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
    const powerInput = body.querySelector(".spml-power");
    const nameLabel = body.querySelector(".spml-name-label");
    const powerLabel = body.querySelector(".spml-power-label");
    const currentPower = body.querySelector(".spml-current");
    const testStatus = body.querySelector(".spml-test-status");
    const testAction = body.querySelector(".spml-test-action");
    const applyMeasured = body.querySelector(".spml-apply");
    const repeatTest = body.querySelector(".spml-repeat");
    nameInput.value = existing.name ?? "";
    powerInput.value = existing.power ?? "";

    const clearInvalid = (label) => label?.classList.remove("spml-invalid");
    const markInvalid = (label) => label?.classList.add("spml-invalid");

    nameInput.addEventListener("input", () => clearInvalid(nameLabel));
    powerInput.addEventListener("input", () => clearInvalid(powerLabel));

    const entityId = findPowerSensor(selector);
    let measuredValue = null;
    let closed = false;
    let testRun = 0;
    let unsubscribe = null;

    const renderCurrentPower = (state) => {
      const value = stateToWatts(state);
      currentPower.textContent = value === null
        ? `${custom(selector, "current_moment_power", "Current moment power")}: —`
        : `${custom(selector, "current_moment_power", "Current moment power")}: ${formatWatts(value)} W`;
    };

    renderCurrentPower(entityId ? selector.hass?.states?.[entityId] : undefined);
    if (entityId && selector.hass?.connection?.subscribeEvents) {
      selector.hass.connection.subscribeEvents((event) => {
        if (event?.data?.entity_id === entityId) renderCurrentPower(event.data.new_state);
      }, "state_changed").then((unsub) => {
        if (closed) {
          try { unsub(); } catch (_) {}
          return;
        }
        unsubscribe = unsub;
      }).catch(() => {});
    }

    const close = () => { dialog.open = false; };
    footer.querySelector(".spml-cancel")?.addEventListener("click", close);

    const save = () => {
      clearInvalid(nameLabel);
      clearInvalid(powerLabel);

      const name = String(nameInput.value || "").trim();
      const power = Number(powerInput.value);
      const nameValid = Boolean(name) && nameInput.checkValidity();
      const powerValid = powerInput.checkValidity() && Number.isFinite(power);

      const invalidInputs = [];
      if (!nameValid) {
        markInvalid(nameLabel);
        invalidInputs.push(nameInput);
      }
      if (!powerValid) {
        markInvalid(powerLabel);
        invalidInputs.push(powerInput);
      }
      if (invalidInputs.length) {
        invalidInputs[0].focus();
        return false;
      }

      const next = Array.isArray(selector.value) ? selector.value.slice() : [];
      const item = { name, power };
      if (editing) next[index] = item; else next.push(item);
      next.sort((a, b) => Number(a.power) - Number(b.power));
      selector.dispatchEvent(new CustomEvent("value-changed", { detail: { value: next }, bubbles: true, composed: true }));
      close();
      return true;
    };

    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    const runStablePowerTest = async () => {
      const run = ++testRun;
      measuredValue = null;
      testAction.disabled = true;
      testAction.hidden = true;
      applyMeasured.hidden = true;
      repeatTest.hidden = true;
      testStatus.classList.remove("spml-test-result");

      const samples = [];
      const sampleCount = findSampleCount(selector);
      let stableValue = null;
      while (!closed && run === testRun && samples.length < sampleCount) {
        const value = stateToWatts(entityId ? selector.hass?.states?.[entityId] : undefined);
        if (value !== null && value > 0) {
          if (stableValue === value) {
            samples.push(value);
          } else {
            stableValue = value;
            samples.length = 0;
            samples.push(value);
          }
        } else {
          stableValue = null;
          samples.length = 0;
        }

        const formattedSamples = samples.map(formatWatts).join(", ");
        testStatus.textContent = `${custom(selector, "testing_wait", "Testing, wait")} [${formattedSamples}]`;

        if (samples.length >= sampleCount) break;
        await sleep(1000);
      }
      if (closed || run !== testRun) return;

      if (!samples.length || stableValue === null) {
        testStatus.textContent = custom(selector, "power_test_unavailable", "Power measurement is unavailable. Check the light and repeat the test.");
        repeatTest.hidden = false;
        testAction.disabled = false;
        return;
      }

      measuredValue = stableValue;
      testStatus.classList.add("spml-test-result");
      testStatus.textContent = `${custom(selector, "measured_result", "Measured")}: ${formatWatts(measuredValue)} W`;
      applyMeasured.hidden = false;
      repeatTest.hidden = false;
      testAction.disabled = false;
    };

    testAction.addEventListener("click", runStablePowerTest);
    repeatTest.addEventListener("click", runStablePowerTest);
    applyMeasured.addEventListener("click", () => {
      if (measuredValue === null) return;
      powerInput.value = String(Number(measuredValue.toFixed(2)));
      powerInput.dispatchEvent(new Event("input", { bubbles: true }));
      save();
    });

    footer.querySelector(".spml-save")?.addEventListener("click", save);
    body.addEventListener("keydown", (event) => {
      if (event.key === "Enter") { event.preventDefault(); save(); }
    });
    dialog.addEventListener("closed", () => {
      closed = true;
      testRun += 1;
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
