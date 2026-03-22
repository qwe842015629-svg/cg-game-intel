(function () {
  const TARGET_PAGE_CLASS = 'change-form';
  const NAME_RE =
    /(content|body|description|summary|excerpt|topup|meta_description|html|prompt|answer|message|notes|intro|detail|remark)/i;
  const EXPECT_EXTERNAL_TOOLBAR_IDS = new Set(['id_content', 'id_content_tw', 'id_topup_info', 'id_topup_info_tw']);

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function sanitizeHtml(html) {
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(`<div data-uai-sanitize-root="1">${String(html || '')}</div>`, 'text/html');
      const root = doc.querySelector('[data-uai-sanitize-root="1"]') || doc.body;
      root.querySelectorAll('script, style, iframe, object, embed').forEach((node) => node.remove());

      // Legacy rich text may contain center tags; convert them to neutral containers.
      root.querySelectorAll('center').forEach((node) => {
        const neutral = doc.createElement('div');
        while (node.firstChild) {
          neutral.appendChild(node.firstChild);
        }
        node.replaceWith(neutral);
      });

      root.querySelectorAll('*').forEach((el) => {
        Array.from(el.attributes).forEach((attr) => {
          const attrName = String(attr.name || '').toLowerCase();
          const attrValue = String(attr.value || '');
          if (/^on/i.test(attrName)) {
            el.removeAttribute(attr.name);
          }
          if ((attrName === 'href' || attrName === 'src') && /^javascript:/i.test(attrValue)) {
            el.removeAttribute(attr.name);
          }
          // Preview should stay product-stable; remove inline styles that frequently break list/text layout.
          if (attrName === 'style') {
            el.removeAttribute(attr.name);
          }
          // Keep media sizing attributes for images/videos, drop legacy align attributes.
          if (attrName === 'align') {
            el.removeAttribute(attr.name);
          }
          // Preview should not inherit historical editor classes/ids/data-* attributes.
          if (attrName === 'class' || attrName === 'id' || attrName.startsWith('data-')) {
            el.removeAttribute(attr.name);
          }
        });
      });
      return root.innerHTML;
    } catch (error) {
      return escapeHtml(html || '');
    }
  }

  function normalizePreviewContent(previewContent) {
    if (!previewContent) return;
    const leadingSpaces = /^[\t \u00a0\u2000-\u200b\u3000]{2,}/gm;
    const lineLeadingSpaces = /\n[\t \u00a0\u2000-\u200b\u3000]{2,}/g;
    const walker = document.createTreeWalker(previewContent, NodeFilter.SHOW_TEXT, null);
    let node = walker.nextNode();
    while (node) {
      const parent = node.parentElement;
      if (parent && !parent.closest('pre, code')) {
        const value = String(node.textContent || '');
        const normalized = value
          .replace(leadingSpaces, '')
          .replace(lineLeadingSpaces, '\n')
          .replace(/\u200b/g, '');
        if (normalized !== value) {
          node.textContent = normalized;
        }
      }
      node = walker.nextNode();
    }

    previewContent.querySelectorAll('li').forEach((item) => {
      const first = item.firstChild;
      if (!first || first.nodeType !== Node.TEXT_NODE) return;
      const value = String(first.textContent || '');
      const normalized = value.replace(/^[\t \u00a0\u2000-\u200b\u3000]+/, '');
      if (normalized !== value) {
        first.textContent = normalized;
      }
    });
  }

  function applyInlineMarkdown(line) {
    let text = escapeHtml(line);
    text = text.replace(/!\[([^\]]*)\]\(([^\)\s]+)\)/g, '<img alt="$1" src="$2" />');
    text = text.replace(/\[([^\]]+)\]\(([^\)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    text = text.replace(/~~([^~]+)~~/g, '<del>$1</del>');
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    return text;
  }

  function parseTableBlock(blockLines) {
    if (blockLines.length < 2) return null;
    const header = blockLines[0].trim();
    const divider = blockLines[1].trim();
    if (!header.includes('|') || !/^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(divider)) {
      return null;
    }

    const toCells = (row) =>
      row
        .trim()
        .replace(/^\|/, '')
        .replace(/\|$/, '')
        .split('|')
        .map((cell) => applyInlineMarkdown(cell.trim()));

    const headCells = toCells(header);
    const bodyRows = blockLines.slice(2).map(toCells);

    let html = '<table><thead><tr>';
    headCells.forEach((cell) => {
      html += `<th>${cell}</th>`;
    });
    html += '</tr></thead><tbody>';

    bodyRows.forEach((row) => {
      if (!row.length) return;
      html += '<tr>';
      row.forEach((cell) => {
        html += `<td>${cell}</td>`;
      });
      html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
  }

  function markdownToHtml(raw) {
    const source = String(raw || '').replace(/\r\n/g, '\n');
    if (!source.trim()) {
      return '<p class="uai-lite-empty">暂无内容预览</p>';
    }

    const codeBlocks = [];
    let normalized = source.replace(/```([\s\S]*?)```/g, function (_, code) {
      const token = `__UAI_CODE_BLOCK_${codeBlocks.length}__`;
      codeBlocks.push(`<pre><code>${escapeHtml(code)}</code></pre>`);
      return token;
    });

    const blocks = normalized.split(/\n{2,}/).map((part) => part.split('\n'));
    const htmlBlocks = [];

    blocks.forEach((blockLines) => {
      if (!blockLines.length) return;
      const firstLine = blockLines[0].trim();
      if (!firstLine) return;

      if (/^__UAI_CODE_BLOCK_\d+__$/.test(firstLine) && blockLines.length === 1) {
        htmlBlocks.push(firstLine);
        return;
      }

      const table = parseTableBlock(blockLines);
      if (table) {
        htmlBlocks.push(table);
        return;
      }

      if (/^#{1,6}\s+/.test(firstLine) && blockLines.length === 1) {
        const level = Math.min((firstLine.match(/^#+/) || ['#'])[0].length, 6);
        const text = firstLine.replace(/^#{1,6}\s+/, '');
        htmlBlocks.push(`<h${level}>${applyInlineMarkdown(text)}</h${level}>`);
        return;
      }

      if (/^(-{3,}|\*{3,})$/.test(firstLine) && blockLines.length === 1) {
        htmlBlocks.push('<hr />');
        return;
      }

      if (blockLines.every((line) => /^>\s?/.test(line.trim()))) {
        const quote = blockLines.map((line) => applyInlineMarkdown(line.replace(/^>\s?/, ''))).join('<br>');
        htmlBlocks.push(`<blockquote>${quote}</blockquote>`);
        return;
      }

      if (blockLines.every((line) => /^[-*+]\s+/.test(line.trim()))) {
        const items = blockLines
          .map((line) => line.trim().replace(/^[-*+]\s+/, ''))
          .map((line) => `<li>${applyInlineMarkdown(line)}</li>`)
          .join('');
        htmlBlocks.push(`<ul>${items}</ul>`);
        return;
      }

      if (blockLines.every((line) => /^\d+\.\s+/.test(line.trim()))) {
        const items = blockLines
          .map((line) => line.trim().replace(/^\d+\.\s+/, ''))
          .map((line) => `<li>${applyInlineMarkdown(line)}</li>`)
          .join('');
        htmlBlocks.push(`<ol>${items}</ol>`);
        return;
      }

      const paragraph = blockLines.map((line) => applyInlineMarkdown(line)).join('<br>');
      htmlBlocks.push(`<p>${paragraph}</p>`);
    });

    let html = htmlBlocks.join('\n');
    codeBlocks.forEach((codeHtml, index) => {
      html = html.replace(`__UAI_CODE_BLOCK_${index}__`, codeHtml);
    });
    return html;
  }

  function formatBytes(bytes) {
    const value = Number(bytes || 0);
    if (value < 1024) return `${value} B`;
    if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
    return `${(value / 1024 / 1024).toFixed(2)} MB`;
  }

  function insertAtCursor(textarea, value) {
    if (!textarea) return;
    textarea.focus();

    const start = textarea.selectionStart || 0;
    const end = textarea.selectionEnd || 0;
    const before = textarea.value.slice(0, start);
    const after = textarea.value.slice(end);

    textarea.value = `${before}${value}${after}`;
    const cursor = start + value.length;
    textarea.setSelectionRange(cursor, cursor);
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    textarea.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function wrapSelection(textarea, prefix, suffix, fallbackText) {
    if (!textarea) return;
    textarea.focus();

    const start = textarea.selectionStart || 0;
    const end = textarea.selectionEnd || 0;
    const selected = textarea.value.slice(start, end) || fallbackText || '';
    const next = `${prefix}${selected}${suffix}`;

    const before = textarea.value.slice(0, start);
    const after = textarea.value.slice(end);
    textarea.value = `${before}${next}${after}`;

    const cursorStart = start + prefix.length;
    const cursorEnd = cursorStart + selected.length;
    textarea.setSelectionRange(cursorStart, cursorEnd);
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    textarea.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function makeButton(label, action, title) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'uai-lite-btn';
    button.textContent = label;
    button.dataset.action = action;
    if (title) button.title = title;
    return button;
  }

  function createFormatSelect(textarea) {
    const select = document.createElement('select');
    select.className = 'uai-lite-select';
    select.innerHTML = [
      '<option value="">正文</option>',
      '<option value="h2">标题 1 (H2)</option>',
      '<option value="h3">标题 2 (H3)</option>',
      '<option value="quote">引用</option>',
      '<option value="code">代码块</option>',
      '<option value="hr">分隔线</option>',
    ].join('');

    select.addEventListener('change', () => {
      const value = select.value;
      if (!value) return;
      if (value === 'h2') insertAtCursor(textarea, '\n## 小节标题\n');
      if (value === 'h3') insertAtCursor(textarea, '\n### 三级标题\n');
      if (value === 'quote') insertAtCursor(textarea, '\n> 引用内容\n');
      if (value === 'code') insertAtCursor(textarea, '\n```\ncode snippet\n```\n');
      if (value === 'hr') insertAtCursor(textarea, '\n---\n');
      select.value = '';
    });

    return select;
  }

  function getDraftTitleForAI(textarea) {
    const titleSelectors = ['#id_title', '#id_title_tw', 'input[name="title"]', 'input[name="title_tw"]'];
    for (const selector of titleSelectors) {
      const input = document.querySelector(selector);
      if (input && String(input.value || '').trim()) {
        return String(input.value || '').trim().slice(0, 60);
      }
    }
    return findFieldTitle(textarea) || '游戏内容';
  }

  function stripHtmlTags(value) {
    const source = String(value || '');
    if (!source.trim()) return '';
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(`<div>${source}</div>`, 'text/html');
      const text = String(doc.body.textContent || '');
      return text.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
    } catch (error) {
      return source.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    }
  }

  function buildLocalSmartTypesetHtml(rawText) {
    const source = String(rawText || '').replace(/\r\n/g, '\n').trim();
    if (!source) return '';
    if (/<[a-z][\s\S]*>/i.test(source)) {
      return sanitizeHtml(source);
    }

    const lines = source.split('\n').map((line) => line.trim());
    const blocks = [];
    const paragraph = [];

    const flushParagraph = () => {
      if (!paragraph.length) return;
      let text = paragraph.join(' ');
      if (text.length > 18 && !/[。！？.!?]$/.test(text)) {
        text += '。';
      }
      blocks.push(text);
      paragraph.length = 0;
    };

    lines.forEach((line, idx) => {
      if (!line) {
        flushParagraph();
        return;
      }
      const isStructured = /^#{1,6}\s+/.test(line) || /^[-*+]\s+/.test(line) || /^\d+\.\s+/.test(line) || /^>\s?/.test(line);
      if (isStructured) {
        flushParagraph();
        blocks.push(line);
        return;
      }
      if (idx === 0 && line.length <= 32) {
        flushParagraph();
        blocks.push(`## ${line}`);
        return;
      }
      paragraph.push(line);
    });
    flushParagraph();

    if (!blocks.length) return '';
    if (!/^#{1,6}\s+/.test(blocks[0])) {
      blocks.unshift('## 内容导读');
    }

    return markdownToHtml(blocks.join('\n\n'));
  }

  async function requestAiTypeset({ rawText, gameName }) {
    const endpoint = '/api/seo-automation/rewrite/';
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 45000);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        credentials: 'omit',
        signal: controller.signal,
        body: JSON.stringify({
          raw_text: String(rawText || ''),
          game_name: String(gameName || '游戏内容').slice(0, 80),
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
        const detail =
          (typeof data.detail === 'string' && data.detail) ||
          (typeof data.error === 'string' && data.error) ||
          `HTTP ${response.status}`;
        throw new Error(detail);
      }

      const bodyHtml = String(data.body_html || '').trim();
      if (!bodyHtml) {
        throw new Error('empty_body_html');
      }
      return {
        html: sanitizeHtml(bodyHtml),
        diagnostics: typeof data.diagnostics === 'object' && data.diagnostics ? data.diagnostics : {},
      };
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  async function runAiTypesetAction(textarea, triggerButton, shellContext) {
    if (!textarea || !triggerButton) return;

    const source = String(textarea.value || '');
    if (!source.trim()) {
      if (shellContext && shellContext.statusRight) {
        shellContext.statusRight.textContent = '没有可排版内容';
      }
      return;
    }
    if (triggerButton.dataset.uaiLoading === 'true') return;

    const statusRight = shellContext && shellContext.statusRight ? shellContext.statusRight : null;
    const refresh = shellContext && typeof shellContext.refresh === 'function' ? shellContext.refresh : null;
    const defaultHint = statusRight ? String(statusRight.textContent || '') : '';

    triggerButton.dataset.uaiLoading = 'true';
    triggerButton.disabled = true;
    triggerButton.classList.add('is-loading');
    if (statusRight) {
      statusRight.textContent = 'AI排版处理中...';
    }

    const gameName = getDraftTitleForAI(textarea);
    const rawText = /<[a-z][\s\S]*>/i.test(source) ? stripHtmlTags(source) : source;

    let nextValue = '';
    let hint = '';
    try {
      const aiResult = await requestAiTypeset({ rawText, gameName });
      nextValue = aiResult.html;
      const diagnostics = aiResult.diagnostics || {};
      hint = diagnostics.fallback ? `AI排版完成（${diagnostics.reason || 'fallback'}）` : 'AI排版完成';
    } catch (error) {
      nextValue = buildLocalSmartTypesetHtml(rawText);
      hint = 'AI服务暂不可用，已切换本地智能排版';
    }

    if (!String(nextValue || '').trim()) {
      nextValue = source;
    }

    textarea.value = nextValue;
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    textarea.dispatchEvent(new Event('change', { bubbles: true }));
    if (refresh) refresh();

    if (statusRight) {
      statusRight.textContent = hint;
      window.setTimeout(() => {
        if (!statusRight) return;
        if (statusRight.textContent !== hint) return;
        statusRight.textContent = defaultHint || '快捷键: Ctrl+B / Ctrl+I / Ctrl+K';
      }, 4200);
    }

    triggerButton.classList.remove('is-loading');
    triggerButton.disabled = false;
    triggerButton.dataset.uaiLoading = 'false';
  }

  function createDefaultToolbar(textarea, shellContext = {}) {
    const wrapper = document.createElement('div');
    wrapper.className = 'uai-lite-toolbar-main';

    const groupFormat = document.createElement('div');
    groupFormat.className = 'uai-lite-toolbar-group';
    groupFormat.appendChild(createFormatSelect(textarea));

    const groupInline = document.createElement('div');
    groupInline.className = 'uai-lite-toolbar-group';
    [
      makeButton('B', 'bold', '粗体 (Ctrl+B)'),
      makeButton('I', 'italic', '斜体 (Ctrl+I)'),
      makeButton('Link', 'link', '插入链接 (Ctrl+K)'),
      makeButton('Image', 'image', '插入图片'),
    ].forEach((item) => groupInline.appendChild(item));

    const groupBlock = document.createElement('div');
    groupBlock.className = 'uai-lite-toolbar-group';
    [makeButton('UL', 'ul'), makeButton('OL', 'ol'), makeButton('Table', 'table'), makeButton('Code', 'code')].forEach(
      (item) => groupBlock.appendChild(item)
    );

    const groupTpl = document.createElement('div');
    groupTpl.className = 'uai-lite-toolbar-group';
    [
      makeButton('模板:公告', 'tpl-notice'),
      makeButton('模板:FAQ', 'tpl-faq'),
      makeButton('模板:步骤', 'tpl-steps'),
    ].forEach((item) => groupTpl.appendChild(item));

    const groupAI = document.createElement('div');
    groupAI.className = 'uai-lite-toolbar-group';
    groupAI.appendChild(makeButton('一键AI排版', 'ai-typeset', '调用 AI 自动完成排版与结构整理'));

    wrapper.appendChild(groupFormat);
    wrapper.appendChild(groupInline);
    wrapper.appendChild(groupBlock);
    wrapper.appendChild(groupTpl);
    wrapper.appendChild(groupAI);

    wrapper.addEventListener('click', async (event) => {
      const target = event.target.closest('button[data-action]');
      if (!target) return;

      const action = target.dataset.action;
      if (action === 'ai-typeset') {
        await runAiTypesetAction(textarea, target, shellContext);
        return;
      }

      if (action === 'bold') wrapSelection(textarea, '**', '**', '粗体文本');
      if (action === 'italic') wrapSelection(textarea, '*', '*', '斜体文本');
      if (action === 'code') insertAtCursor(textarea, '\n```\ncode snippet\n```\n');
      if (action === 'ul') insertAtCursor(textarea, '\n- 列表项\n');
      if (action === 'ol') insertAtCursor(textarea, '\n1. 列表项\n');
      if (action === 'table') insertAtCursor(textarea, '\n| 列1 | 列2 |\n| --- | --- |\n| 内容 | 内容 |\n');

      if (action === 'link') {
        const text = (window.prompt('链接文本') || '').trim() || '链接';
        const url = (window.prompt('链接地址') || '').trim();
        if (!url) return;
        insertAtCursor(textarea, `[${text}](${url})`);
      }

      if (action === 'image') {
        if (typeof window.uaiOpenContentMediaPicker === 'function') {
          window.uaiOpenContentMediaPicker(textarea);
          return;
        }
        const alt = (window.prompt('图片说明') || '').trim() || 'image';
        const url = (window.prompt('图片地址') || '').trim();
        if (!url) return;
        insertAtCursor(textarea, `\n![${alt}](${url})\n`);
      }

      if (action === 'tpl-notice') {
        insertAtCursor(
          textarea,
          '\n> [公告]\n> 1. 这里填写维护或版本信息。\n> 2. 建议补充开始/结束时间与影响范围。\n'
        );
      }

      if (action === 'tpl-faq') {
        insertAtCursor(
          textarea,
          '\n## 常见问题 FAQ\n\n### Q1: 问题示例？\nA: 这里填写答案。\n\n### Q2: 问题示例？\nA: 这里填写答案。\n'
        );
      }

      if (action === 'tpl-steps') {
        insertAtCursor(
          textarea,
          '\n## 操作步骤\n1. 第一步：\n2. 第二步：\n3. 第三步：\n'
        );
      }
    });

    return wrapper;
  }

  function findFieldTitle(textarea) {
    const row = textarea.closest('.form-row, .fieldBox, .form-group') || textarea.parentElement;
    if (!row) return textarea.name || textarea.id || '富文本编辑器';

    const label = row.querySelector('label');
    if (label) {
      return String(label.textContent || '').replace(/[:：]\s*$/, '').trim() || '富文本编辑器';
    }
    return textarea.name || textarea.id || '富文本编辑器';
  }

  function shouldEnhance(textarea) {
    if (!textarea || textarea.tagName !== 'TEXTAREA') return false;
    if (textarea.dataset.uaiEnhanced === 'true') return false;
    if (textarea.dataset.uaiBridge === 'off') return false;
    if (textarea.disabled || textarea.readOnly) return false;
    if (textarea.closest('#changelist')) return false;

    const id = textarea.id || '';
    const name = textarea.name || '';
    const rows = Number(textarea.getAttribute('rows') || 0);
    const title = findFieldTitle(textarea);

    if (NAME_RE.test(id) || NAME_RE.test(name) || NAME_RE.test(title)) return true;
    if (rows >= 4) return true;
    if ((textarea.value || '').length >= 120) return true;
    return false;
  }

  function syncStatus(textarea, statusLeft, statusRight, topMeta) {
    const text = String(textarea.value || '');
    const lineCount = text ? text.split('\n').length : 0;
    const charCount = text.length;
    const bytes = new Blob([text]).size;
    const wordCount = text
      .replace(/[\u4e00-\u9fa5]/g, ' $& ')
      .trim()
      .split(/\s+/)
      .filter(Boolean).length;

    statusLeft.textContent = `字符 ${charCount} · 行数 ${lineCount} · 词数 ${wordCount}`;
    statusRight.textContent = '快捷键: Ctrl+B / Ctrl+I / Ctrl+K';
    topMeta.textContent = `${formatBytes(bytes)} · ${/<[a-z][\s\S]*>/i.test(text) ? 'HTML' : 'Markdown'}`;
  }

  function renderPreview(textarea, previewContent) {
    const value = String(textarea.value || '');
    if (!value.trim()) {
      previewContent.innerHTML = '<p class="uai-lite-empty">暂无内容预览</p>';
      return;
    }

    const looksLikeHtml = /<[a-z][\s\S]*>/i.test(value);
    if (looksLikeHtml) {
      previewContent.innerHTML = sanitizeHtml(value);
      normalizePreviewContent(previewContent);
      return;
    }
    previewContent.innerHTML = markdownToHtml(value);
    normalizePreviewContent(previewContent);
  }

  function findScrollableRange(element) {
    if (!element) return 0;
    return Math.max((element.scrollHeight || 0) - (element.clientHeight || 0), 0);
  }

  function syncScrollByRatio(from, to) {
    const fromRange = findScrollableRange(from);
    const toRange = findScrollableRange(to);
    if (fromRange <= 0 || toRange <= 0) return;
    const ratio = (from.scrollTop || 0) / fromRange;
    to.scrollTop = Math.round(ratio * toRange);
  }

  function flashPreviewPosition(previewContent) {
    if (!previewContent) return;
    previewContent.classList.remove('is-focus-flash');
    void previewContent.offsetWidth;
    previewContent.classList.add('is-focus-flash');
    window.setTimeout(() => {
      previewContent.classList.remove('is-focus-flash');
    }, 520);
  }

  function locateCursorInPreview(textarea, previewContent) {
    if (!textarea || !previewContent) return;
    const cursor = Number(textarea.selectionStart || 0);
    const total = Math.max(String(textarea.value || '').length, 1);
    const ratio = Math.min(1, Math.max(0, cursor / total));
    const targetRange = findScrollableRange(previewContent);
    previewContent.scrollTop = Math.round(targetRange * ratio);
    flashPreviewPosition(previewContent);
  }

  function locatePreviewClickToEditor(event, textarea, previewContent) {
    if (!event || !textarea || !previewContent) return;
    const rect = previewContent.getBoundingClientRect();
    const offsetY = event.clientY - rect.top + previewContent.scrollTop;
    const ratio = previewContent.scrollHeight > 0 ? Math.min(1, Math.max(0, offsetY / previewContent.scrollHeight)) : 0;
    const position = Math.round(ratio * String(textarea.value || '').length);

    textarea.focus();
    textarea.setSelectionRange(position, position);
    const targetRange = findScrollableRange(textarea);
    textarea.scrollTop = Math.round(targetRange * ratio);
  }

  function bindSplitScrollSync(shell, textarea, previewContent) {
    if (!shell || !textarea || !previewContent) return;
    if (textarea.dataset.uaiSplitSyncBound === 'true') return;

    const state = { locking: false };

    const syncFromEditor = () => {
      if (!shell.classList.contains('is-split')) return;
      if (state.locking) return;
      state.locking = true;
      syncScrollByRatio(textarea, previewContent);
      window.requestAnimationFrame(() => {
        state.locking = false;
      });
    };

    const syncFromPreview = () => {
      if (!shell.classList.contains('is-split')) return;
      if (state.locking) return;
      state.locking = true;
      syncScrollByRatio(previewContent, textarea);
      window.requestAnimationFrame(() => {
        state.locking = false;
      });
    };

    textarea.addEventListener('scroll', syncFromEditor);
    previewContent.addEventListener('scroll', syncFromPreview);
    previewContent.addEventListener('click', (event) => {
      if (!shell.classList.contains('is-split') && !shell.classList.contains('is-preview')) return;
      locatePreviewClickToEditor(event, textarea, previewContent);
    });

    textarea.dataset.uaiSplitSyncBound = 'true';
  }

  function isExternalToolbarNode(node) {
    if (!node || node.nodeType !== 1) return false;
    return node.matches('.gpc-toolbar, #article-content-toolbar');
  }

  function collectExternalToolbarsAroundTextarea(textarea) {
    const result = [];
    if (!textarea || !textarea.parentElement) return result;

    const parent = textarea.parentElement;
    const prev = textarea.previousElementSibling;
    const next = textarea.nextElementSibling;
    if (isExternalToolbarNode(prev)) result.push(prev);
    if (isExternalToolbarNode(next) && next !== prev) result.push(next);

    parent.querySelectorAll(':scope > .gpc-toolbar, :scope > #article-content-toolbar').forEach((node) => {
      if (node === textarea) return;
      if (result.includes(node)) return;
      result.push(node);
    });
    return result;
  }

  function closeOtherFullscreenShells(currentShell) {
    document.querySelectorAll('.uai-lite-shell.is-fullscreen').forEach((shell) => {
      if (shell === currentShell) return;
      shell.classList.remove('is-fullscreen');
      const btn = shell.querySelector('button[data-action="toggle-fullscreen"]');
      if (btn) btn.classList.remove('is-active');
    });
  }

  function moveEmbeddedToolbars(shell) {
    const host = shell.querySelector('.uai-lite-toolbar-host');
    const editorPane = shell.querySelector('.uai-lite-editor-pane');
    if (!host || !editorPane) return;

    const embedded = editorPane.querySelectorAll(':scope > .gpc-toolbar, :scope > #article-content-toolbar');
    embedded.forEach((toolbar) => {
      toolbar.classList.add('uai-lite-external-toolbar');
      host.appendChild(toolbar);
    });

    if (host.querySelector('.uai-lite-external-toolbar')) {
      const placeholder = host.querySelector('[data-uai-toolbar-placeholder="1"]');
      if (placeholder) placeholder.remove();
    }
  }

  function attachKeyboardShortcuts(textarea) {
    if (textarea.dataset.uaiShortcutBound === 'true') return;

    textarea.addEventListener('keydown', (event) => {
      if (!event.ctrlKey) return;
      const key = String(event.key || '').toLowerCase();

      if (key === 'b') {
        event.preventDefault();
        wrapSelection(textarea, '**', '**', '粗体文本');
      }
      if (key === 'i') {
        event.preventDefault();
        wrapSelection(textarea, '*', '*', '斜体文本');
      }
      if (key === 'k') {
        event.preventDefault();
        const text = (window.prompt('链接文本') || '').trim() || '链接';
        const url = (window.prompt('链接地址') || '').trim();
        if (!url) return;
        insertAtCursor(textarea, `[${text}](${url})`);
      }
    });

    textarea.dataset.uaiShortcutBound = 'true';
  }

  function enhanceTextarea(textarea) {
    if (!shouldEnhance(textarea)) return;

    const shell = document.createElement('section');
    shell.className = 'uai-lite-shell';

    const header = document.createElement('div');
    header.className = 'uai-lite-header';

    const headerTop = document.createElement('div');
    headerTop.className = 'uai-lite-header-top';

    const title = document.createElement('div');
    title.className = 'uai-lite-title';
    title.textContent = findFieldTitle(textarea);

    const topMeta = document.createElement('div');
    topMeta.className = 'uai-lite-meta';

    const headerRight = document.createElement('div');
    headerRight.className = 'uai-lite-header-right';

    const previewBtn = makeButton('预览', 'toggle-preview');
    const splitBtn = makeButton('分栏', 'toggle-split');
    const locateBtn = makeButton('定位', 'locate-cursor', '定位到当前编辑段落');
    const fullBtn = makeButton('全屏', 'toggle-fullscreen');
    headerRight.appendChild(previewBtn);
    headerRight.appendChild(splitBtn);
    headerRight.appendChild(locateBtn);
    headerRight.appendChild(fullBtn);

    headerTop.appendChild(title);
    headerTop.appendChild(topMeta);
    headerTop.appendChild(headerRight);

    const toolbarHost = document.createElement('div');
    toolbarHost.className = 'uai-lite-toolbar-host';

    header.appendChild(headerTop);
    header.appendChild(toolbarHost);

    const body = document.createElement('div');
    body.className = 'uai-lite-body';

    const editorPane = document.createElement('div');
    editorPane.className = 'uai-lite-editor-pane';

    const previewPane = document.createElement('div');
    previewPane.className = 'uai-lite-preview-pane';
    const previewContent = document.createElement('div');
    previewContent.className = 'uai-lite-preview-content';
    previewPane.appendChild(previewContent);

    body.appendChild(editorPane);
    body.appendChild(previewPane);

    const status = document.createElement('div');
    status.className = 'uai-lite-status';
    const statusLeft = document.createElement('div');
    statusLeft.className = 'uai-lite-status-left';
    const statusRight = document.createElement('div');
    statusRight.className = 'uai-lite-status-right';
    status.appendChild(statusLeft);
    status.appendChild(statusRight);

    shell.appendChild(header);
    shell.appendChild(body);
    shell.appendChild(status);

    const detachedToolbars = collectExternalToolbarsAroundTextarea(textarea);
    textarea.parentNode.insertBefore(shell, textarea);
    editorPane.appendChild(textarea);
    detachedToolbars.forEach((toolbar) => {
      toolbar.classList.add('uai-lite-external-toolbar');
      toolbarHost.appendChild(toolbar);
    });

    textarea.classList.add('uai-bridge-textarea');
    textarea.dataset.uaiEnhanced = 'true';

    const rows = Number(textarea.getAttribute('rows') || 0);
    if (rows >= 18) {
      textarea.style.minHeight = '360px';
    } else if (rows >= 10) {
      textarea.style.minHeight = '280px';
    }

    function refresh() {
      renderPreview(textarea, previewContent);
      syncStatus(textarea, statusLeft, statusRight, topMeta);
      moveEmbeddedToolbars(shell);
    }

    toolbarHost.appendChild(
      createDefaultToolbar(textarea, {
        statusRight,
        refresh: () => refresh(),
      })
    );

    if (EXPECT_EXTERNAL_TOOLBAR_IDS.has(textarea.id) && !toolbarHost.querySelector('.uai-lite-external-toolbar')) {
      const placeholder = document.createElement('span');
      placeholder.textContent = '正在接入扩展工具...';
      placeholder.dataset.uaiToolbarPlaceholder = '1';
      placeholder.className = 'uai-lite-loading';
      toolbarHost.appendChild(placeholder);

      window.setTimeout(() => {
        if (toolbarHost.querySelector('.uai-lite-external-toolbar')) {
          placeholder.remove();
          return;
        }
        placeholder.textContent = '扩展工具未就绪，已启用内置工具栏';
        window.setTimeout(() => {
          placeholder.remove();
        }, 1800);
      }, 2200);
    }

    const shouldDefaultSplit = rows >= 12 || (textarea.value || '').length >= 240;
    if (shouldDefaultSplit) {
      shell.classList.add('is-split');
      splitBtn.classList.add('is-active');
    }
    bindSplitScrollSync(shell, textarea, previewContent);

    previewBtn.addEventListener('click', () => {
      const enabled = shell.classList.toggle('is-preview');
      if (enabled) {
        shell.classList.remove('is-split');
      }
      previewBtn.classList.toggle('is-active', enabled);
      splitBtn.classList.toggle('is-active', shell.classList.contains('is-split'));
      refresh();
    });

    splitBtn.addEventListener('click', () => {
      const enabled = shell.classList.toggle('is-split');
      shell.classList.remove('is-preview');
      splitBtn.classList.toggle('is-active', enabled);
      previewBtn.classList.remove('is-active');
      refresh();
    });

    locateBtn.addEventListener('click', () => {
      locateCursorInPreview(textarea, previewContent);
    });

    fullBtn.addEventListener('click', () => {
      const enabled = shell.classList.toggle('is-fullscreen');
      if (enabled) closeOtherFullscreenShells(shell);
      fullBtn.classList.toggle('is-active', enabled);
      document.body.classList.toggle('uai-lite-lock', Boolean(document.querySelector('.uai-lite-shell.is-fullscreen')));
    });

    textarea.addEventListener('input', refresh);
    textarea.addEventListener('change', refresh);
    attachKeyboardShortcuts(textarea);
    refresh();
  }

  function isSupportedEditPage() {
    const body = document.body;
    if (!body) return false;
    if (document.getElementById('changelist') || document.getElementById('changelist-form')) return false;

    const contentMain = document.getElementById('content-main');
    if (!contentMain) return false;

    const form = contentMain.querySelector('form');
    if (!form) return false;
    return Boolean(contentMain.querySelector('textarea'));
  }

  function init() {
    const body = document.body;
    if (!isSupportedEditPage()) return;

    body.classList.add(TARGET_PAGE_CLASS);
    const areas = document.querySelectorAll('form textarea');
    areas.forEach((textarea) => {
      enhanceTextarea(textarea);
    });

    document.querySelectorAll('.uai-lite-shell').forEach((shell) => {
      moveEmbeddedToolbars(shell);
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;

    const active = document.querySelector('.uai-lite-shell.is-fullscreen');
    if (!active) return;

    active.classList.remove('is-fullscreen');
    const btn = active.querySelector('button[data-action="toggle-fullscreen"]');
    if (btn) btn.classList.remove('is-active');
    document.body.classList.remove('uai-lite-lock');
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  setInterval(init, 1200);
})();
