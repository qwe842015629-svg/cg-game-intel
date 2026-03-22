(function () {
  const DEFAULT_TOPUP_INFO = `【🎮 1. 聯繫客服】
加入我們的微信官方帳號（VX：Lirenxin_2015，公眾號：盼星全球手游）。
請直接傳送您想購買的商品截圖給客服，我們會快速核對價格並提供報價。

【🔒 2. 身份驗證】
若您是第一次使用我們的服務，需先進行簡單身份核實，確保交易為您本人操作，以保障帳號安全。

【💰 3. 選擇付款方式】
確認金額後，您可選擇【銀行轉帳】或【超商付款】。
付款完成後請將交易資訊回傳客服，我們會立即為您核帳，讓流程更快速。

【✅ 4. 完成儲值】
確認款項與遊戲資訊無誤後，我們會立刻為您完成儲值，並透過 LINE 通知您，即可安心上線遊玩。

【手遊代儲常見問題 Q&A】
Q：代儲會不會影響我的帳號安全？
A：請放心。我們已穩定營運多年，嚴格杜絕低價黑卡與非法操作，確保您的帳號安全。

Q：為什麼代儲價格會比自己儲值便宜？
A：我們透過各國匯率差異與點數卡渠道優勢降低成本，因此可提供更實惠的價格。

Q：自己買點卡會不會更方便？
A：不一定。部分低價點卡可能來自非法來源，存在封號風險；我們提供合法、安全且省時的代儲流程。

【為什麼選擇我們】
✔ 安全保障：所有點數卡均來自官方正規渠道，並由各國專業買手採購。
💲 價格實惠：主打薄利多銷，價格普遍優於市面多數代儲商。
🤝 專人服務：全年無休，24 小時客服在線，從詢價到完成代儲全程協助。

【提供代儲資料】
為完成儲值，請準備並提供以下資訊給客服：
- 遊戲名稱
- 登入方式（Facebook、Google 等）
- 遊戲帳號（名稱或 ID）
- 遊戲密碼（如需）
- 伺服器名稱
- 角色名稱
- 角色等級
- 購買商品截圖

【付款方式】
MEME GAME BUY 手遊代儲付款方式：
【無卡存款】
【銀行轉帳】
【超商代碼】`;

  function fillField(id, value) {
    const field = document.getElementById(id);
    if (!field) return;
    field.value = value || "";
    field.dispatchEvent(new Event("input", { bubbles: true }));
    field.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function getFieldValue(id) {
    const field = document.getElementById(id);
    if (!field || typeof field.value !== "string") return "";
    return field.value.trim();
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

    return data;
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
        alert("未找到图标上传框或素材库组件未加载。");
      }
    };
  }

  function fillTopupInfoIfEmpty(templateText) {
    if (!getFieldValue("id_topup_info")) {
      fillField("id_topup_info", templateText);
    }
    if (!getFieldValue("id_topup_info_tw")) {
      fillField("id_topup_info_tw", templateText);
    }
  }

  function fillSeoFieldsIfEmpty(title, description, developer, packageId) {
    const seoTitle = document.getElementById("id_seo_title");
    if (seoTitle && !seoTitle.value && title) {
      seoTitle.value = `${title}代储_充值 - MEME港台游戏工具箱`;
      seoTitle.dispatchEvent(new Event("input", { bubbles: true }));
      seoTitle.dispatchEvent(new Event("change", { bubbles: true }));
    }

    const seoDescription = document.getElementById("id_seo_description");
    if (seoDescription && !seoDescription.value && description) {
      seoDescription.value = String(description).slice(0, 160);
      seoDescription.dispatchEvent(new Event("input", { bubbles: true }));
      seoDescription.dispatchEvent(new Event("change", { bubbles: true }));
    }

    const seoKeywords = document.getElementById("id_seo_keywords");
    if (seoKeywords && !seoKeywords.value) {
      const candidates = [
        title,
        developer,
        packageId,
        title ? `${title}充值` : "",
        title ? `${title}代充` : "",
      ]
        .filter(Boolean)
        .map((x) => String(x).trim())
        .filter((x) => x.length > 0);
      if (candidates.length) {
        seoKeywords.value = candidates.join(", ");
        seoKeywords.dispatchEvent(new Event("input", { bubbles: true }));
        seoKeywords.dispatchEvent(new Event("change", { bubbles: true }));
      }
    }
  }

  async function handleScrape(button, input, status) {
    const url = input.value.trim();
    if (!url) {
      alert("请输入 Google Play 链接");
      return;
    }

    setStatus(status, "⏳ 正在抓取并同步图标，请稍候...", "#666");
    button.style.opacity = "0.5";
    button.style.pointerEvents = "none";

    try {
      const data = await requestScrape(url);

      const packageId = data.package_id || parsePackageIdFromUrl(url);
      const title = data.title || guessTitleFromPackageId(packageId);
      const description = data.description || (title ? `${title} 游戏介绍待完善。` : "");
      const content = data.content || description;
      const topupTemplate = data.topup_info_template || DEFAULT_TOPUP_INFO;

      fillField("id_title", title);
      if (!getFieldValue("id_title_tw")) {
        fillField("id_title_tw", title);
      }
      fillField("id_developer", data.developer || "");
      fillField("id_google_play_id", packageId || "");
      fillField("id_description", description);
      fillField("id_description_tw", description);
      fillField("id_content", content);
      fillField("id_content_tw", content);
      fillField("id_icon_external_url", data.icon_external_url || data.icon_url || "");

      fillTopupInfoIfEmpty(topupTemplate);
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
        const extra = hasExternalFallback ? "<br>已写入外链兜底（icon_external_url）" : "";
        setStatus(
          status,
          `✅ 导入成功！图标已自动下载到素材库并写入图标上传框。${extra}${warningTip}`,
          "green"
        );
        return;
      }

      if (data.media_id) {
        const extra = hasExternalFallback ? "<br>已写入外链兜底（icon_external_url）" : "";
        setStatus(
          status,
          `✅ 导入成功！图标已同步到素材库（ID: ${data.media_id}）。${extra}${warningTip}<br><button type="button" id="select-icon-btn" style="margin-top:6px;padding:4px 8px;border:1px solid #ddd;background:#f5f5f5;cursor:pointer;">📷 在素材库中选择此图标</button>`,
          "green"
        );
        bindManualPickerAction(status, data.title || "");
        return;
      }

      if (hasExternalFallback) {
        setStatus(
          status,
          `✅ 导入成功！已写入图标外链兜底（icon_external_url）。${warningTip}`,
          "green"
        );
        return;
      }

      setStatus(status, `✅ 导入成功（未提取到图标）。${warningTip}`, "green");
    } catch (error) {
      console.error("Scraper error:", error);
      setStatus(status, `❌ 抓取失败：${error.message}`, "red");
    } finally {
      button.style.opacity = "1";
      button.style.pointerEvents = "auto";
    }
  }

  function initScraper() {
    const button = document.getElementById("scrape-btn");
    const input = document.getElementById("google-play-url");
    const status = document.getElementById("scrape-status");
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

  // SimpleUI 会动态替换页面内容，定时重绑可保证按钮始终可用。
  setInterval(initScraper, 1000);
})();
