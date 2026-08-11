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

  const getModesHelperText = (selector) => {
    const localize = selector?.hass?.localize?.bind(selector.hass);
    if (!localize) return "";
    return (
      localize(`component.${DOMAIN}.options.step.init.data_description.modes`) ||
      localize(`component.${DOMAIN}.config.step.settings.data_description.modes`) ||
      ""
    );
  };

  const formHostForSelector = (selector) => {
    try {
      const selectorHost = selector.getRootNode()?.host;
      return selectorHost?.getRootNode?.()?.host || null;
    } catch (_) {
      return null;
    }
  };

  const formRootForSelector = (selector) => {
    try {
      const selectorHost = selector.getRootNode()?.host;
      return selectorHost?.getRootNode?.() || null;
    } catch (_) {
      return null;
    }
  };

  const formatNumber = (value) =>
    Number(value).toFixed(2).replace(/0+$/, "").replace(/\.$/, "");

  const brightnessForPower = (power, maxPower, roundTo5) => {
    if (!(maxPower > 0)) return 100;
    const ratio = Math.max(0, Math.min(1, power / maxPower));
    const estimated = ratio * 100;
    if (roundTo5) {
      return Math.max(5, Math.min(100, 5 * Math.floor(estimated / 5 + 0.5)));
    }
    return Math.max(1, Math.min(100, Math.floor(estimated + 0.5)));
  };

  const alignHelperTexts = (root) => {
    if (!root?.querySelectorAll) return;

    for (const helper of root.querySelectorAll("ha-input-helper-text")) {
      helper.style.paddingLeft = "0";
      helper.style.paddingInlineStart = "0";
    }

    for (const element of root.querySelectorAll("*")) {
      if (element.shadowRoot) alignHelperTexts(element.shadowRoot);
    }
  };

  const decorateModeRows = (selector) => {
    const root = selector?.shadowRoot;
    const modes = Array.isArray(selector?.value) ? selector.value : [];
    if (!root || !modes.length) return;

    const descriptions = [...root.querySelectorAll(".description")];
    if (!descriptions.length) return;

    const powers = modes.map((mode) => Number(mode?.power));
    const validPowers = powers.filter(Number.isFinite);
    if (!validPowers.length) return;

    const maxPower = Math.max(...validPowers);
    const roundTo5 = Boolean(formHostForSelector(selector)?.data?.round_brightness_to_5);

    descriptions.forEach((description, index) => {
      const power = powers[index];
      if (!Number.isFinite(power)) return;
      const pct = brightnessForPower(power, maxPower, roundTo5);
      const nextText = `${formatNumber(power)} W · ${pct}%`;
      if (description.textContent !== nextText) description.textContent = nextText;
    });
  };

  const patchDebugMeasures = (selector) => {
    const debug = selector?.shadowRoot?.querySelector?.(".spml-debug-measures");
    if (!debug) return;
    const text = String(debug.textContent || "").trim();
    if (text && !text.endsWith(" W")) debug.textContent = `${text} W`;
  };

  const patchSelector = (selector) => {
    if (!selector?.shadowRoot || !isModesSelector(selector)) return;

    const text = getModesHelperText(selector);
    if (!text) return;

    const root = selector.shadowRoot;
    const label = root.querySelector("label");
    const container = root.querySelector(".items-container");
    if (!container) return;

    let helper = root.querySelector(".spml-modes-helper");

    if (helper && helper.tagName?.toLowerCase() !== "div") {
      const replacement = document.createElement("div");
      replacement.className = "spml-modes-helper";
      helper.replaceWith(replacement);
      helper = replacement;
    }

    if (!helper) {
      helper = document.createElement("div");
      helper.className = "spml-modes-helper";
    }

    if (helper.textContent !== text) helper.textContent = text;
    helper.style.cssText = [
      "display:block",
      "margin:0 0 16px 0",
      "padding:0",
      "color:var(--secondary-text-color)",
      "font-size:12px",
      "line-height:1.45",
      "text-align:start",
      "max-width:100%"
    ].join(";");

    if (label) label.insertAdjacentElement("afterend", helper);
    else container.insertAdjacentElement("beforebegin", helper);

    const addMeasuresRow = root.querySelector(".spml-add-measures-row");
    if (addMeasuresRow) addMeasuresRow.style.marginBottom = "16px";

    alignHelperTexts(formRootForSelector(selector));
    decorateModeRows(selector);
    patchDebugMeasures(selector);
  };

  const walk = (root) => {
    if (!root?.querySelectorAll) return;
    for (const selector of root.querySelectorAll("ha-selector-object")) patchSelector(selector);
    for (const element of root.querySelectorAll("*")) {
      if (element.shadowRoot) walk(element.shadowRoot);
    }
  };

  let refreshQueued = false;
  const refresh = () => {
    if (refreshQueued) return;
    refreshQueued = true;
    queueMicrotask(() => {
      refreshQueued = false;
      walk(document);
    });
  };

  const observer = new MutationObserver(refresh);
  observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true });

  customElements.whenDefined("ha-selector-object").then(() => {
    const ctor = customElements.get("ha-selector-object");
    const proto = ctor?.prototype;

    if (proto && !proto.__spmlHelperTextPatched) {
      const previousUpdated = proto.updated;
      proto.updated = function (...args) {
        const result = previousUpdated?.apply(this, args);
        queueMicrotask(() => patchSelector(this));
        return result;
      };
      proto.__spmlHelperTextPatched = true;
    }

    refresh();
    setTimeout(refresh, 100);
    setTimeout(refresh, 500);
    setTimeout(refresh, 1500);
  });
})();