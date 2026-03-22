(function () {
  if (window.__galaxyAdminFloatingChatInitialized) {
    return;
  }
  window.__galaxyAdminFloatingChatInitialized = true;

  var API_BASE = "/api/customer-service/admin/chat";
  var POLL_MS = 5000;
  var state = {
    open: false,
    sessions: [],
    currentSessionId: "",
    sessionsLoading: false,
    detailLoading: false,
    pollTimer: null,
  };

  function $(root, selector) {
    return root.querySelector(selector);
  }

  function getCookie(name) {
    var pattern = new RegExp("(?:^|; )" + name.replace(/[.$?*|{}()[\]\\/+^]/g, "\\$&") + "=([^;]*)");
    var match = document.cookie.match(pattern);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function toNumber(value) {
    var num = Number(value);
    return Number.isFinite(num) ? num : 0;
  }

  function formatTime(value) {
    if (!value) {
      return "";
    }
    var date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return String(value);
    }
    return date.toLocaleString();
  }

  async function requestJson(url, options) {
    var opts = options || {};
    var method = (opts.method || "GET").toUpperCase();
    var headers = {};
    if (opts.headers) {
      Object.keys(opts.headers).forEach(function (key) {
        headers[key] = opts.headers[key];
      });
    }

    if (method !== "GET" && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
    if (method !== "GET") {
      headers["X-CSRFToken"] = getCookie("csrftoken");
    }

    var response = await fetch(url, {
      method: method,
      credentials: "same-origin",
      headers: headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });

    var text = await response.text();
    var payload = {};
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch (error) {
        payload = { raw: text };
      }
    }

    if (!response.ok) {
      var message =
        payload.detail ||
        payload.error ||
        payload.message ||
        (payload.raw ? String(payload.raw).slice(0, 120) : "") ||
        ("HTTP " + response.status);
      throw new Error(message);
    }

    return payload;
  }

  function statusClass(status) {
    if (status === "human") {
      return "gafc-human";
    }
    if (status === "closed") {
      return "gafc-closed";
    }
    return "";
  }

  function messageClass(senderType) {
    if (senderType === "user") {
      return "gafc-user";
    }
    if (senderType === "agent") {
      return "gafc-agent";
    }
    if (senderType === "ai") {
      return "gafc-ai";
    }
    return "gafc-system";
  }

  function createRoot() {
    var root = document.createElement("div");
    root.className = "gafc-root";
    root.id = "gafcRoot";
    root.innerHTML =
      '<button type="button" class="gafc-toggle" id="gafcToggle" title="客服会话">' +
      '<span>在线客服</span>' +
      '<span class="gafc-toggle-badge" id="gafcBadge"></span>' +
      "</button>" +
      '<section class="gafc-panel" id="gafcPanel" aria-hidden="true">' +
      '<header class="gafc-header">' +
      '<div class="gafc-title">' +
      "<strong>在线客服</strong>" +
      '<span id="gafcHeaderHint">加载中...</span>' +
      "</div>" +
      '<div class="gafc-header-actions">' +
      '<button type="button" class="gafc-icon-btn" id="gafcOpenConsole" title="打开完整控制台">全屏</button>' +
      '<button type="button" class="gafc-icon-btn" id="gafcMinimize" title="最小化">最小</button>' +
      "</div>" +
      "</header>" +
      '<div class="gafc-main">' +
      '<aside class="gafc-sessions" id="gafcSessions"></aside>' +
      '<section class="gafc-thread">' +
      '<div class="gafc-meta" id="gafcMeta">请选择一个会话</div>' +
      '<div class="gafc-messages" id="gafcMessages"><div class="gafc-empty">等待数据中</div></div>' +
      '<div class="gafc-compose">' +
      '<textarea class="gafc-reply" id="gafcReply" placeholder="请输入回复（Enter发送，Shift+Enter换行）"></textarea>' +
      '<div class="gafc-compose-actions">' +
      '<button type="button" class="gafc-btn" id="gafcAssign">接单</button>' +
      '<button type="button" class="gafc-btn gafc-btn-danger" id="gafcClose">关闭</button>' +
      '<button type="button" class="gafc-btn gafc-btn-primary" id="gafcSend">发送</button>' +
      "</div>" +
      "</div>" +
      "</section>" +
      "</div>" +
      "</section>";
    document.body.appendChild(root);
    return root;
  }

  var root = createRoot();
  var els = {
    root: root,
    toggle: $(root, "#gafcToggle"),
    badge: $(root, "#gafcBadge"),
    panel: $(root, "#gafcPanel"),
    sessions: $(root, "#gafcSessions"),
    headerHint: $(root, "#gafcHeaderHint"),
    meta: $(root, "#gafcMeta"),
    messages: $(root, "#gafcMessages"),
    reply: $(root, "#gafcReply"),
    send: $(root, "#gafcSend"),
    assign: $(root, "#gafcAssign"),
    close: $(root, "#gafcClose"),
    minimize: $(root, "#gafcMinimize"),
    openConsole: $(root, "#gafcOpenConsole"),
  };

  function totalUnread() {
    return state.sessions.reduce(function (sum, item) {
      return sum + toNumber(item.unread_user_count);
    }, 0);
  }

  function setOpen(open) {
    state.open = !!open;
    els.root.classList.toggle("gafc-open", state.open);
    els.panel.setAttribute("aria-hidden", state.open ? "false" : "true");
  }

  function renderHeaderHint() {
    var unread = totalUnread();
    if (unread > 0) {
      els.headerHint.textContent = "待处理：" + unread;
    } else {
      els.headerHint.textContent = "暂无未读消息";
    }
  }

  function renderBadge() {
    var unread = totalUnread();
    if (unread > 0) {
      els.root.classList.add("gafc-has-unread");
      els.badge.textContent = unread > 99 ? "99+" : String(unread);
    } else {
      els.root.classList.remove("gafc-has-unread");
      els.badge.textContent = "";
    }
    renderHeaderHint();
  }

  function renderMeta(session) {
    if (!session) {
      els.meta.textContent = "请选择一个会话";
      return;
    }
    var visitorName = session.visitor_name || "匿名访客";
    var statusValue = session.status_display || session.status || "-";
    var agentName = session.assigned_agent_name || "-";
    els.meta.innerHTML =
      "<strong>访客：</strong> " +
      escapeHtml(visitorName) +
      '<span style="margin-left:10px;"><strong>状态：</strong> ' +
      escapeHtml(statusValue) +
      '</span><span style="margin-left:10px;"><strong>客服：</strong> ' +
      escapeHtml(agentName) +
      "</span>";
  }

  function renderMessages(messages) {
    if (!Array.isArray(messages) || messages.length === 0) {
      els.messages.innerHTML = '<div class="gafc-empty">暂无消息</div>';
      return;
    }

    els.messages.innerHTML = messages
      .map(function (item) {
        var senderType = item.sender_type || "system";
        return (
          '<div class="gafc-message ' +
          messageClass(senderType) +
          '">' +
          "<div>" +
          escapeHtml(item.content || "") +
          "</div>" +
          '<div class="gafc-message-meta">' +
          escapeHtml(item.sender_name || item.sender_type_display || senderType) +
          " | " +
          escapeHtml(formatTime(item.created_at)) +
          "</div>" +
          "</div>"
        );
      })
      .join("");

    els.messages.scrollTop = els.messages.scrollHeight;
  }

  function renderSessionList() {
    if (!state.sessions.length) {
      els.sessions.innerHTML = '<div class="gafc-empty">暂无活跃会话</div>';
      return;
    }

    els.sessions.innerHTML = state.sessions
      .map(function (item) {
        var active = String(item.session_id) === String(state.currentSessionId) ? "gafc-active" : "";
        var unread = toNumber(item.unread_user_count);
        var visitor = item.visitor_name || "匿名访客";
        var preview = item.last_message_preview || "暂无消息";
        var lastTime = formatTime(item.last_message_at || item.updated_at || "");
        return (
          '<div class="gafc-session-item ' +
          active +
          '" data-session-id="' +
          item.session_id +
          '">' +
          '<div class="gafc-session-top"><span class="gafc-session-title">' +
          escapeHtml(visitor) +
          '</span><span class="gafc-status ' +
          statusClass(item.status) +
          '">' +
          escapeHtml(item.status_display || item.status || "会话") +
          "</span></div>" +
          '<div class="gafc-session-preview">' +
          escapeHtml(preview) +
          '</div><div class="gafc-session-meta"><span>' +
          escapeHtml(lastTime) +
          "</span>" +
          (unread > 0
            ? '<span class="gafc-unread-dot">' + (unread > 99 ? "99+" : unread) + "</span>"
            : "<span></span>") +
          "</div></div>"
        );
      })
      .join("");

    Array.prototype.forEach.call(els.sessions.querySelectorAll(".gafc-session-item"), function (node) {
      node.addEventListener("click", function () {
        var sessionId = node.getAttribute("data-session-id") || "";
        if (!sessionId) {
          return;
        }
        state.currentSessionId = sessionId;
        renderSessionList();
        refreshSessionDetail(false).catch(function (error) {
          setMetaError(error);
        });
      });
    });
  }

  function ensureSessionSelected() {
    if (!state.currentSessionId) {
      setMetaError(new Error("请先选择一个会话。"));
      return false;
    }
    return true;
  }

  function setMetaError(error) {
    var message = (error && error.message) || "请求失败。";
    els.meta.textContent = message;
  }

  function normalizeSessions(rows) {
    return rows
      .filter(function (item) {
        return item.status !== "closed";
      })
      .sort(function (a, b) {
        var unreadDiff = toNumber(b.unread_user_count) - toNumber(a.unread_user_count);
        if (unreadDiff !== 0) {
          return unreadDiff;
        }
        var waitingDiff = toNumber(Boolean(b.is_user_waiting)) - toNumber(Boolean(a.is_user_waiting));
        if (waitingDiff !== 0) {
          return waitingDiff;
        }
        var t1 = new Date(a.updated_at || 0).getTime();
        var t2 = new Date(b.updated_at || 0).getTime();
        return t2 - t1;
      });
  }

  async function refreshSessions() {
    if (state.sessionsLoading) {
      return;
    }

    state.sessionsLoading = true;
    try {
      var data = await requestJson(API_BASE + "/sessions/");
      state.sessions = normalizeSessions(Array.isArray(data.results) ? data.results : []);

      if (
        !state.currentSessionId ||
        !state.sessions.some(function (item) {
          return String(item.session_id) === String(state.currentSessionId);
        })
      ) {
        state.currentSessionId = state.sessions.length ? state.sessions[0].session_id : "";
      }

      renderSessionList();
      renderBadge();

      if (state.open && state.currentSessionId) {
        await refreshSessionDetail(true);
      }
    } catch (error) {
      els.headerHint.textContent = "聊天接口不可用";
    } finally {
      state.sessionsLoading = false;
    }
  }

  async function refreshSessionDetail(silent) {
    if (!state.currentSessionId || state.detailLoading) {
      return;
    }

    state.detailLoading = true;
    try {
      var detail = await requestJson(API_BASE + "/sessions/" + state.currentSessionId + "/");
      renderMeta(detail);
      renderMessages(Array.isArray(detail.messages) ? detail.messages : []);

      var index = state.sessions.findIndex(function (item) {
        return String(item.session_id) === String(state.currentSessionId);
      });
      if (index >= 0) {
        var previous = state.sessions[index];
        var lastMessage = detail.messages && detail.messages.length ? detail.messages[detail.messages.length - 1] : null;
        state.sessions[index] = Object.assign({}, previous, {
          status: detail.status,
          status_display: detail.status_display,
          assigned_agent_name: detail.assigned_agent_name,
          unread_user_count: 0,
          last_message_preview: lastMessage ? lastMessage.content : previous.last_message_preview,
          last_message_at: lastMessage ? lastMessage.created_at : previous.last_message_at,
        });
        renderSessionList();
        renderBadge();
      }
    } catch (error) {
      if (!silent) {
        setMetaError(error);
      }
    } finally {
      state.detailLoading = false;
    }
  }

  async function replyCurrent() {
    if (!ensureSessionSelected()) {
      return;
    }
    var content = String(els.reply.value || "").trim();
    if (!content) {
      return;
    }

    els.send.disabled = true;
    try {
      await requestJson(API_BASE + "/sessions/" + state.currentSessionId + "/reply/", {
        method: "POST",
        body: { content: content },
      });
      els.reply.value = "";
      await refreshSessions();
      await refreshSessionDetail(true);
    } catch (error) {
      setMetaError(error);
    } finally {
      els.send.disabled = false;
    }
  }

  async function assignCurrent() {
    if (!ensureSessionSelected()) {
      return;
    }
    els.assign.disabled = true;
    try {
      await requestJson(API_BASE + "/sessions/" + state.currentSessionId + "/assign/", {
        method: "POST",
        body: {},
      });
      await refreshSessions();
      await refreshSessionDetail(true);
    } catch (error) {
      setMetaError(error);
    } finally {
      els.assign.disabled = false;
    }
  }

  async function closeCurrent() {
    if (!ensureSessionSelected()) {
      return;
    }
    if (!window.confirm("确认关闭该会话吗？")) {
      return;
    }
    els.close.disabled = true;
    try {
      await requestJson(API_BASE + "/sessions/" + state.currentSessionId + "/close/", {
        method: "POST",
        body: {},
      });
      state.currentSessionId = "";
      renderMeta(null);
      renderMessages([]);
      await refreshSessions();
    } catch (error) {
      setMetaError(error);
    } finally {
      els.close.disabled = false;
    }
  }

  function startPolling() {
    if (state.pollTimer) {
      clearInterval(state.pollTimer);
    }
    state.pollTimer = window.setInterval(function () {
      refreshSessions().catch(function () {});
    }, POLL_MS);
  }

  els.toggle.addEventListener("click", function () {
    setOpen(true);
    refreshSessions().catch(function () {});
  });

  els.minimize.addEventListener("click", function () {
    setOpen(false);
  });

  els.openConsole.addEventListener("click", function () {
    window.open("/admin/customer_service/chatsession/console/", "_blank");
  });

  els.send.addEventListener("click", function () {
    replyCurrent().catch(function () {});
  });

  els.assign.addEventListener("click", function () {
    assignCurrent().catch(function () {});
  });

  els.close.addEventListener("click", function () {
    closeCurrent().catch(function () {});
  });

  els.reply.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      replyCurrent().catch(function () {});
    }
  });

  refreshSessions().catch(function () {});
  startPolling();
})();
