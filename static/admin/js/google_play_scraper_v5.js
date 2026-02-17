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

    const ADMIN_BASE = "/admin/game_page/gamepage";

    function setStatus(statusEl, text, color, useHtml) {
        if (!statusEl) return;
        if (useHtml) {
            statusEl.innerHTML = text;
        } else {
            statusEl.innerText = text;
        }
        statusEl.style.color = color || "#666";
    }

    function fillField(fieldId, value) {
        const el = document.getElementById(fieldId) || document.querySelector(`[name="${fieldId.replace(/^id_/, "")}"]`);
        if (!el) return;
        el.value = value || "";
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function getFieldValue(fieldId) {
        const el = document.getElementById(fieldId) || document.querySelector(`[name="${fieldId.replace(/^id_/, "")}"]`);
        return el && typeof el.value === "string" ? el.value.trim() : "";
    }

    function getCsrfToken() {
        const hidden = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (hidden && hidden.value) return hidden.value;

        const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : "";
    }

    function parsePackageIdFromUrl(url) {
        try {
            const parsed = new URL(url);
            return parsed.searchParams.get("id") || "";
        } catch {
            return "";
        }
    }

    function guessTitleFromPackageId(packageId) {
        if (!packageId) return "";
        const tail = packageId.split(".").pop() || packageId;
        return tail.replace(/[-_]+/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
    }

    async function requestScrape(url) {
        const resp = await fetch(`${ADMIN_BASE}/scrape-google-play/?url=${encodeURIComponent(url)}`, {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
        });

        let data = null;
        try {
            data = await resp.json();
        } catch {
            throw new Error(`抓取接口返回了非 JSON 响应 (HTTP ${resp.status})`);
        }

        if (!resp.ok || (data && data.error)) {
            throw new Error((data && data.error) || `抓取失败 (HTTP ${resp.status})`);
        }
        return data || {};
    }

    async function requestLoadTopupTemplate() {
        const resp = await fetch(`${ADMIN_BASE}/get-topup-template/`, {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
        });
        const data = await resp.json();
        if (!resp.ok || data.error) {
            throw new Error(data.error || `读取模板失败 (HTTP ${resp.status})`);
        }
        return data;
    }

    async function requestSaveTopupTemplate(payload) {
        const csrf = getCsrfToken();
        const resp = await fetch(`${ADMIN_BASE}/save-topup-template/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                "X-CSRFToken": csrf,
            },
            body: JSON.stringify(payload),
        });
        const data = await resp.json();
        if (!resp.ok || data.error) {
            throw new Error(data.error || `保存模板失败 (HTTP ${resp.status})`);
        }
        return data;
    }

    function fillTopupIfEmpty(data) {
        const topupTemplate = data.topup_info_template || DEFAULT_TOPUP_INFO;
        const topupTwTemplate = data.topup_info_tw_template || topupTemplate;
        if (!getFieldValue("id_topup_info")) {
            fillField("id_topup_info", topupTemplate);
        }
        if (!getFieldValue("id_topup_info_tw")) {
            fillField("id_topup_info_tw", topupTwTemplate);
        }
    }

    function bindScrapeButton() {
        const btn = document.getElementById("scrape-btn");
        const input = document.getElementById("google-play-url");
        const status = document.getElementById("scrape-status");
        if (!btn || !input || !status) return;
        if (btn.dataset.bound === "true") return;
        btn.dataset.bound = "true";

        btn.addEventListener("click", async function () {
            const url = input.value.trim();
            if (!url) {
                alert("请输入 Google Play 链接");
                return;
            }

            setStatus(status, "正在抓取，请稍候...", "#666");
            btn.style.opacity = "0.5";
            btn.style.pointerEvents = "none";

            try {
                const data = await requestScrape(url);
                const packageId = data.package_id || parsePackageIdFromUrl(url);
                const title = data.title || guessTitleFromPackageId(packageId);
                const fallbackDescription = data.description || (title ? `${title} 游戏介绍待完善。` : "");
                const fallbackContent = data.content || fallbackDescription;

                fillField("id_title", title);
                fillField("id_developer", data.developer);
                fillField("id_google_play_id", packageId);
                fillField("id_icon_external_url", data.icon_external_url || data.icon_url || "");
                fillField("id_description", fallbackDescription);
                fillField("id_description_tw", fallbackDescription);
                fillField("id_content", fallbackContent);
                fillField("id_content_tw", fallbackContent);
                fillTopupIfEmpty(data);

                const seoTitleEl = document.getElementById("id_seo_title");
                if (seoTitleEl && !seoTitleEl.value && title) {
                    seoTitleEl.value = `${title}代储_充值 - MEME港台游戏工具箱`;
                }

                if (data.warning) {
                    setStatus(status, `已填充基础信息（提示：${data.warning}）`, "#d97706");
                } else if (data.media_id) {
                    setStatus(status, `导入成功，图标已保存到素材库 (ID: ${data.media_id})。`, "#14853b");
                } else {
                    setStatus(status, "导入成功。", "#14853b");
                }
            } catch (err) {
                console.error("Google Play scrape failed:", err);
                const msg = `导入失败：${err.message}`;
                setStatus(status, msg, "#cc2e2e");
                alert(msg);
            } finally {
                btn.style.opacity = "1";
                btn.style.pointerEvents = "auto";
            }
        });
    }

    function bindTemplateButtons() {
        const saveBtn = document.getElementById("save-topup-template-btn");
        const loadBtn = document.getElementById("load-topup-template-btn");
        const status = document.getElementById("scrape-status");

        if (saveBtn && saveBtn.dataset.bound !== "true") {
            saveBtn.dataset.bound = "true";
            saveBtn.addEventListener("click", async function () {
                const topup = getFieldValue("id_topup_info");
                const topupTw = getFieldValue("id_topup_info_tw");
                if (!topup) {
                    alert("请先填写充值说明再保存模板");
                    return;
                }

                saveBtn.style.opacity = "0.5";
                saveBtn.style.pointerEvents = "none";
                setStatus(status, "正在保存默认充值模板...", "#666");
                try {
                    const data = await requestSaveTopupTemplate({
                        topup_info: topup,
                        topup_info_tw: topupTw || topup,
                    });
                    setStatus(status, data.message || "默认充值模板已保存。", "#14853b");
                } catch (err) {
                    console.error("save template failed:", err);
                    const msg = `保存模板失败：${err.message}`;
                    setStatus(status, msg, "#cc2e2e");
                    alert(msg);
                } finally {
                    saveBtn.style.opacity = "1";
                    saveBtn.style.pointerEvents = "auto";
                }
            });
        }

        if (loadBtn && loadBtn.dataset.bound !== "true") {
            loadBtn.dataset.bound = "true";
            loadBtn.addEventListener("click", async function () {
                loadBtn.style.opacity = "0.5";
                loadBtn.style.pointerEvents = "none";
                setStatus(status, "正在读取默认充值模板...", "#666");
                try {
                    const data = await requestLoadTopupTemplate();
                    const topup = (data.topup_info || "").trim();
                    const topupTw = (data.topup_info_tw || "").trim() || topup;
                    if (!topup) {
                        throw new Error("默认模板为空，请先保存模板");
                    }

                    const existing = getFieldValue("id_topup_info");
                    const existingTw = getFieldValue("id_topup_info_tw");
                    if ((existing || existingTw) && !window.confirm("当前充值说明已有内容，确认覆盖为默认模板吗？")) {
                        setStatus(status, "已取消覆盖模板。", "#666");
                        return;
                    }

                    fillField("id_topup_info", topup);
                    fillField("id_topup_info_tw", topupTw);
                    setStatus(status, "默认充值模板已套用。", "#14853b");
                } catch (err) {
                    console.error("load template failed:", err);
                    const msg = `套用模板失败：${err.message}`;
                    setStatus(status, msg, "#cc2e2e");
                    alert(msg);
                } finally {
                    loadBtn.style.opacity = "1";
                    loadBtn.style.pointerEvents = "auto";
                }
            });
        }
    }

    function init() {
        bindScrapeButton();
        bindTemplateButtons();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // SimpleUI 会动态替换 DOM，定时重绑确保按钮持续可用。
    setInterval(init, 1000);
})();
