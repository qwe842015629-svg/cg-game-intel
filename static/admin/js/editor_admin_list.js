(function () {
  function onTargetListPage() {
    const body = document.body;
    if (!body) return false;
    return body.classList.contains('model-article') || body.classList.contains('model-gamepage');
  }

  function syncTwoColumnLayoutState() {
    const changelist = document.getElementById('changelist');
    if (!changelist) return;

    const filter = changelist.querySelector('#changelist-filter');
    changelist.classList.toggle('admin-list-has-filter', Boolean(filter));
  }

  function countCheckedRows(root) {
    return root.querySelectorAll('tbody input.action-select:checked').length;
  }

  function ensureSummaryBar(resultList) {
    const changelist = document.getElementById('changelist');
    if (!changelist || !resultList) return null;

    let bar = changelist.querySelector('.admin-list-summary');
    if (!bar) {
      bar = document.createElement('div');
      bar.className = 'admin-list-summary';
      bar.innerHTML = [
        '<span class="admin-list-summary__chip" data-role="rows">本页条目: 0</span>',
        '<span class="admin-list-summary__chip" data-role="checked">已勾选: 0</span>',
        '<span class="admin-list-summary__chip" data-role="filters">筛选: 无</span>',
      ].join('');
      changelist.insertBefore(bar, changelist.firstChild);
    }
    return bar;
  }

  function getFilterSummary() {
    const selected = document.querySelectorAll('#changelist-filter li.selected a');
    if (!selected.length) return '无';

    const values = [];
    selected.forEach((el) => {
      const text = String(el.textContent || '').trim();
      if (text && text !== '全部') values.push(text);
    });
    return values.length ? values.join(' / ') : '无';
  }

  function refreshSummary() {
    if (!onTargetListPage()) return;

    const resultList = document.getElementById('result_list');
    if (!resultList) return;

    const bar = ensureSummaryBar(resultList);
    if (!bar) return;

    const rowCount = resultList.querySelectorAll('tbody tr').length;
    const checkedCount = countCheckedRows(resultList);
    const filterText = getFilterSummary();

    const rowsEl = bar.querySelector('[data-role="rows"]');
    const checkedEl = bar.querySelector('[data-role="checked"]');
    const filtersEl = bar.querySelector('[data-role="filters"]');

    if (rowsEl) rowsEl.textContent = `本页条目: ${rowCount}`;
    if (checkedEl) checkedEl.textContent = `已勾选: ${checkedCount}`;
    if (filtersEl) filtersEl.textContent = `筛选: ${filterText}`;
  }

  function bindEvents() {
    const changelist = document.getElementById('changelist');
    if (!changelist || changelist.dataset.summaryBound === 'true') return;

    changelist.addEventListener('change', (event) => {
      const target = event.target;
      if (target && target.classList && target.classList.contains('action-select')) {
        refreshSummary();
      }
    });

    changelist.dataset.summaryBound = 'true';
  }

  function init() {
    if (!onTargetListPage()) return;
    syncTwoColumnLayoutState();
    bindEvents();
    refreshSummary();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  setInterval(init, 1200);
})();
