(function () {
  const TOOLBAR_ID = 'article-content-toolbar';

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

  function createButton(text, action) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = text;
    button.dataset.action = action;
    return button;
  }

  function bindToolbar() {
    const textarea = document.getElementById('id_content');
    if (!textarea || document.getElementById(TOOLBAR_ID)) return;

    const toolbar = document.createElement('div');
    toolbar.id = TOOLBAR_ID;
    toolbar.innerHTML = '<strong style="font-size:12px;color:#334155;">快捷插入：</strong>';
    toolbar.appendChild(createButton('二级标题', 'h2'));
    toolbar.appendChild(createButton('引用块', 'quote'));
    toolbar.appendChild(createButton('分割线', 'hr'));
    toolbar.appendChild(createButton('插入图片', 'img'));

    toolbar.addEventListener('click', (event) => {
      const btn = event.target.closest('button[data-action]');
      if (!btn) return;

      const action = btn.dataset.action;
      if (action === 'h2') {
        insertAtCursor(textarea, '\n## 小节标题\n');
      }
      if (action === 'quote') {
        insertAtCursor(textarea, '\n> 这里填写重点信息\n');
      }
      if (action === 'hr') {
        insertAtCursor(textarea, '\n---\n');
      }
      if (action === 'img') {
        const alt = (window.prompt('图片说明文字') || '').trim() || 'image';
        const url = (window.prompt('图片链接（可粘贴素材库 URL）') || '').trim();
        if (!url) return;
        insertAtCursor(textarea, `\n![${alt}](${url})\n`);
      }
    });

    textarea.parentNode.insertBefore(toolbar, textarea);
  }

  function bindMetaAssist() {
    const titleInput = document.getElementById('id_title');
    const metaTitleInput = document.getElementById('id_meta_title');
    const excerptInput = document.getElementById('id_excerpt');
    const metaDescInput = document.getElementById('id_meta_description');

    if (titleInput && metaTitleInput && titleInput.dataset.metaAssistBound !== 'true') {
      titleInput.addEventListener('blur', () => {
        if (!metaTitleInput.value.trim()) {
          metaTitleInput.value = titleInput.value.trim();
          metaTitleInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
      titleInput.dataset.metaAssistBound = 'true';
    }

    if (excerptInput && metaDescInput && excerptInput.dataset.metaAssistBound !== 'true') {
      excerptInput.addEventListener('blur', () => {
        if (!metaDescInput.value.trim()) {
          metaDescInput.value = excerptInput.value.trim().slice(0, 160);
          metaDescInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
      excerptInput.dataset.metaAssistBound = 'true';
    }
  }

  function init() {
    bindToolbar();
    bindMetaAssist();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  setInterval(init, 1200);
})();
