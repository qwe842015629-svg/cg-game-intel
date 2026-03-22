(function () {
  const textMap = new Map([
    ['loading...', '加载中...'],
    ['Change theme', '切换主题'],
    ['Set font size', '字体大小'],
    ['Reset', '重置'],
    ['Change password', '修改密码'],
    ['Log out', '退出登录'],
    ['Home', '首页'],
    ['Quick navigation', '快捷导航'],
    ['Recent actions', '最近操作'],
    ['Documentation', '文档'],
  ]);

  function getSimpleUIApp() {
    if (window.app && Array.isArray(window.app.menus)) return window.app;

    try {
      if (
        window.parent &&
        window.parent !== window &&
        window.parent.app &&
        Array.isArray(window.parent.app.menus)
      ) {
        return window.parent.app;
      }
    } catch (error) {
      // Cross-origin frame access can fail; ignore safely.
    }

    return null;
  }

  function hasEmailMarketingMenu(items) {
    if (!Array.isArray(items)) return false;

    for (const item of items) {
      const name = String((item && item.name) || '').trim();
      const url = String((item && item.url) || '').trim();
      if (name === '邮件营销' || url.startsWith('/admin/email_marketing/')) {
        return true;
      }

      if (Array.isArray(item && item.models) && hasEmailMarketingMenu(item.models)) {
        return true;
      }
    }

    return false;
  }

  function createFixedEmailMarketingMenu() {
    return {
      app: 'email_marketing',
      name: '邮件营销',
      icon: 'fas fa-envelope-open-text',
      eid: 'fixed_email_marketing_1123',
      models: [
        {
          name: '发送邮箱配置',
          icon: 'fas fa-paper-plane',
          url: '/admin/email_marketing/emailsenderconfig/',
          eid: 'fixed_email_marketing_1120',
        },
        {
          name: '营销活动',
          icon: 'fas fa-bullhorn',
          url: '/admin/email_marketing/emailcampaign/',
          eid: 'fixed_email_marketing_1121',
        },
        {
          name: '发送日志',
          icon: 'fas fa-list-check',
          url: '/admin/email_marketing/campaignrecipientlog/',
          eid: 'fixed_email_marketing_1122',
        },
      ],
    };
  }

  function ensureMenuData(app, menuGroup) {
    if (!app || !Array.isArray(app.menuData) || !Array.isArray(menuGroup && menuGroup.models)) return;

    menuGroup.models.forEach((model) => {
      const targetUrl = String(model.url || '');
      if (!targetUrl) return;

      const exists = app.menuData.some((item) => String((item && item.url) || '') === targetUrl);
      if (!exists) {
        app.menuData.push(model);
      }
    });
  }

  function findInsertIndex(menus) {
    const anchors = new Set(['页面底部管理', '用户管理']);
    const index = menus.findIndex((item) => anchors.has(String((item && item.name) || '').trim()));
    return index >= 0 ? index : menus.length;
  }

  function ensureFixedEmailMarketingMenu() {
    const app = getSimpleUIApp();
    if (!app || !Array.isArray(app.menus)) return;
    if (hasEmailMarketingMenu(app.menus)) return;

    const menu = createFixedEmailMarketingMenu();
    const insertIndex = findInsertIndex(app.menus);
    app.menus.splice(insertIndex, 0, menu);
    ensureMenuData(app, menu);

    if (typeof app.$forceUpdate === 'function') {
      app.$forceUpdate();
    }
  }

  function patchLanguageObject() {
    if (!window.language || typeof window.language !== 'object') return;

    window.language.change_password = '修改密码';
    window.language.logout = '退出登录';
    window.language.yes = '是';
    window.language.no = '否';
    window.language.confirm = '确认执行该操作？';
  }

  function translateNodeText(root) {
    if (!root) return;

    const selectors = [
      '.loading .center span:last-child',
      '.el-dialog__title',
      '.el-dropdown-menu__item',
      '.el-tabs__item span',
      '.el-breadcrumb__inner',
    ];

    selectors.forEach((selector) => {
      root.querySelectorAll(selector).forEach((el) => {
        const raw = (el.textContent || '').trim();
        if (!raw) return;

        const translated = textMap.get(raw);
        if (translated && translated !== raw) {
          el.textContent = translated;
        }
      });
    });
  }

  function patch() {
    patchLanguageObject();
    translateNodeText(document);
    ensureFixedEmailMarketingMenu();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patch);
  } else {
    patch();
  }

  let retryCount = 0;
  const retryTimer = window.setInterval(() => {
    patch();
    retryCount += 1;
    if (retryCount >= 20) {
      window.clearInterval(retryTimer);
    }
  }, 500);

  const observer = new MutationObserver(() => {
    patch();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
})();
