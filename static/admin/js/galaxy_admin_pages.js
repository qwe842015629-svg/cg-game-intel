(function () {
  const galaxyComponentUrl =
    'https://cdn.jsdelivr.net/gh/uiverse-io/galaxy@master/Buttons/0x-Sarthak_hungry-penguin-30.html';

  const textMap = new Map([
    ['Home', '首页'],
    ['Back', '返回'],
    ['Add', '新增'],
    ['Delete', '删除'],
    ['Search', '搜索'],
    ['Actions', '批量操作'],
    ['Go', '执行'],
    ['Save', '保存'],
    ['Save and continue editing', '保存并继续编辑'],
    ['Save and add another', '保存并新增'],
    ['History', '历史记录'],
    ['View on site', '站点预览'],
    ['Close', '关闭'],
    ['Tips', '提示'],
    ['loading...', '加载中...'],
    ['Please correct the error below.', '请先修正以下错误。'],
    ['Please correct the errors below.', '请先修正以下错误。'],
    ['Change password', '修改密码'],
    ['Log out', '退出登录'],
    ['Quick navigation', '快捷导航'],
    ['Recent actions', '最近操作'],
    ['Documentation', '文档'],

    // Fallbacks for occasional mojibake output in legacy templates.
    ['澧炲姞', '新增'],
    ['鍒犻櫎', '删除'],
    ['杩斿洖', '返回'],
  ]);

  const forcedLabels = [
    ['button[name="_save"]', '保存'],
    ['button[name="_continue"]', '保存并继续编辑'],
    ['button[name="_addanother"]', '保存并新增'],
    ['[data-name="add_item"]', '新增'],
    ['[data-name="delete_selected"]', '删除'],
  ];

  let remoteStyleRequested = false;
  let observerAttached = false;

  function normalizeText(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  function translateText(raw) {
    const normalized = normalizeText(raw);
    if (!normalized) return '';
    if (textMap.has(normalized)) return textMap.get(normalized);

    const lower = normalized.toLowerCase();
    for (const [source, target] of textMap.entries()) {
      if (source.toLowerCase() === lower) return target;
    }
    return '';
  }

  function patchLanguageObject() {
    if (!window.language || typeof window.language !== 'object') return;

    window.language.change_password = '修改密码';
    window.language.logout = '退出登录';
    window.language.yes = '是';
    window.language.no = '否';
    window.language.confirm = '确认执行该操作？';
    window.language.loading = '加载中...';
  }

  function translateTextNodes(root) {
    if (!root || typeof NodeFilter === 'undefined') return;

    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node || !node.nodeValue) return NodeFilter.FILTER_REJECT;
        if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;

        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;

        const tag = parent.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA') {
          return NodeFilter.FILTER_REJECT;
        }

        return NodeFilter.FILTER_ACCEPT;
      },
    });

    const patches = [];
    let current = walker.nextNode();
    while (current) {
      const original = current.nodeValue || '';
      const trimmed = original.trim();
      const translated = translateText(trimmed);
      if (translated && translated !== trimmed) {
        patches.push([current, original.replace(trimmed, translated)]);
      }
      current = walker.nextNode();
    }

    patches.forEach(([node, value]) => {
      node.nodeValue = value;
    });
  }

  function translateAttributes(root) {
    if (!root || !root.querySelectorAll) return;

    root.querySelectorAll('[placeholder],[title],[aria-label]').forEach((el) => {
      ['placeholder', 'title', 'aria-label'].forEach((attr) => {
        if (!el.hasAttribute(attr)) return;
        const raw = el.getAttribute(attr) || '';
        const translated = translateText(raw);
        if (translated && translated !== raw) {
          el.setAttribute(attr, translated);
        }
      });
    });

    root.querySelectorAll('input[type="submit"][value],input[type="button"][value]').forEach((input) => {
      const raw = input.value || '';
      const translated = translateText(raw);
      if (translated && translated !== raw) {
        input.value = translated;
      }
    });
  }

  function resolveLabelTarget(el) {
    const candidates = Array.from(el.querySelectorAll('span')).filter((span) => {
      const cls = String(span.className || '');
      if (/(el-icon|icon|fa-|fas|far|lucide)/i.test(cls)) return false;
      return Boolean((span.textContent || '').trim());
    });

    return candidates[0] || null;
  }

  function setElementLabel(el, label) {
    const translated = translateText(label) || label;
    const target = resolveLabelTarget(el);
    if (target) {
      if (normalizeText(target.textContent) !== translated) {
        target.textContent = translated;
      }
      return;
    }

    if (normalizeText(el.textContent) !== translated) {
      el.textContent = translated;
    }
  }

  function patchForcedLabels() {
    forcedLabels.forEach(([selector, label]) => {
      document.querySelectorAll(selector).forEach((el) => {
        setElementLabel(el, label);
      });
    });
  }

  function parseAdminPath() {
    const parts = window.location.pathname.split('/').filter(Boolean);
    if (parts.length < 3 || parts[0] !== 'admin') return null;

    return {
      app: parts[1],
      model: parts[2],
      listUrl: `/admin/${parts[1]}/${parts[2]}/`,
      path: `/${parts.join('/')}/`,
    };
  }

  function openInSimpleUITab(url, name, eid, icon) {
    try {
      if (
        window.parent &&
        window.parent !== window &&
        window.parent.app &&
        typeof window.parent.app.openTab === 'function'
      ) {
        window.parent.app.openTab({
          url,
          name: name || '管理页面',
          icon: icon || 'far fa-file',
          eid: eid || `admin-pages-${Date.now()}-${Math.random()}`,
          newUrl: `${window.location.origin}${url}`,
          breadcrumbs: [
            { name: '后台管理', icon: 'fas fa-shield-halved' },
            { name: name || '管理页面', icon: icon || 'far fa-file' },
          ],
        });
        return true;
      }
    } catch (error) {
      console.warn('[admin-pages] 打开标签页失败，回退普通跳转。', error);
    }

    return false;
  }

  function getCtaTarget(meta) {
    if (!meta) {
      return {
        label: '管理首页',
        url: '/admin/',
        name: '管理首页',
        icon: 'fas fa-home',
      };
    }

    const isList = window.location.pathname === meta.listUrl;
    if (isList) {
      return {
        label: '管理首页',
        url: '/admin/',
        name: '管理首页',
        icon: 'fas fa-home',
      };
    }

    return {
      label: '返回列表',
      url: meta.listUrl,
      name: '数据列表',
      icon: 'fas fa-list',
    };
  }

  function buildCtaButton(label, onClick) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'galaxy-inline-cta';
    btn.innerHTML = `
      <span>${label}&nbsp;</span>
      <svg viewBox="0 0 13 10" height="10" width="15" aria-hidden="true">
        <path d="M1,5 L11,5"></path>
        <polyline points="8 1 12 5 8 9"></polyline>
      </svg>
    `;
    btn.addEventListener('click', onClick);
    return btn;
  }

  function mountInlineCta() {
    const meta = parseAdminPath();
    const target = getCtaTarget(meta);

    const headerHost = document.querySelector('.page-header .el-page-header__left');
    if (headerHost && !headerHost.querySelector('.galaxy-inline-cta')) {
      const cta = buildCtaButton(target.label, () => {
        if (!openInSimpleUITab(target.url, target.name, '', target.icon)) {
          window.location.href = target.url;
        }
      });
      headerHost.appendChild(cta);
      return;
    }

    const actionsHost = document.querySelector('#changelist .actions');
    if (actionsHost && !actionsHost.querySelector('.galaxy-inline-cta')) {
      const cta = buildCtaButton(target.label, () => {
        if (!openInSimpleUITab(target.url, target.name, '', target.icon)) {
          window.location.href = target.url;
        }
      });
      actionsHost.appendChild(cta);
    }
  }

  function decorateFieldsetTitles() {
    const iconCycle = ['scan-line', 'file-pen-line', 'database', 'sliders-horizontal'];
    let iconIndex = 0;

    document.querySelectorAll('fieldset.module h2').forEach((heading) => {
      if (heading.querySelector('.galaxy-field-icon')) return;

      const icon = document.createElement('i');
      icon.className = 'galaxy-field-icon';
      icon.setAttribute('data-lucide', iconCycle[iconIndex % iconCycle.length]);
      iconIndex += 1;

      heading.insertBefore(icon, heading.firstChild);
    });
  }

  function installGalaxyRemoteButtonStyle() {
    if (remoteStyleRequested || document.getElementById('galaxy-admin-pages-remote-style')) return;
    remoteStyleRequested = true;

    fetch(galaxyComponentUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.text();
      })
      .then((source) => {
        const match = source.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
        if (!match || !match[1]) return;

        const scopedCss = match[1].replace(/\.cta\b/g, '.galaxy-inline-cta');
        const styleEl = document.createElement('style');
        styleEl.id = 'galaxy-admin-pages-remote-style';
        styleEl.textContent = scopedCss;
        document.head.appendChild(styleEl);
      })
      .catch((error) => {
        console.info('[admin-pages] 远程 Galaxy 样式加载失败，使用本地样式回退。', error);
      });
  }

  function refreshLucideIcons() {
    if (!window.lucide || typeof window.lucide.createIcons !== 'function') return;
    window.lucide.createIcons({
      attrs: {
        'stroke-width': 1.9,
      },
    });
  }

  function patchTitle() {
    if (!document.title) return;

    if (document.title.includes('Site administration')) {
      document.title = document.title.replace('Site administration', '后台管理');
    }
    if (document.title.includes('Django site admin')) {
      document.title = document.title.replace('Django site admin', 'Django 管理后台');
    }
  }

  function patchDocument() {
    patchLanguageObject();
    translateTextNodes(document.body || document);
    translateAttributes(document.body || document);
    patchForcedLabels();
    mountInlineCta();
    decorateFieldsetTitles();
    patchTitle();
    installGalaxyRemoteButtonStyle();
    refreshLucideIcons();
  }

  function attachObserver() {
    if (observerAttached || !document.body || typeof MutationObserver === 'undefined') return;
    observerAttached = true;

    let rafToken = 0;
    const schedulePatch = () => {
      if (rafToken) return;
      rafToken = window.requestAnimationFrame(() => {
        rafToken = 0;
        patchDocument();
      });
    };

    const observer = new MutationObserver(schedulePatch);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['title', 'placeholder', 'aria-label', 'value'],
    });
  }

  function run() {
    patchDocument();
    attachObserver();

    // Keep retrying briefly for async-rendered nodes in iframe/tab context.
    let refreshCount = 0;
    const timer = window.setInterval(() => {
      patchDocument();
      refreshCount += 1;
      if (refreshCount >= 6) {
        window.clearInterval(timer);
      }
    }, 450);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run, { once: true });
  } else {
    run();
  }
})();
