(function () {
  const trendData = parseJsonScript('trend-data', { labels: [], series: [] });
  const statusData = parseJsonScript('status-data', []);

  const trendChart = document.getElementById('trendChart');
  const trendLegend = document.getElementById('trendLegend');
  const statusDonut = document.getElementById('statusDonut');
  const statusTotal = document.getElementById('statusTotal');
  const statusLegend = document.getElementById('statusLegend');

  const statusIconMap = {
    published: 'badge-check',
    draft: 'file-pen-line',
    archived: 'archive',
  };

  const galaxyComponentUrl =
    'https://cdn.jsdelivr.net/gh/uiverse-io/galaxy@master/Buttons/0x-Sarthak_hungry-penguin-30.html';

  window.goBack = function goBack() {
    if (document.referrer && window.history.length > 1) {
      window.history.back();
      return;
    }
    window.location.href = '/admin/';
  };

  function parseJsonScript(id, fallback) {
    const el = document.getElementById(id);
    if (!el) return fallback;

    try {
      return JSON.parse(el.textContent || '') || fallback;
    } catch (error) {
      console.error(`[dashboard] 解析 ${id} 失败:`, error);
      return fallback;
    }
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
          eid: eid || `dashboard-${Date.now()}-${Math.random()}`,
          newUrl: `${window.location.origin}${url}`,
          breadcrumbs: [
            { name: '运营看板', icon: 'fas fa-tachometer-alt' },
            { name: name || '管理页面', icon: icon || 'far fa-file' },
          ],
        });
        return true;
      }
    } catch (error) {
      console.warn('[dashboard] 打开标签页失败，回退为普通跳转:', error);
    }

    return false;
  }

  function bindAdminLinks() {
    const links = document.querySelectorAll('a.js-admin-tab-link');
    links.forEach((link) => {
      link.addEventListener('click', function onClick(event) {
        const url = this.getAttribute('href') || '';
        if (!url.startsWith('/admin/')) return;

        const name = this.dataset.name || this.textContent.trim();
        const eid = this.dataset.eid || '';
        const icon = this.dataset.icon || 'far fa-file';

        if (openInSimpleUITab(url, name, eid, icon)) {
          event.preventDefault();
        }
      });
    });
  }

  function renderTrend() {
    if (!trendChart || !trendLegend) return;

    const labels = Array.isArray(trendData.labels) ? trendData.labels : [];
    const series = Array.isArray(trendData.series) ? trendData.series : [];

    if (!labels.length || !series.length) {
      trendChart.innerHTML = '<div class="list-empty">暂无趋势数据</div>';
      trendLegend.innerHTML = '';
      return;
    }

    const allValues = [];
    series.forEach((item) => {
      (item.data || []).forEach((value) => allValues.push(Number(value) || 0));
    });

    const maxValue = Math.max(...allValues, 1);

    trendLegend.innerHTML = '';
    series.forEach((item) => {
      const legendItem = document.createElement('span');
      legendItem.className = 'trend-legend-item';
      legendItem.innerHTML = `<span class="trend-legend-dot" style="background:${item.color}"></span>${item.name}`;
      trendLegend.appendChild(legendItem);
    });

    trendChart.innerHTML = '';
    labels.forEach((label, index) => {
      const day = document.createElement('div');
      day.className = 'trend-day';

      const bars = document.createElement('div');
      bars.className = 'trend-bars';

      series.forEach((item) => {
        const value = Number((item.data || [])[index] || 0);
        const bar = document.createElement('div');
        bar.className = 'trend-bar';
        bar.title = `${item.name}: ${value}`;
        bar.style.background = item.color;
        bar.style.height = `${Math.max((value / maxValue) * 160, value ? 8 : 2)}px`;
        bars.appendChild(bar);
      });

      const text = document.createElement('div');
      text.className = 'trend-label';
      text.textContent = String(label);

      day.appendChild(bars);
      day.appendChild(text);
      trendChart.appendChild(day);
    });
  }

  function renderStatusDonut() {
    if (!statusDonut || !statusTotal || !statusLegend) return;

    const rows = Array.isArray(statusData) ? statusData : [];
    if (!rows.length) {
      statusDonut.style.background = '#edf3fc';
      statusTotal.textContent = '0';
      statusLegend.innerHTML = '<div class="list-empty">暂无状态数据</div>';
      return;
    }

    const total = rows.reduce((sum, item) => sum + (Number(item.value) || 0), 0);
    statusTotal.textContent = String(total);

    let progress = 0;
    const segments = rows.map((item) => {
      const value = Number(item.value) || 0;
      const percent = total ? (value / total) * 100 : 0;
      const start = progress;
      progress += percent;
      return `${item.color} ${start}% ${progress}%`;
    });
    statusDonut.style.background = `conic-gradient(${segments.join(', ')})`;

    statusLegend.innerHTML = '';
    rows.forEach((item) => {
      const row = document.createElement('div');
      row.className = 'status-row';

      const icon = statusIconMap[item.status] || 'circle';
      row.innerHTML = `
        <span class="status-name">
          <i data-lucide="${icon}"></i>
          <span class="trend-legend-dot" style="background:${item.color}"></span>
          ${item.label}
        </span>
        <span class="status-value">${item.value}</span>
      `;
      statusLegend.appendChild(row);
    });
  }

  function installGalaxyRemoteButtonStyle() {
    if (document.getElementById('galaxy-remote-style')) return;

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

        const scopedCss = match[1].replace(/\.cta\b/g, '.galaxy-cta');
        const styleEl = document.createElement('style');
        styleEl.id = 'galaxy-remote-style';
        styleEl.textContent = scopedCss;
        document.head.appendChild(styleEl);
      })
      .catch((error) => {
        console.info('[dashboard] 远程 Galaxy 样式加载失败，已使用本地回退样式。', error);
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

  bindAdminLinks();
  renderTrend();
  renderStatusDonut();
  installGalaxyRemoteButtonStyle();
  refreshLucideIcons();

  // 动态渲染后重复触发几次，确保 iframe 内异步节点都能渲染 Lucide 图标。
  let refreshCount = 0;
  const timer = window.setInterval(() => {
    refreshLucideIcons();
    refreshCount += 1;
    if (refreshCount >= 6) {
      window.clearInterval(timer);
    }
  }, 450);
})();
