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

  const getModesHelperText = (selector) => {
    const localize = selector?.hass?.localize?.bind(selector.hass);
    if (!localize) return "";

    // Options/config-flow translations are already loaded by Home Assistant before
    // the form is rendered. Read the translated string directly instead of trying
    // to stringify selector.helper, which is a Lit TemplateResult for data_description.
    return (
      localize(`component.${DOMAIN}.options.step.init.data_description.modes`) ||
      localize(`component.${DOMAIN}.config.step.settings.data_description.modes`) ||
      ""
    );
  };

  const patchSelector = (selector) => {
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

  const walk = (root) => {
    if (!root?.querySelectorAll) return;
    for (const selector of root.querySelectorAll("ha-selector-object")) patchSelector(selector);
    for (const element of root.querySelectorAll("*")) {
      if (element.shadowRoot) walk(element.shadowRoot);
    }
  };

  const refresh = () => walk(document);
  const observer = new MutationObserver(() => queueMicrotask(refresh));
  observer.observe(document.documentElement, { childList: true, subtree: true });

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