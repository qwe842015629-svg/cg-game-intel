(function () {
  const PREVIEW_BINDINGS = [
    { inputSelector: 'input[type="file"][name="cover_image"]', previewId: 'article-cover-live-preview', mode: 'cover' },
    { inputSelector: 'input[type="file"][name="icon_image"]', previewId: 'gamepage-icon-live-preview', mode: 'icon' },
    { inputSelector: 'input[type="file"][name="banner_image"]', previewId: 'gamepage-banner-live-preview', mode: 'banner' },
  ];
  const COVER_INPUT_SELECTOR = 'input[type="file"][name="cover_image"]';
  const CONTENT_TEXTAREA_SELECTOR = '#id_content';
  const COVER_PICKER_ACTION_CLASS = 'editor-cover-from-content-action';

  function createCounterEl() {
    const el = document.createElement('div');
    el.className = 'editor-char-counter';
    return el;
  }

  function updateCounter(input, counterEl, maxLength) {
    const length = String(input.value || '').length;
    const suffix = maxLength > 0 ? ` / ${maxLength}` : '';
    counterEl.textContent = `${length}${suffix}`;
    if (maxLength > 0 && length > maxLength) {
      counterEl.classList.add('editor-char-counter--warn');
    } else {
      counterEl.classList.remove('editor-char-counter--warn');
    }
  }

  function bindCharCounter(input) {
    if (!input || input.dataset.counterBound === 'true') return;
    const maxLength = Number(input.dataset.charCounter || 0);
    if (!maxLength) return;

    const counterEl = createCounterEl();
    input.insertAdjacentElement('afterend', counterEl);
    const handler = () => updateCounter(input, counterEl, maxLength);
    input.addEventListener('input', handler);
    handler();
    input.dataset.counterBound = 'true';
  }

  function autoGrowTextarea(textarea) {
    if (!textarea || textarea.dataset.autogrowBound === 'true') return;
    const resize = () => {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.max(textarea.scrollHeight, 140)}px`;
    };
    textarea.addEventListener('input', resize);
    resize();
    textarea.dataset.autogrowBound = 'true';
  }

  function renderPreviewCard(previewEl, dataUrl, mode, filename) {
    if (!previewEl || !dataUrl) return;

    const imageClassByMode = {
      icon: 'admin-image-preview-card__img admin-image-preview-card__img--icon',
      banner: 'admin-image-preview-card__img admin-image-preview-card__img--banner',
      cover: 'admin-image-preview-card__img',
    };
    const imageClass = imageClassByMode[mode] || imageClassByMode.cover;
    const labelByMode = {
      icon: '未保存图标预览',
      banner: '未保存 Banner 预览',
      cover: '未保存封面预览',
    };

    previewEl.classList.remove('admin-image-preview-card--empty');
    previewEl.innerHTML = [
      `<img src="${dataUrl}" alt="preview" class="${imageClass}" />`,
      `<div class="admin-image-preview-card__meta">${labelByMode[mode] || '预览图'}：${filename || 'image'}</div>`,
    ].join('');
  }

  function getOrCreateCoverSourceHiddenInput(fileInput) {
    if (!fileInput || !fileInput.form) return null;
    let hidden = fileInput.form.querySelector('input[name="cover_image_from_content_url"]');
    if (hidden) return hidden;

    hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'cover_image_from_content_url';
    hidden.value = '';
    fileInput.form.appendChild(hidden);
    return hidden;
  }

  function normalizeImageUrl(rawUrl) {
    const value = String(rawUrl || '').trim();
    if (!value) return '';
    if (value.startsWith('//')) return `${window.location.protocol}${value}`;
    if (value.startsWith('/')) return `${window.location.origin}${value}`;
    return value;
  }

  function extractContentImageUrls(text) {
    const source = String(text || '');
    const urls = new Set();

    const htmlImgRegex = /<img\b[^>]*\bsrc=["']([^"']+)["'][^>]*>/gi;
    const mdImgRegex = /!\[[^\]]*]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
    const bareImgRegex = /(https?:\/\/[^\s"'()<>]+?\.(?:png|jpe?g|gif|webp|bmp|svg|avif)(?:\?[^\s"'()<>]*)?)/gi;

    let match = null;
    while ((match = htmlImgRegex.exec(source))) {
      urls.add(normalizeImageUrl(match[1]));
    }
    while ((match = mdImgRegex.exec(source))) {
      urls.add(normalizeImageUrl(match[1]));
    }
    while ((match = bareImgRegex.exec(source))) {
      urls.add(normalizeImageUrl(match[1]));
    }

    return Array.from(urls).filter(Boolean);
  }

  function ensureCoverPickerModal() {
    const existed = document.getElementById('cover-from-content-modal');
    if (existed) return existed;

    const modal = document.createElement('div');
    modal.id = 'cover-from-content-modal';
    modal.className = 'cover-from-content-modal';
    modal.innerHTML = [
      '<div class="cover-from-content-modal__dialog">',
      '  <div class="cover-from-content-modal__header">',
      '    <strong>从正文选择封面图</strong>',
      '    <button type="button" class="cover-from-content-modal__close" data-role="close">×</button>',
      '  </div>',
      '  <div class="cover-from-content-modal__body" data-role="list"></div>',
      '  <div class="cover-from-content-modal__footer">',
      '    <button type="button" class="button" data-role="cancel">取消</button>',
      '  </div>',
      '</div>',
    ].join('');

    modal.addEventListener('click', (event) => {
      const roleEl = event.target.closest('[data-role]');
      if (!roleEl) {
        if (event.target === modal) modal.classList.remove('is-open');
        return;
      }
      const role = roleEl.dataset.role;
      if (role === 'close' || role === 'cancel') {
        modal.classList.remove('is-open');
      }
    });

    document.body.appendChild(modal);
    return modal;
  }

  function openCoverPicker(options) {
    const modal = ensureCoverPickerModal();
    const listEl = modal.querySelector('[data-role="list"]');
    if (!listEl) return;

    const rows = Array.isArray(options.urls) ? options.urls : [];
    listEl.innerHTML = '';

    rows.forEach((url, index) => {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'cover-from-content-item';
      item.innerHTML = [
        `<img src="${url}" alt="content-image-${index + 1}" loading="lazy" />`,
        `<span>图片 ${index + 1}</span>`,
      ].join('');
      item.addEventListener('click', () => {
        options.onPick(url);
        modal.classList.remove('is-open');
      });
      listEl.appendChild(item);
    });

    modal.classList.add('is-open');
  }

  function ensureCoverFromContentAction() {
    const fileInput = document.querySelector(COVER_INPUT_SELECTOR);
    const contentTextarea = document.querySelector(CONTENT_TEXTAREA_SELECTOR);
    const previewEl = document.getElementById('article-cover-live-preview');
    if (!fileInput || !contentTextarea || !previewEl) return;
    if (fileInput.parentNode.querySelector(`.${COVER_PICKER_ACTION_CLASS}`)) return;

    const wrapper = document.createElement('div');
    wrapper.className = COVER_PICKER_ACTION_CLASS;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'button';
    btn.textContent = '从正文选择封面';

    const status = document.createElement('span');
    status.className = 'editor-cover-from-content-status';
    status.textContent = '可从正文中的图片快速设为封面';

    btn.addEventListener('click', () => {
      const urls = extractContentImageUrls(contentTextarea.value);
      if (!urls.length) {
        status.textContent = '正文中未识别到图片';
        return;
      }

      openCoverPicker({
        urls,
        onPick: (url) => {
          const hidden = getOrCreateCoverSourceHiddenInput(fileInput);
          if (hidden) hidden.value = String(url || '');
          renderPreviewCard(previewEl, url, 'cover', '来自正文（保存后生效）');
          status.textContent = '已选择正文图片，点击“保存”后生效';
        },
      });
    });

    wrapper.appendChild(btn);
    wrapper.appendChild(status);
    fileInput.insertAdjacentElement('afterend', wrapper);
  }

  function bindLivePreview(binding) {
    const input = document.querySelector(binding.inputSelector);
    const previewEl = document.getElementById(binding.previewId);
    if (!input || !previewEl || input.dataset.previewBound === 'true') return;

    input.addEventListener('change', () => {
      if (binding.mode === 'cover') {
        const hidden = getOrCreateCoverSourceHiddenInput(input);
        if (hidden) hidden.value = '';
        const status = input.parentNode && input.parentNode.querySelector('.editor-cover-from-content-status');
        if (status) status.textContent = '已改为上传文件作为封面';
      }

      const file = input.files && input.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        renderPreviewCard(previewEl, String(reader.result || ''), binding.mode, file.name);
      };
      reader.readAsDataURL(file);
    });

    input.dataset.previewBound = 'true';
  }

  function init() {
    document.querySelectorAll('input[data-char-counter], textarea[data-char-counter]').forEach(bindCharCounter);
    document.querySelectorAll('textarea.editor-textarea, textarea.editor-textarea--lg, textarea.editor-textarea--xl').forEach(autoGrowTextarea);
    PREVIEW_BINDINGS.forEach(bindLivePreview);
    ensureCoverFromContentAction();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  setInterval(init, 1200);
})();
