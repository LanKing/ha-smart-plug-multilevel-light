class SmartPlugModesEnhancer {
  static enhance() {
    const selector = customElements.get("ha-selector-object");
    if (!selector || selector.prototype.__smartPlugModesEnhanced) return;

    const originalAdd = selector.prototype._addItem;
    const originalEdit = selector.prototype._editItem;

    const isOurSelector = (instance) => {
      const object = instance?.selector?.object;
      const fields = object?.fields;
      return Boolean(object?.multiple && fields?.name?.selector?.text !== undefined && fields?.current?.selector?.number?.unit_of_measurement === "A");
    };

    const findCurrentSensor = (instance) => {
      try {
        const selectorHost = instance.getRootNode()?.host;
        const formHost = selectorHost?.getRootNode?.()?.host;
        const value = formHost?.data?.current_sensor;
        return value ? String(value) : "";
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

    const currentInAmps = (instance) => {
      const entityId = findCurrentSensor(instance);
      return stateToAmps(entityId ? instance.hass?.states?.[entityId] : undefined);
    };

    const isRu = (instance) => String(instance.hass?.language || "").toLowerCase().startsWith("ru");
    const text = (instance, key) => {
      const ru = { add_mode:"Добавить режим", edit_mode:"Изменить режим", mode_name:"Название режима", current_threshold:"Порог тока", measured_current:"Измеренный ток", unavailable:"недоступен", cancel:"Отмена", add:"Добавить", save:"Сохранить", required_name:"Введите название режима", required_current:"Введите корректный ток" };
      const en = { add_mode:"Add mode", edit_mode:"Edit mode", mode_name:"Mode name", current_threshold:"Current threshold", measured_current:"Measured current", unavailable:"unavailable", cancel:"Cancel", add:"Add", save:"Save", required_name:"Enter a mode name", required_current:"Enter a valid current" };
      return (isRu(instance) ? ru : en)[key];
    };

    const showEditor = (instance, existing = null) => {
      const editing = existing !== null;
      const dialog = document.createElement("ha-dialog");
      dialog.setAttribute("header-title", text(instance, editing ? "edit_mode" : "add_mode"));
      dialog.setAttribute("prevent-scrim-close", "");

      const body = document.createElement("div");
      body.innerHTML = `
        <style>
          .spml-editor{display:flex;flex-direction:column;gap:24px;min-width:0}.spml-field{display:flex;flex-direction:column;gap:8px}.spml-label{font-size:14px;font-weight:500;color:var(--primary-text-color)}.spml-threshold-head{display:flex;align-items:center;justify-content:space-between;gap:16px}.spml-measured{display:flex;align-items:center;justify-content:flex-end;color:var(--secondary-text-color);font-size:14px;text-align:right}.spml-measured-value{cursor:pointer;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:3px}.spml-measured-value.unavailable{cursor:default;text-decoration:none}.spml-input-wrap{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:10px}.spml-input{box-sizing:border-box;width:100%;min-height:56px;padding:0 16px;border:1px solid var(--outline-color,var(--divider-color));border-radius:12px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit;font-size:16px;outline:none}.spml-input:focus{border:2px solid var(--primary-color);padding:0 15px}.spml-unit{color:var(--secondary-text-color);font-size:16px}.spml-error{min-height:18px;color:var(--error-color);font-size:12px}
        </style>
        <div class="spml-editor">
          <div class="spml-field"><label class="spml-label" for="spml-name">${text(instance,"mode_name")}</label><input id="spml-name" class="spml-input spml-name" type="text" autocomplete="off" /></div>
          <div class="spml-field"><div class="spml-threshold-head"><label class="spml-label" for="spml-current">${text(instance,"current_threshold")}</label><div class="spml-measured"><span class="spml-measured-value"></span></div></div><div class="spml-input-wrap"><input id="spml-current" class="spml-input spml-current" type="number" min="0" step="0.001" inputmode="decimal" /><span class="spml-unit">A</span></div></div>
          <div class="spml-error"></div>
        </div>`;

      const footer = document.createElement("ha-dialog-footer");
      footer.slot = "footer";
      footer.innerHTML = `<ha-button class="spml-cancel" appearance="plain" slot="secondaryAction">${text(instance,"cancel")}</ha-button><ha-button class="spml-save" slot="primaryAction">${text(instance,editing?"save":"add")}</ha-button>`;
      dialog.append(body, footer);
      document.body.append(dialog);

      const nameInput = body.querySelector(".spml-name");
      const currentInput = body.querySelector(".spml-current");
      const measuredNode = body.querySelector(".spml-measured-value");
      const errorNode = body.querySelector(".spml-error");
      nameInput.value = existing?.name ?? "";
      currentInput.value = existing?.current ?? "";

      let measuredValue = null;
      let unsubscribe = null;
      const renderMeasured = (value) => {
        measuredValue = value;
        measuredNode.dataset.value = value === null ? "" : String(value);
        measuredNode.classList.toggle("unavailable", value === null);
        measuredNode.textContent = value === null ? `${text(instance,"measured_current")}: ${text(instance,"unavailable")}` : `${text(instance,"measured_current")}: ${value.toFixed(3).replace(/0+$/," ").trim().replace(/\.$/,"")} A`;
      };
      renderMeasured(currentInAmps(instance));

      const entityId = findCurrentSensor(instance);
      if (entityId && instance.hass?.connection?.subscribeEvents) {
        instance.hass.connection.subscribeEvents((event) => {
          const data = event?.data;
          if (data?.entity_id === entityId) renderMeasured(stateToAmps(data.new_state));
        }, "state_changed").then((unsub) => { unsubscribe = unsub; }).catch(() => {});
      }

      measuredNode.addEventListener("click", () => {
        if (measuredValue === null) return;
        const normalized = Number(measuredValue.toFixed(3));
        currentInput.value = String(normalized);
        currentInput.dispatchEvent(new Event("input", { bubbles:true }));
        currentInput.focus();
        currentInput.select();
      });

      const close = () => { dialog.open = false; };
      footer.querySelector(".spml-cancel")?.addEventListener("click", close);
      const submit = () => {
        const name = String(nameInput.value || "").trim();
        const current = Number(currentInput.value);
        if (!name) { errorNode.textContent = text(instance,"required_name"); nameInput.focus(); return; }
        if (!Number.isFinite(current) || current < 0) { errorNode.textContent = text(instance,"required_current"); currentInput.focus(); return; }
        dialog.dispatchEvent(new CustomEvent("spml-submit", { detail:{ name,current } }));
        close();
      };
      footer.querySelector(".spml-save")?.addEventListener("click", submit);
      body.addEventListener("keydown", (event) => { if (event.key === "Enter") { event.preventDefault(); submit(); } });
      dialog.addEventListener("closed", () => { try { unsubscribe?.(); } catch (_) {} dialog.remove(); }, { once:true });
      dialog.open = true;
      requestAnimationFrame(() => nameInput.focus());
      return dialog;
    };

    selector.prototype._addItem = async function(ev){ if(!isOurSelector(this)) return originalAdd.call(this,ev); ev.stopPropagation(); const dialog=showEditor(this,null); dialog.addEventListener("spml-submit",(event)=>{const next=Array.isArray(this.value)?this.value.slice():[];next.push(event.detail);next.sort((a,b)=>Number(a.current)-Number(b.current));this.dispatchEvent(new CustomEvent("value-changed",{detail:{value:next},bubbles:true,composed:true}));},{once:true});};
    selector.prototype._editItem = async function(ev){ if(!isOurSelector(this)) return originalEdit.call(this,ev); ev.stopPropagation(); const item=ev.currentTarget.item; const index=ev.currentTarget.index; const dialog=showEditor(this,item); dialog.addEventListener("spml-submit",(event)=>{const next=Array.isArray(this.value)?this.value.slice():[];next[index]=event.detail;next.sort((a,b)=>Number(a.current)-Number(b.current));this.dispatchEvent(new CustomEvent("value-changed",{detail:{value:next},bubbles:true,composed:true}));},{once:true});};
    selector.prototype.__smartPlugModesEnhanced = true;
  }
}

const tryEnhance = () => { if (customElements.get("ha-selector-object")) { SmartPlugModesEnhancer.enhance(); return true; } return false; };
if (!tryEnhance()) customElements.whenDefined("ha-selector-object").then(() => SmartPlugModesEnhancer.enhance());
