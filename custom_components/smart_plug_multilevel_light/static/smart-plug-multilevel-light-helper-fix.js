(() => {
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

  const toText = (value, seen = new Set()) => {
    if (value == null || value === false) return "";
    if (typeof value === "string" || typeof value === "number") return String(value);
    if (Array.isArray(value)) return value.map((item) => toText(item, seen)).join("");
    if (typeof value !== "object" || seen.has(value)) return "";
    seen.add(value);

    // Lit TemplateResult: interleave static strings with rendered values.
    if (Array.isArray(value.strings)) {
      const values = Array.isArray(value.values) ? value.values : [];
      return value.strings
        .map((part, index) => String(part) + (index < values.length ? toText(values[index], seen) : ""))
        .join("")
        .replace(/<[^>]+>/g, "")
        .trim();
    }

    for (const key of ["text", "content", "message", "value"]) {
      if (key in value) {
        const text = toText(value[key], seen).trim();
        if (text) return text;
      }
    }

    // Last-resort search for the actual translated string inside wrapper objects.
    for (const nested of Object.values(value)) {
      const text = toText(nested, seen).trim();
      if (text && text !== "[object Object]") return text;
    }
    return "";
  };

  const patchSelector = (selector) => {
    if (!selector?.shadowRoot || !isModesSelector(selector)) return;
    const helper = selector.shadowRoot.querySelector(".spml-modes-helper");
    if (!helper) return;
    const text = toText(selector.helper).trim();
    if (text) helper.textContent = text;
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

    // config-v2 creates the helper and may write the raw helper object during every
    // Lit update. Run this normalizer after that update so [object Object] can never
    // overwrite the visible description again.
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