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

    function parsePackageIdFromUrl(url) {
        try {
            const u = new URL(url);
            return u.searchParams.get("id") || "";
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
        const resp = await fetch(`/admin/game_page/gamepage/scrape-google-play/?url=${encodeURIComponent(url)}`, {
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        });

        let data = null;
        try {
            data = await resp.json();
        } catch (e) {
            throw new Error(`抓取接口返回了非 JSON 响应 (HTTP ${resp.status})`);
        }

        if (!resp.ok || (data && data.error)) {
            throw new Error((data && data.error) || `抓取失败 (HTTP ${resp.status})`);
        }
        return data || {};
    }

    function initScraper() {
        const btn = document.getElementById("scrape-btn");
        const input = document.getElementById("google-play-url");
        const status = document.getElementById("scrape-status");

        if (!btn || !input || !status) {
            return;
        }

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

                // 基础字段
                fillField("id_title", title);
                fillField("id_developer", data.developer);
                fillField("id_google_play_id", packageId);
                fillField("id_icon_external_url", data.icon_external_url || data.icon_url || "");
                fillField("id_description", fallbackDescription);
                fillField("id_description_tw", fallbackDescription);

                // 内容字段：确保“游戏详情”不再空白
                fillField("id_content", fallbackContent);
                fillField("id_content_tw", fallbackContent);

                // 充值说明：仅在空白时填入默认模板
                const topupTemplate = data.topup_info_template || DEFAULT_TOPUP_INFO;
                if (!getFieldValue("id_topup_info")) {
                    fillField("id_topup_info", topupTemplate);
                }
                if (!getFieldValue("id_topup_info_tw")) {
                    fillField("id_topup_info_tw", topupTemplate);
                }

                // 如果 SEO 标题为空，顺便补齐
                const seoTitle = document.getElementById("id_seo_title");
                if (seoTitle && !seoTitle.value && title) {
                    seoTitle.value = `${title}代储_充值 - MEME港台游戏工具箱`;
                }

                if (data.warning) {
                    setStatus(status, `已填充基础信息（提示：${data.warning}）`, "#d97706");
                } else if (data.source === "jina_proxy") {
                    setStatus(status, "导入成功（已提取 Google Play 游戏简介并填充详情）。", "#14853b");
                } else if (data.media_id) {
                    setStatus(
                        status,
                        `导入成功。图标已保存到素材库 (ID: ${data.media_id})，请在“游戏图标”处点“从素材库选择”。`,
                        "#14853b"
                    );
                } else {
                    setStatus(status, "导入成功（未获取到图标）。", "#14853b");
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

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initScraper);
    } else {
        initScraper();
    }

    // SimpleUI 会动态替换页面内容，定时重绑可保证按钮始终可用。
    setInterval(initScraper, 1000);
})();
