(function () {
    const TARGET_TEXTAREA_IDS = ["id_content", "id_content_tw", "id_topup_info", "id_topup_info_tw"];
    const MODAL_ID = "gpc-media-picker-modal";
    const STYLE_ID = "gpc-content-enhancer-style";

    const state = {
        page: 1,
        search: "",
        category: "",
        results: [],
        selectedId: null,
        activeTextarea: null,
    };

    function ensureStyle() {
        if (document.getElementById(STYLE_ID)) return;
        const style = document.createElement("style");
        style.id = STYLE_ID;
        style.textContent = `
            .gpc-toolbar { display:flex; gap:8px; margin:8px 0 6px; flex-wrap:wrap; }
            .gpc-toolbar button { border:1px solid #d9d9d9; background:#fff; border-radius:4px; padding:4px 10px; cursor:pointer; }
            .gpc-toolbar button:hover { border-color:#1677ff; color:#1677ff; }
            .gpc-modal-backdrop { position:fixed; inset:0; background:rgba(0,0,0,.45); z-index:10000; display:none; }
            .gpc-modal { width:min(980px,92vw); max-height:86vh; background:#fff; border-radius:8px; margin:4vh auto; display:flex; flex-direction:column; overflow:hidden; }
            .gpc-modal-head { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-bottom:1px solid #f0f0f0; }
            .gpc-modal-body { padding:12px 16px; display:flex; flex-direction:column; gap:10px; overflow:auto; }
            .gpc-filter { display:flex; gap:8px; align-items:center; }
            .gpc-filter input, .gpc-filter select { height:32px; border:1px solid #d9d9d9; border-radius:4px; padding:0 8px; }
            .gpc-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:10px; }
            .gpc-card { border:1px solid #f0f0f0; border-radius:6px; overflow:hidden; cursor:pointer; background:#fff; }
            .gpc-card.selected { outline:2px solid #1677ff; border-color:#1677ff; }
            .gpc-card img { width:100%; height:95px; object-fit:cover; display:block; background:#fafafa; }
            .gpc-card .meta { padding:6px; font-size:12px; color:#666; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
            .gpc-modal-foot { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-top:1px solid #f0f0f0; }
            .gpc-btn { border:1px solid #d9d9d9; background:#fff; border-radius:4px; padding:6px 12px; cursor:pointer; }
            .gpc-btn.primary { background:#1677ff; color:#fff; border-color:#1677ff; }
            .gpc-status { color:#666; font-size:12px; }
        `;
        document.head.appendChild(style);
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function insertAtCursor(textarea, value) {
        if (!textarea) return;
        textarea.focus();

        const start = textarea.selectionStart || 0;
        const end = textarea.selectionEnd || 0;
        const before = textarea.value.slice(0, start);
        const after = textarea.value.slice(end);
        textarea.value = `${before}${value}${after}`;

        const nextPos = start + value.length;
        textarea.selectionStart = nextPos;
        textarea.selectionEnd = nextPos;
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        textarea.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function normalizeLinkUrl(url) {
        const raw = (url || "").trim();
        if (!raw) return "";
        if (/^(https?:\/\/|mailto:|\/)/i.test(raw)) return raw;
        return `https://${raw}`;
    }

    function insertLink(textarea) {
        const text = (window.prompt("请输入外显文字：") || "").trim();
        if (!text) return;
        const url = normalizeLinkUrl(window.prompt("请输入链接地址（支持 http(s)://、mailto: 或 /path）："));
        if (!url) return;
        insertAtCursor(textarea, `[${text}](${url})`);
    }

    function createModal() {
        if (document.getElementById(MODAL_ID)) return;

        const wrapper = document.createElement("div");
        wrapper.id = MODAL_ID;
        wrapper.className = "gpc-modal-backdrop";
        wrapper.innerHTML = `
            <div class="gpc-modal">
                <div class="gpc-modal-head">
                    <strong>从素材库插入图片</strong>
                    <button type="button" class="gpc-btn" data-close="1">关闭</button>
                </div>
                <div class="gpc-modal-body">
                    <div class="gpc-filter">
                        <input type="text" id="gpc-search-input" placeholder="按名称/Alt 搜索素材" />
                        <select id="gpc-category-select">
                            <option value="">全部分类</option>
                            <option value="icon">图标</option>
                            <option value="banner">横幅</option>
                            <option value="background">背景</option>
                            <option value="product">商品</option>
                            <option value="other">其他</option>
                        </select>
                        <button type="button" class="gpc-btn" id="gpc-search-btn">搜索</button>
                    </div>
                    <div class="gpc-grid" id="gpc-grid"></div>
                </div>
                <div class="gpc-modal-foot">
                    <div class="gpc-status" id="gpc-status">请选择一张图片</div>
                    <div style="display:flex;gap:8px;align-items:center;">
                        <button type="button" class="gpc-btn" id="gpc-prev-btn">上一页</button>
                        <span id="gpc-page-label">第 1 页</span>
                        <button type="button" class="gpc-btn" id="gpc-next-btn">下一页</button>
                        <button type="button" class="gpc-btn primary" id="gpc-insert-btn">插入图片</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(wrapper);

        wrapper.addEventListener("click", (event) => {
            if (event.target === wrapper || event.target.getAttribute("data-close") === "1") {
                closeModal();
            }
        });

        document.getElementById("gpc-search-btn").addEventListener("click", () => {
            state.search = document.getElementById("gpc-search-input").value.trim();
            state.category = document.getElementById("gpc-category-select").value;
            state.page = 1;
            loadMedia();
        });

        document.getElementById("gpc-prev-btn").addEventListener("click", () => {
            if (state.page <= 1) return;
            state.page -= 1;
            loadMedia();
        });

        document.getElementById("gpc-next-btn").addEventListener("click", () => {
            state.page += 1;
            loadMedia();
        });

        document.getElementById("gpc-insert-btn").addEventListener("click", () => {
            const picked = state.results.find((x) => String(x.id) === String(state.selectedId));
            if (!picked || !state.activeTextarea) {
                alert("请先选择一张图片");
                return;
            }
            const alt = (picked.alt_text || picked.name || "image").trim();
            const url = (picked.url || "").trim();
            if (!url) {
                alert("素材 URL 无效");
                return;
            }
            insertAtCursor(state.activeTextarea, `![${alt}](${url})`);
            closeModal();
        });
    }

    function closeModal() {
        const modal = document.getElementById(MODAL_ID);
        if (!modal) return;
        modal.style.display = "none";
        state.selectedId = null;
        state.results = [];
    }

    function renderMediaGrid() {
        const grid = document.getElementById("gpc-grid");
        const status = document.getElementById("gpc-status");
        const pageLabel = document.getElementById("gpc-page-label");
        if (!grid || !status || !pageLabel) return;

        pageLabel.textContent = `第 ${state.page} 页`;
        grid.innerHTML = "";
        if (!state.results.length) {
            status.textContent = "未找到素材";
            return;
        }

        status.textContent = `已加载 ${state.results.length} 条素材`;
        state.results.forEach((item) => {
            const card = document.createElement("div");
            card.className = "gpc-card";
            card.dataset.id = item.id;
            card.innerHTML = `
                <img src="${escapeHtml(item.thumbnail_url || item.url || "")}" alt="${escapeHtml(item.alt_text || item.name || "media")}" />
                <div class="meta">${escapeHtml(item.name || "未命名素材")}</div>
            `;
            card.addEventListener("click", () => {
                state.selectedId = item.id;
                grid.querySelectorAll(".gpc-card").forEach((el) => el.classList.remove("selected"));
                card.classList.add("selected");
                status.textContent = `已选择：${item.name || item.id}`;
            });
            grid.appendChild(card);
        });
    }

    async function loadMedia() {
        const status = document.getElementById("gpc-status");
        if (status) status.textContent = "正在加载素材...";
        const params = new URLSearchParams({
            page: String(state.page),
            search: state.search || "",
            category: state.category || "",
        });

        try {
            const resp = await fetch(`/api/media/?${params.toString()}`, {
                credentials: "same-origin",
                headers: { Accept: "application/json" },
            });
            const data = await resp.json();
            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status}`);
            }
            state.results = Array.isArray(data.results) ? data.results : [];
            renderMediaGrid();
        } catch (err) {
            console.error("load media failed:", err);
            state.results = [];
            renderMediaGrid();
            if (status) status.textContent = `加载素材失败：${err.message}`;
        }
    }

    function openModalForTextarea(textarea) {
        state.activeTextarea = textarea;
        state.page = 1;
        state.search = "";
        state.category = "";
        state.selectedId = null;

        createModal();
        const modal = document.getElementById(MODAL_ID);
        if (!modal) return;

        modal.style.display = "block";
        const searchInput = document.getElementById("gpc-search-input");
        const categorySelect = document.getElementById("gpc-category-select");
        if (searchInput) searchInput.value = "";
        if (categorySelect) categorySelect.value = "";
        loadMedia();
    }

    function bindToolbarToTextarea(textarea) {
        if (!textarea || textarea.dataset.gpcBound === "true") return;
        textarea.dataset.gpcBound = "true";

        const toolbar = document.createElement("div");
        toolbar.className = "gpc-toolbar";
        toolbar.innerHTML = `
            <button type="button" data-action="link">插入超链接</button>
            <button type="button" data-action="image">从素材库插入图片</button>
        `;
        toolbar.addEventListener("click", (event) => {
            const btn = event.target.closest("button[data-action]");
            if (!btn) return;
            const action = btn.getAttribute("data-action");
            if (action === "link") {
                insertLink(textarea);
            }
            if (action === "image") {
                openModalForTextarea(textarea);
            }
        });

        textarea.parentNode.insertBefore(toolbar, textarea);
    }

    function init() {
        ensureStyle();
        TARGET_TEXTAREA_IDS.forEach((id) => {
            const textarea = document.getElementById(id);
            if (textarea && textarea.tagName === "TEXTAREA") {
                bindToolbarToTextarea(textarea);
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // SimpleUI 动态刷新 DOM，定时扫描确保工具条存在。
    setInterval(init, 1000);
})();
