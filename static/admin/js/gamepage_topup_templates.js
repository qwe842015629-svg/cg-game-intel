(function () {
  const TOOLBAR_ID = "topup-template-toolbar";
  const STATUS_ID = "topup-template-status";
  const SELECT_ID = "topup-template-select";
  const BTN_LOAD_ID = "topup-template-load-btn";
  const BTN_SAVE_ID = "topup-template-save-btn";
  const DEFAULT_TEMPLATE_KEY = "default";

  const state = {
    autoApplied: false,
  };

  function getAdminBasePath() {
    const marker = "/game_page/gamepage/";
    const path = String(window.location.pathname || "");
    if (!path.includes(marker)) {
      return "/admin/game_page/gamepage";
    }
    return path.split(marker)[0] + marker.slice(0, -1);
  }

  function endpoint(path) {
    return `${getAdminBasePath()}/topup-template/${path}/`;
  }

  function getCsrfToken() {
    const input = document.querySelector("input[name='csrfmiddlewaretoken']");
    if (input && input.value) return input.value;
    const match = document.cookie.match(/(?:^|;)\s*csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function getField(id) {
    return document.getElementById(id);
  }

  function getFieldText(field) {
    if (!field || typeof field.value !== "string") return "";
    return field.value.trim();
  }

  function isEmptyField(field) {
    return !getFieldText(field);
  }

  function setFieldValue(field, value) {
    if (!field) return;
    field.value = value || "";
    field.dispatchEvent(new Event("input", { bubbles: true }));
    field.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function setStatus(message, color) {
    const el = document.getElementById(STATUS_ID);
    if (!el) return;
    el.textContent = message || "";
    el.style.color = color || "#666";
  }

  function normalizeKey(rawKey) {
    const key = String(rawKey || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9_-]/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "");
    return key || DEFAULT_TEMPLATE_KEY;
  }

  async function fetchTemplateList() {
    const select = document.getElementById(SELECT_ID);
    if (!select) return [];

    select.innerHTML = `<option value="">Loading...</option>`;
    setStatus("Loading templates...", "#666");

    try {
      const resp = await fetch(endpoint("list"), {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);

      const items = Array.isArray(data.items) ? data.items : [];
      if (!items.length) {
        select.innerHTML = `<option value="">No template</option>`;
        setStatus("No template yet", "#666");
        return [];
      }

      select.innerHTML = items
        .map((item) => {
          const key = String(item.key || "").trim();
          return `<option value="${key}">${key}</option>`;
        })
        .join("");

      const hasDefault = items.some((item) => String(item.key || "").trim() === DEFAULT_TEMPLATE_KEY);
      if (hasDefault) {
        select.value = DEFAULT_TEMPLATE_KEY;
      } else if (items[0] && items[0].key) {
        select.value = String(items[0].key);
      }

      setStatus(`Loaded ${items.length} templates`, "#1f7a1f");
      return items;
    } catch (error) {
      console.error("template list error:", error);
      select.innerHTML = `<option value="">Load failed</option>`;
      setStatus(`Load failed: ${error.message}`, "#c0392b");
      return [];
    }
  }

  async function applyTemplateByKey(rawKey, options) {
    const opts = options || {};
    const onlyFillEmpty = Boolean(opts.onlyFillEmpty);
    const silent = Boolean(opts.silent);

    const select = document.getElementById(SELECT_ID);
    const topupInfo = getField("id_topup_info");
    const topupInfoTw = getField("id_topup_info_tw");
    if (!topupInfo || !topupInfoTw) {
      return { applied: false, reason: "fields_not_found" };
    }

    let key = normalizeKey(rawKey || (select ? select.value : ""));
    if (!key) key = DEFAULT_TEMPLATE_KEY;

    const bothNonEmpty = !isEmptyField(topupInfo) && !isEmptyField(topupInfoTw);
    if (onlyFillEmpty && bothNonEmpty) {
      if (!silent) setStatus("Topup fields already filled, skipped", "#666");
      return { applied: false, reason: "already_filled", key };
    }

    if (!silent) setStatus(`Loading template: ${key} ...`, "#666");
    try {
      const resp = await fetch(`${endpoint("load")}?key=${encodeURIComponent(key)}`, {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);

      const nextCn = String(data.topup_info || "");
      const nextTw = String(data.topup_info_tw || "");

      if (onlyFillEmpty) {
        if (isEmptyField(topupInfo) && nextCn.trim()) setFieldValue(topupInfo, nextCn);
        if (isEmptyField(topupInfoTw) && nextTw.trim()) setFieldValue(topupInfoTw, nextTw || nextCn);
      } else {
        setFieldValue(topupInfo, nextCn);
        setFieldValue(topupInfoTw, nextTw);
      }

      if (select) select.value = key;
      if (!silent) setStatus(`Template applied: ${key}`, "#1f7a1f");
      return { applied: true, key, data };
    } catch (error) {
      console.error("template load error:", error);
      if (!silent) setStatus(`Apply failed: ${error.message}`, "#c0392b");
      return { applied: false, reason: "request_failed", key, error };
    }
  }

  async function loadTemplate() {
    const select = document.getElementById(SELECT_ID);
    const key = String((select && select.value) || "").trim();
    if (!key) {
      setStatus("Please select a template first", "#c0392b");
      return;
    }
    await applyTemplateByKey(key, { onlyFillEmpty: false, silent: false });
  }

  async function maybeApplyDefaultTemplate() {
    if (state.autoApplied) return;

    const topupInfo = getField("id_topup_info");
    const topupInfoTw = getField("id_topup_info_tw");
    if (!topupInfo || !topupInfoTw) return;

    if (!isEmptyField(topupInfo) && !isEmptyField(topupInfoTw)) {
      state.autoApplied = true;
      return;
    }

    state.autoApplied = true;
    const result = await applyTemplateByKey(DEFAULT_TEMPLATE_KEY, {
      onlyFillEmpty: true,
      silent: true,
    });
    if (result.applied) {
      setStatus(`Template applied: ${result.key}`, "#1f7a1f");
    }
  }

  async function saveTemplate() {
    const topupInfo = getField("id_topup_info");
    const topupInfoTw = getField("id_topup_info_tw");
    const select = document.getElementById(SELECT_ID);
    if (!topupInfo || !topupInfoTw || !select) return;

    const initial = select.value || DEFAULT_TEMPLATE_KEY;
    const inputKey = window.prompt("Template key", initial);
    if (inputKey === null) return;
    const key = normalizeKey(inputKey);

    const payload = {
      key,
      topup_info: String(topupInfo.value || ""),
      topup_info_tw: String(topupInfoTw.value || ""),
    };

    if (!payload.topup_info.trim() && !payload.topup_info_tw.trim()) {
      setStatus("Nothing to save: both fields are empty", "#c0392b");
      return;
    }

    setStatus(`Saving template: ${key} ...`, "#666");
    try {
      const resp = await fetch(endpoint("save"), {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
          Accept: "application/json",
        },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);

      await fetchTemplateList();
      const newSelect = document.getElementById(SELECT_ID);
      if (newSelect) newSelect.value = key;
      setStatus(`Template saved: ${key}`, "#1f7a1f");
    } catch (error) {
      console.error("template save error:", error);
      setStatus(`Save failed: ${error.message}`, "#c0392b");
    }
  }

  function exposePublicApi() {
    window.gpcApplyTopupTemplate = function (key, options) {
      const opts = Object.assign({ onlyFillEmpty: false, silent: false }, options || {});
      return applyTemplateByKey(key || DEFAULT_TEMPLATE_KEY, opts);
    };
  }

  function createToolbar() {
    const topupInfo = getField("id_topup_info");
    const topupInfoTw = getField("id_topup_info_tw");
    if (!topupInfo || !topupInfoTw) return;
    if (document.getElementById(TOOLBAR_ID)) return;

    const anchor = topupInfo.closest(".form-row") || topupInfo.parentElement;
    if (!anchor || !anchor.parentNode) return;

    const toolbar = document.createElement("div");
    toolbar.id = TOOLBAR_ID;
    toolbar.style.cssText = [
      "display:flex",
      "align-items:center",
      "gap:8px",
      "padding:10px 12px",
      "margin:0 0 10px",
      "border:1px solid #e5e7eb",
      "border-radius:6px",
      "background:#f8fafc",
      "flex-wrap:wrap",
    ].join(";");

    toolbar.innerHTML = `
      <strong style="font-size:12px;color:#334155;">Topup Template</strong>
      <select id="${SELECT_ID}" style="min-width:180px;height:30px;border:1px solid #d1d5db;border-radius:4px;padding:0 8px;"></select>
      <button type="button" id="${BTN_LOAD_ID}" class="button">Use Template</button>
      <button type="button" id="${BTN_SAVE_ID}" class="button">Save as Template</button>
      <span id="${STATUS_ID}" style="font-size:12px;color:#666;"></span>
    `;

    anchor.parentNode.insertBefore(toolbar, anchor);

    const loadBtn = document.getElementById(BTN_LOAD_ID);
    const saveBtn = document.getElementById(BTN_SAVE_ID);
    if (loadBtn) loadBtn.addEventListener("click", loadTemplate);
    if (saveBtn) saveBtn.addEventListener("click", saveTemplate);

    fetchTemplateList().then(() => maybeApplyDefaultTemplate());
  }

  function init() {
    exposePublicApi();
    createToolbar();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  setInterval(init, 1200);
})();
