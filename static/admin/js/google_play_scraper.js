(function () {
  function fillField(id, value) {
    const field = document.getElementById(id);
    if (!field) return;
    field.value = value || "";
    field.dispatchEvent(new Event("input", { bubbles: true }));
    field.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function slugifyFilename(raw) {
    const normalized = String(raw || "game-icon")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "");
    return normalized || "game-icon";
  }

  function setStatus(statusEl, html, color) {
    statusEl.innerHTML = html;
    statusEl.style.color = color || "#666";
  }

  async function applyMediaToIconInput(mediaUrl, fileHint) {
    const iconInput = document.querySelector('input[type="file"][name="icon_image"]');
    if (!iconInput || !mediaUrl) return false;

    try {
      const response = await fetch(mediaUrl, { credentials: "same-origin" });
      if (!response.ok) return false;

      const blob = await response.blob();
      if (!blob || !blob.size) return false;

      const mime = blob.type || "image/png";
      let ext = "png";
      if (mime.includes("jpeg")) ext = "jpg";
      else if (mime.includes("webp")) ext = "webp";
      else if (mime.includes("gif")) ext = "gif";

      const fileName = `${slugifyFilename(fileHint)}.${ext}`;
      const file = new File([blob], fileName, { type: mime });

      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      iconInput.files = dataTransfer.files;
      iconInput.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    } catch (error) {
      console.error("Auto apply icon file failed:", error);
      return false;
    }
  }

  function bindManualPickerAction(container, title) {
    const btn = container.querySelector("#select-icon-btn");
    if (!btn) return;

    btn.onclick = function () {
      const iconInput = document.querySelector('input[type="file"][name="icon_image"]');
      if (iconInput && window.openMediaModal) {
        window.openMediaModal(iconInput);
        setTimeout(() => {
          if (window.setMediaSearch) window.setMediaSearch(title || "");
        }, 260);
      } else {
        alert("未找到图标上传框或素材库组件未加载");
      }
    };
  }

  async function handleScrape(btn, input, status) {
    const url = input.value.trim();
    if (!url) {
      alert("请输入 Google Play 链接");
      return;
    }

    setStatus(status, "⏳ 正在抓取并同步图标...", "#666");
    btn.style.opacity = "0.5";
    btn.style.pointerEvents = "none";

    try {
      const response = await fetch(
        "/admin/game_page/gamepage/scrape-google-play/?url=" + encodeURIComponent(url),
        { credentials: "same-origin" }
      );
      const data = await response.json();

      if (!response.ok || data.error) {
        setStatus(status, "❌ " + (data.error || "抓取失败"), "red");
        return;
      }

      fillField("id_title", data.title || "");
      fillField("id_developer", data.developer || "");
      fillField("id_google_play_id", data.package_id || "");
      fillField("id_description", data.description || "");
      fillField("id_icon_external_url", data.icon_external_url || data.icon_url || "");

      const hasExternalFallback = Boolean(data.icon_external_url || data.icon_url);
      let uploadedToIconField = false;

      if (data.media_url) {
        uploadedToIconField = await applyMediaToIconInput(
          data.media_url,
          data.package_id || data.title || "game-icon"
        );
      }

      if (uploadedToIconField) {
        const extra = hasExternalFallback ? "<br>已写入外链兜底（icon_external_url）" : "";
        setStatus(
          status,
          `✅ 导入成功！图标已自动下载到素材库并写入图标上传框${extra}<br>保存后将优先显示本地图，外链作为兜底。`,
          "green"
        );
        return;
      }

      if (data.media_id) {
        const extra = hasExternalFallback ? "<br>已写入外链兜底（icon_external_url）" : "";
        setStatus(
          status,
          `✅ 导入成功！图标已同步至素材库（ID: ${data.media_id}）${extra}<br><button type="button" id="select-icon-btn" style="margin-top:6px;padding:4px 8px;border:1px solid #ddd;background:#f5f5f5;cursor:pointer;">🔍 在素材库中选择此图标</button>`,
          "green"
        );
        bindManualPickerAction(status, data.title || "");
        return;
      }

      if (hasExternalFallback) {
        setStatus(
          status,
          "✅ 导入成功！已写入图标外链兜底（icon_external_url），保存后前台可显示。",
          "green"
        );
        return;
      }

      setStatus(status, "✅ 导入成功（未提取到图标）", "green");
    } catch (error) {
      console.error("Scraper error:", error);
      setStatus(status, "❌ 网络错误: " + error.message, "red");
    } finally {
      btn.style.opacity = "1";
      btn.style.pointerEvents = "auto";
    }
  }

  function initScraper() {
    const btn = document.getElementById("scrape-btn");
    const input = document.getElementById("google-play-url");
    const status = document.getElementById("scrape-status");
    if (!btn || !input || !status) return;
    if (btn.dataset.bound) return;

    btn.dataset.bound = "true";
    btn.onclick = function () {
      handleScrape(btn, input, status);
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initScraper);
  } else {
    initScraper();
  }

  // Re-bind periodically for dynamic admin content.
  setInterval(initScraper, 1000);
})();
