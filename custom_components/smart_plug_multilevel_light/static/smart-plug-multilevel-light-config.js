(() => {
  const TARGET_NAME_FIELD = "name";
  const TARGET_CURRENT_FIELD = "current";

  const isRu = (hass) =>
    String(hass?.language || "").toLowerCase().startsWith("ru");

  const text = (hass, key) => {
    const ru = {
      add_mode: "Добавить режим",
      edit_mode: "Изменить режим",
      mode_name: "Название режима",
      current_threshold: "Порог тока",
      measured_current: "Измеренный ток",
      unavailable: "недоступен",
      refresh: "Обновить",
      cancel: "Отмена",
      add: "Добавить",
      save: "Сохранить",
      required_name: "Введите название режима",
      required_current: "Введите корректный ток",
    };
    const en = {
      add_mode: "Add mode",
      edit_mode: "Edit mode",
      mode_name: "Mode name",
      current_threshold: "Current threshold",
      measured_current: "Measured current",
      unavailable: "unavailable",
      refresh: "Refresh",
      cancel: "Cancel",
      add: "Add",
      save: "Save",
      required_name: "Enter a mode name",
      required_current: "Enter a valid current",
    };
    return (isRu(hass) ? ru : en)[key];
  };

  const isOurModesSelector = (element) => {
    const object = element?.selector?.object;
    const fields = object?.fields;
    if (!object || !fields) return false;

    return (
      object.multiple === true &&
      object.label_field === TARGET_NAME_FIELD &&
      object.description_field === TARGET_CURRENT_FIELD &&
      fields[TARGET_NAME_FIELD]?.selector?.text !== undefined &&
      fields[TARGET_CURRENT_FIELD]?.selector?.number?.unit_of_measurement === "A"
    );
  };

  const currentSensorFromForm = (element) => {
    try {
      const haSelector = element.getRootNode()?.host;
      const haForm = haSelector?.getRootNode?.()?.host;
      const entityId = haForm?.data?.current_sensor;
      return entityId ? String(entityId) : "";
    } catch (_) {
      return "";
    }
  };

  const measuredCurrentAmps = (element) => {
    const entityId = currentSensorFromForm(element);
    const state = entityId ? element.hass?.states?.[entityId] : undefined;
    if (!state || ["unknown", "unavailable"].includes(state.state)) return null;

    const raw = Number(state.state);
    if (!Number.isFinite(raw)) return null;

    const unit = String(state.attributes?.unit_of_measurement || "A").trim();
    if (unit === "mA") return raw / 1000;
    if (unit === "µA" || unit === "μA" || unit === "uA") return raw / 1_000_000;
    if (unit === "kA") return raw * 1000;
    return raw;
  };

  const formatCurrent = (element, value) => {
    if (value === null) {
      return `${text(element.hass, "measured_current")}: ${text(
        element.hass,
        "unavailable"
      )}`;
    }

    const formatted = value
      .toFixed(3)
      .replace(/0+$/, "")
      .replace(/\.$/, "");
    return `${text(element.hass, "measured_current")}: ${formatted} A`;
  };

  const emitValue = (element, value) => {
    element.dispatchEvent(
      new CustomEvent("value-changed", {
        detail: { value },
        bubbles: true,
        composed: true,
      })
    );
  };

  const openEditor = (element, { item = null, index = null } = {}) => {
    const editing = index !== null;
    const hass = element.hass;

    const dialog = document.createElement("ha-dialog");
    dialog.setAttribute(
      "header-title",
      text(hass, editing ? "edit_mode" : "add_mode")
    );
    dialog.setAttribute("prevent-scrim-close", "");

    const body = document.createElement("div");
    body.innerHTML = `
      <style>
        .spml-editor {
          display: flex;
          flex-direction: column;
          gap: 22px;
          min-width: 0;
        }
        .spml-field-label {
          font-size: 14px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .spml-threshold-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          margin-bottom: 8px;
        }
        .spml-measured {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 8px;
          min-width: 0;
          color: var(--secondary-text-color);
          font-size: 13px;
          text-align: right;
        }
        .spml-current-row {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          align-items: center;
          gap: 8px;
        }
        .spml-unit {
          color: var(--secondary-text-color);
        }
        .spml-error {
          min-height: 18px;
          color: var(--error-color);
          font-size: 12px;
          line-height: 18px;
        }
        @media (max-width: 450px) {
          .spml-threshold-header {
            align-items: flex-start;
            flex-direction: column;
            gap: 4px;
          }
          .spml-measured {
            width: 100%;
            justify-content: flex-end;
          }
        }
      </style>
      <div class="spml-editor">
        <ha-textfield class="spml-name" label="${text(hass, "mode_name")}" required></ha-textfield>
        <div>
          <div class="spml-threshold-header">
            <div class="spml-field-label">${text(hass, "current_threshold")}</div>
            <div class="spml-measured">
              <span class="spml-measured-value"></span>
              <ha-button class="spml-refresh" appearance="plain">${text(
                hass,
                "refresh"
              )}</ha-button>
            </div>
          </div>
          <div class="spml-current-row">
            <ha-textfield class="spml-current" type="number" min="0" max="100" step="0.001" required></ha-textfield>
            <span class="spml-unit">A</span>
          </div>
        </div>
        <div class="spml-error"></div>
      </div>
    `;

    const footer = document.createElement("ha-dialog-footer");
    footer.slot = "footer";
    footer.innerHTML = `
      <ha-button class="spml-cancel" appearance="plain" slot="secondaryAction">${text(
        hass,
        "cancel"
      )}</ha-button>
      <ha-button class="spml-submit" slot="primaryAction">${text(
        hass,
        editing ? "save" : "add"
      )}</ha-button>
    `;

    dialog.append(body, footer);
    document.body.append(dialog);

    const nameInput = body.querySelector(".spml-name");
    const currentInput = body.querySelector(".spml-current");
    const measuredNode = body.querySelector(".spml-measured-value");
    const errorNode = body.querySelector(".spml-error");

    nameInput.value = item?.[TARGET_NAME_FIELD] ?? "";
    currentInput.value = item?.[TARGET_CURRENT_FIELD] ?? "";

    const refreshMeasured = () => {
      measuredNode.textContent = formatCurrent(element, measuredCurrentAmps(element));
    };
    refreshMeasured();

    body.querySelector(".spml-refresh")?.addEventListener("click", (event) => {
      event.preventDefault();
      refreshMeasured();
    });

    const close = () => {
      dialog.open = false;
    };

    footer.querySelector(".spml-cancel")?.addEventListener("click", close);
    footer.querySelector(".spml-submit")?.addEventListener("click", () => {
      const name = String(nameInput.value || "").trim();
      const current = Number(currentInput.value);

      if (!name) {
        errorNode.textContent = text(hass, "required_name");
        nameInput.focus();
        return;
      }
      if (!Number.isFinite(current) || current < 0 || current > 100) {
        errorNode.textContent = text(hass, "required_current");
        currentInput.focus();
        return;
      }

      const next = Array.isArray(element.value) ? element.value.slice() : [];
      const updated = {
        [TARGET_NAME_FIELD]: name,
        [TARGET_CURRENT_FIELD]: current,
      };

      if (editing) next[index] = updated;
      else next.push(updated);

      next.sort(
        (a, b) =>
          Number(a?.[TARGET_CURRENT_FIELD]) - Number(b?.[TARGET_CURRENT_FIELD])
      );
      emitValue(element, next);
      close();
    });

    dialog.addEventListener("closed", () => dialog.remove(), { once: true });
    dialog.open = true;
    requestAnimationFrame(() => nameInput.focus());
  };

  customElements.whenDefined("ha-selector-object").then(() => {
    const ObjectSelector = customElements.get("ha-selector-object");
    if (!ObjectSelector || ObjectSelector.prototype.__spmlEnhanced) return;

    const originalAdd = ObjectSelector.prototype._addItem;
    const originalEdit = ObjectSelector.prototype._editItem;

    ObjectSelector.prototype._addItem = function (event) {
      if (!isOurModesSelector(this)) {
        return originalAdd.call(this, event);
      }
      event.stopPropagation();
      openEditor(this);
    };

    ObjectSelector.prototype._editItem = function (event) {
      if (!isOurModesSelector(this)) {
        return originalEdit.call(this, event);
      }
      event.stopPropagation();
      openEditor(this, {
        item: event.currentTarget.item,
        index: event.currentTarget.index,
      });
    };

    ObjectSelector.prototype.__spmlEnhanced = true;
  });
})();
