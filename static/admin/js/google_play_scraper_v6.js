(function () {
  const DEFAULT_TOPUP_INFO = [
    "【代储说明】",
    "1. 联系客服确认商品与价格。",
    "2. 提供区服、角色与商品截图等信息。",
    "3. 完成付款后客服会尽快完成代储。",
  ].join("\n");

  function getField(id) {
    return document.getElementById(id);
  }

  function fillField(id, value) {
    const field = getField(id);
    if (!field) return;
    field.value = value || "";
    field.dispatchEvent(new Event("input", { bubbles: true }));
    field.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function getFieldValue(id) {
    const field = getField(id);
    if (!field || typeof field.value !== "string") return "";
    return field.value.trim();
  }

  function isFieldEmpty(id) {
    return !getFieldValue(id);
  }

  function setFieldIfEmpty(id, value) {
    if (!isFieldEmpty(id)) return false;
    fillField(id, value || "");
    return true;
  }

  function setStatus(statusEl, html, color) {
    if (!statusEl) return;
    statusEl.innerHTML = html;
    statusEl.style.color = color || "#666";
  }

  function parsePackageIdFromUrl(url) {
    try {
      const parsed = new URL(url);
      return parsed.searchParams.get("id") || "";
    } catch (error) {
      return "";
    }
  }

  function guessTitleFromPackageId(packageId) {
    if (!packageId) return "";
    const tail = packageId.split(".").pop() || packageId;
    return tail.replace(/[-_]+/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
  }

  function stripHtmlToText(value) {
    const html = String(value || "").trim();
    if (!html) return "";
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      return String(doc.body.textContent || "")
        .replace(/\s+/g, " ")
        .trim();
    } catch (error) {
      return html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    }
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

  async function requestScrape(url) {
    const response = await fetch(
      "/admin/game_page/gamepage/scrape-google-play/?url=" + encodeURIComponent(url),
      { credentials: "same-origin" }
    );

    let data = {};
    try {
      data = await response.json();
    } catch (error) {
      throw new Error(`抓取接口返回了非 JSON 响应 (HTTP ${response.status})`);
    }

    if (!response.ok || data.error) {
      throw new Error(data.error || `抓取失败 (HTTP ${response.status})`);
    }
    return data || {};
  }

  async function requestAiRewrite(rawText, gameName) {
    const response = await fetch("/api/seo-automation/rewrite/", {
      method: "POST",
      credentials: "omit",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        raw_text: String(rawText || ""),
        game_name: String(gameName || "游戏").slice(0, 80),
        keywords: [],
        store_draft: false,
      }),
    });

    let data = {};
    try {
      data = await response.json();
    } catch (error) {
      data = {};
    }

    if (!response.ok) {
      const detail = data.detail || data.error || data.message || `HTTP ${response.status}`;
      throw new Error(String(detail));
    }
    return data || {};
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
    const button = container.querySelector("#select-icon-btn");
    if (!button) return;

    button.onclick = function () {
      const iconInput = document.querySelector('input[type="file"][name="icon_image"]');
      if (iconInput && window.openMediaModal) {
        window.openMediaModal(iconInput);
        setTimeout(() => {
          if (window.setMediaSearch) window.setMediaSearch(title || "");
        }, 260);
      } else {
        alert("未找到图标上传框，或素材库组件未加载。");
      }
    };
  }

  async function applyTopupTemplatePriority(templateText) {
    // Priority 1: dedicated topup template module (default template key).
    if (typeof window.gpcApplyTopupTemplate === "function") {
      try {
        const result = await window.gpcApplyTopupTemplate("default", {
          onlyFillEmpty: true,
          silent: true,
        });
        if (result && result.applied) return "default_template";
      } catch (error) {
        console.warn("apply default topup template failed:", error);
      }
    }

    // Priority 2: fallback text from API payload or built-in default.
    const fallback = String(templateText || DEFAULT_TOPUP_INFO).trim();
    if (!fallback) return "none";
    let changed = false;
    if (setFieldIfEmpty("id_topup_info", fallback)) changed = true;
    if (setFieldIfEmpty("id_topup_info_tw", fallback)) changed = true;
    return changed ? "fallback_template" : "none";
  }

  function fillSeoFieldsIfEmpty(title, description, developer, packageId) {
    const seoTitle = getField("id_seo_title");
    if (seoTitle && !seoTitle.value && title) {
      seoTitle.value = `${title}代储_充值`;
      seoTitle.dispatchEvent(new Event("input", { bubbles: true }));
      seoTitle.dispatchEvent(new Event("change", { bubbles: true }));
    }

    const seoDescription = getField("id_seo_description");
    if (seoDescription && !seoDescription.value && description) {
      seoDescription.value = String(description).slice(0, 160);
      seoDescription.dispatchEvent(new Event("input", { bubbles: true }));
      seoDescription.dispatchEvent(new Event("change", { bubbles: true }));
    }

    const seoKeywords = getField("id_seo_keywords");
    if (seoKeywords && !seoKeywords.value) {
      const keywords = [
        title,
        developer,
        packageId,
        title ? `${title}充值` : "",
        title ? `${title}代储` : "",
      ]
        .filter(Boolean)
        .map((x) => String(x).trim())
        .filter(Boolean);
      if (keywords.length) {
        seoKeywords.value = keywords.join(", ");
        seoKeywords.dispatchEvent(new Event("input", { bubbles: true }));
        seoKeywords.dispatchEvent(new Event("change", { bubbles: true }));
      }
    }
  }

  function buildAiRawText(context) {
    const existing = [getFieldValue("id_content"), getFieldValue("id_description")].filter(Boolean);
    if (existing.length) return existing.join("\n\n");

    const title = context.title || "游戏";
    return [
      `游戏名称：${title}`,
      context.packageId ? `Google Play ID：${context.packageId}` : "",
      context.developer ? `开发商：${context.developer}` : "",
      context.description ? `简介：${context.description}` : "",
      "请生成：游戏详情、简短介绍、SEO标题、SEO关键词、SEO描述。",
    ]
      .filter(Boolean)
      .join("\n");
  }

  function applyAiResultToFields(aiData, context) {
    const bodyHtml = String(aiData.body_html || "").trim();
    const metaTitle = String(aiData.meta_title || aiData.title || "").trim();
    const metaDescription = String(aiData.meta_description || "").trim();
    const keywords = Array.isArray(aiData.tags) ? aiData.tags.filter(Boolean).join(", ") : "";
    const title = String(aiData.title || context.title || "").trim();
    const summary = metaDescription || stripHtmlToText(bodyHtml).slice(0, 160);

    let changed = 0;
    if (setFieldIfEmpty("id_title", title)) changed += 1;
    if (setFieldIfEmpty("id_title_tw", title)) changed += 1;
    if (setFieldIfEmpty("id_content", bodyHtml)) changed += 1;
    if (setFieldIfEmpty("id_content_tw", bodyHtml)) changed += 1;
    if (setFieldIfEmpty("id_description", summary)) changed += 1;
    if (setFieldIfEmpty("id_description_tw", summary)) changed += 1;
    if (setFieldIfEmpty("id_seo_title", metaTitle || `${title}代储_充值`)) changed += 1;
    if (setFieldIfEmpty("id_seo_description", summary)) changed += 1;
    if (setFieldIfEmpty("id_seo_keywords", keywords)) changed += 1;
    return changed;
  }

  function shouldShowAiFallbackButton() {
    return (
      isFieldEmpty("id_content") ||
      isFieldEmpty("id_description") ||
      isFieldEmpty("id_seo_title") ||
      isFieldEmpty("id_seo_keywords") ||
      isFieldEmpty("id_seo_description")
    );
  }

  function appendAiFallbackButton(statusEl, context) {
    if (!statusEl) return;
    if (!shouldShowAiFallbackButton()) return;
    if (statusEl.querySelector("#gp-ai-generate-btn")) return;

    const wrap = document.createElement("div");
    wrap.style.marginTop = "8px";

    const hint = document.createElement("span");
    hint.textContent = "SEO 或详情字段存在缺失，可使用 AI 补齐：";
    hint.style.marginRight = "8px";
    hint.style.color = "#374151";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.id = "gp-ai-generate-btn";
    btn.className = "button";
    btn.textContent = "AI 一键补齐";
    btn.style.padding = "4px 10px";
    btn.style.height = "30px";

    btn.addEventListener("click", async function () {
      if (btn.dataset.loading === "1") return;
      btn.dataset.loading = "1";
      btn.disabled = true;
      const textBak = btn.textContent;
      btn.textContent = "AI 生成中...";

      try {
        const rawText = buildAiRawText(context);
        const aiData = await requestAiRewrite(rawText, context.title || "");
        const changed = applyAiResultToFields(aiData, context);
        setStatus(
          statusEl,
          changed
            ? `AI 已补齐 ${changed} 个字段（仅填充空字段）。`
            : "字段均已有内容，AI 未覆盖已有值。",
          changed ? "green" : "#6b7280"
        );
      } catch (error) {
        setStatus(statusEl, `AI 生成失败：${error.message || error}`, "red");
        appendAiFallbackButton(statusEl, context);
      } finally {
        btn.dataset.loading = "0";
        btn.disabled = false;
        btn.textContent = textBak;
      }
    });

    wrap.appendChild(hint);
    wrap.appendChild(btn);
    statusEl.appendChild(wrap);
  }

  function getContentTypesetButton() {
    const contentField = getField("id_content");
    if (!contentField || typeof contentField.closest !== "function") return null;
    const shell = contentField.closest(".uai-lite-shell");
    if (!shell) return null;
    return shell.querySelector('button[data-action="ai-typeset"]');
  }

  function appendContentTypesetButton(statusEl) {
    if (!statusEl) return;
    if (statusEl.querySelector("#gp-content-typeset-btn")) return;

    const wrap = document.createElement("div");
    wrap.style.marginTop = "8px";

    const hint = document.createElement("span");
    hint.textContent = "提取结果可直接排版：";
    hint.style.marginRight = "8px";
    hint.style.color = "#374151";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.id = "gp-content-typeset-btn";
    btn.className = "button";
    btn.textContent = "一键排版（游戏详情）";
    btn.style.padding = "4px 10px";
    btn.style.height = "30px";

    btn.addEventListener("click", function () {
      const typesetBtn = getContentTypesetButton();
      if (!typesetBtn) {
        setStatus(
          statusEl,
          "未找到游戏详情排版按钮，请稍后重试（编辑器尚在初始化）。",
          "#b45309"
        );
        return;
      }
      typesetBtn.click();
      setStatus(statusEl, "已触发游戏详情一键排版，请等待处理完成。", "#1d4ed8");
    });

    wrap.appendChild(hint);
    wrap.appendChild(btn);
    statusEl.appendChild(wrap);
  }

  async function handleScrape(button, input, status) {
    const url = input.value.trim();
    if (!url) {
      alert("请输入 Google Play 链接");
      return;
    }

    setStatus(status, "正在抓取并同步图标，请稍候...", "#666");
    button.style.opacity = "0.5";
    button.style.pointerEvents = "none";

    try {
      const data = await requestScrape(url);

      const packageId = data.package_id || parsePackageIdFromUrl(url);
      const title = data.title || guessTitleFromPackageId(packageId);
      const description = data.description || (title ? `${title} 游戏介绍待完善。` : "");
      const content = data.content || description;
      const aiContext = {
        url,
        title,
        description,
        packageId,
        developer: data.developer || "",
      };

      fillField("id_title", title);
      if (isFieldEmpty("id_title_tw")) fillField("id_title_tw", title);
      fillField("id_developer", data.developer || "");
      fillField("id_google_play_id", packageId || "");
      fillField("id_description", description);
      fillField("id_description_tw", description);
      fillField("id_content", content);
      fillField("id_content_tw", content);
      fillField("id_icon_external_url", data.icon_external_url || data.icon_url || "");

      await applyTopupTemplatePriority(data.topup_info_template || DEFAULT_TOPUP_INFO);
      fillSeoFieldsIfEmpty(title, description, data.developer || "", packageId || "");

      const hasExternalFallback = Boolean(data.icon_external_url || data.icon_url);
      let uploadedToIconField = false;
      if (data.media_url) {
        uploadedToIconField = await applyMediaToIconInput(
          data.media_url,
          data.package_id || data.title || "game-icon"
        );
      }

      const warningTip = data.warning ? `<br>提示：${data.warning}` : "";
      if (uploadedToIconField) {
        const extra = hasExternalFallback ? "<br>已写入 icon_external_url 兜底。" : "";
        setStatus(status, `导入成功，图标已自动下载并写入图标上传框。${extra}${warningTip}`, "green");
        appendContentTypesetButton(status);
        appendAiFallbackButton(status, aiContext);
        return;
      }

      if (data.media_id) {
        const extra = hasExternalFallback ? "<br>已写入 icon_external_url 兜底。" : "";
        setStatus(
          status,
          `导入成功，图标已同步到素材库（ID: ${data.media_id}）。${extra}${warningTip}` +
            '<br><button type="button" id="select-icon-btn" style="margin-top:6px;padding:4px 8px;border:1px solid #ddd;background:#f5f5f5;cursor:pointer;">在素材库中选择此图标</button>',
          "green"
        );
        bindManualPickerAction(status, data.title || "");
        appendContentTypesetButton(status);
        appendAiFallbackButton(status, aiContext);
        return;
      }

      if (hasExternalFallback) {
        setStatus(status, `导入成功，已写入图标外链兜底（icon_external_url）。${warningTip}`, "green");
        appendContentTypesetButton(status);
        appendAiFallbackButton(status, aiContext);
        return;
      }

      setStatus(status, `导入成功（未提取到图标）。${warningTip}`, "green");
      appendContentTypesetButton(status);
      appendAiFallbackButton(status, aiContext);
    } catch (error) {
      console.error("Scraper error:", error);
      setStatus(status, `抓取失败：${error.message}`, "red");
    } finally {
      button.style.opacity = "1";
      button.style.pointerEvents = "auto";
    }
  }

  function initScraper() {
    const button = getField("scrape-btn");
    const input = getField("google-play-url");
    const status = getField("scrape-status");
    if (!button || !input || !status) return;
    if (button.dataset.bound) return;

    button.dataset.bound = "true";
    button.onclick = function () {
      handleScrape(button, input, status);
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initScraper);
  } else {
    initScraper();
  }

  setInterval(initScraper, 1000);
})();
