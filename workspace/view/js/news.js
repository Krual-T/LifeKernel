import { parseJsonl, formatDateShort, inDateRange, fetchFirst, debounce } from './common.js';

let allItems = [];
let allRecords = [];

function normalizeSources(sources) {
  if (!Array.isArray(sources)) return [];
  return sources.map(s => {
    if (!s) return null;
    if (typeof s === 'string') return { name: s, url: '' };
    return { name: s.name || s.url || '', url: s.url || '' };
  }).filter(Boolean);
}

function flattenRecords(records) {
  const items = [];
  for (const rec of records) {
    if (rec.type === 'news_item' || (!rec.items && rec.title && (rec.date || rec.timestamp))) {
      items.push({
        title: rec.title || '',
        date: rec.date || formatDateShort(rec.timestamp || ''),
        category: rec.category || '',
        summary: rec.summary || '',
        entities: Array.isArray(rec.entities) ? rec.entities : [],
        sources: normalizeSources(rec.sources),
        recordId: rec.id || '',
        recordTitle: rec.title || '',
        recordTimestamp: rec.timestamp || ''
      });
      continue;
    }
    const recordItems = Array.isArray(rec.items) ? rec.items : [];
    for (const item of recordItems) {
      items.push({
        title: item.title || '',
        date: item.date || '',
        category: item.category || '',
        summary: item.summary || '',
        entities: Array.isArray(item.entities) ? item.entities : [],
        sources: normalizeSources(item.sources),
        recordId: rec.id || '',
        recordTitle: rec.title || '',
        recordTimestamp: rec.timestamp || ''
      });
    }
  }
  return items;
}

function renderMeta() {
  const metaEl = document.getElementById('newsMeta');
  if (!metaEl) return;
  if (!allRecords.length) {
    metaEl.textContent = 'No news records found.';
    return;
  }
  const latest = [...allRecords].sort((a, b) => {
    const ta = Date.parse(a.timestamp || '') || 0;
    const tb = Date.parse(b.timestamp || '') || 0;
    return tb - ta;
  })[0];
  const window = '';
  const count = allItems.length;
  metaEl.textContent = `Latest: ${formatDateShort(latest?.timestamp || '')} | Items: ${count}`;
}

function updateCategoryOptions(items) {
  const select = document.getElementById('newsCategory');
  if (!select) return;
  const categories = Array.from(new Set(items.map(i => i.category).filter(Boolean))).sort();
  const existing = select.value;
  select.innerHTML = '<option value="">All</option>';
  categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    select.appendChild(opt);
  });
  if (existing) select.value = existing;
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatSources(sources) {
  if (!sources || !sources.length) return '';
  return sources.map(s => {
    const name = escapeHtml(s.name || s.url || '');
    const url = escapeHtml(s.url || '');
    if (!url) return name;
    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${name || url}</a>`;
  }).join(' | ');
}

function groupByDate(items) {
  const grouped = [];
  let lastDate = null;
  for (const item of items) {
    const date = item.date || '';
    if (date && date !== lastDate) {
      grouped.push({ _dateHeader: date });
      lastDate = date;
    }
    grouped.push(item);
  }
  return grouped;
}

function renderList(items) {
  const listEl = document.getElementById('newsList');
  if (!listEl) return;
  if (!items.length) {
    listEl.innerHTML = '<div class="empty">No news items match current filters.</div>';
    return;
  }
  const html = [];
  const grouped = groupByDate(items);
  for (const item of grouped) {
    if (item._dateHeader) {
      html.push(`<div class="timeline-date">${item._dateHeader}</div>`);
      continue;
    }
    const entities = item.entities?.length ? item.entities.map(e => `<span class="tag">${e}</span>`).join('') : '';
    const sources = formatSources(item.sources);
    const primaryUrl = item.sources?.find(s => s?.url)?.url || '';
    const titleHtml = primaryUrl
      ? `<a href="${escapeHtml(primaryUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title || '')}</a>`
      : escapeHtml(item.title || '');
    html.push(`
      <div class="card">
        <div class="news-title">${titleHtml}</div>
        <div class="news-meta">
          ${item.date ? `<span class="pill">${item.date}</span>` : ''}
          ${item.category ? `<span class="pill">${item.category}</span>` : ''}
          ${item.recordTitle ? `<span class="pill">${item.recordTitle}</span>` : ''}
        </div>
        ${item.summary ? `<div class="section">${item.summary}</div>` : ''}
        ${entities ? `<div class="section">${entities}</div>` : ''}
        ${sources ? `<div class="source-list">${sources}</div>` : ''}
      </div>
    `);
  }
  listEl.innerHTML = html.join('');
}

function applyFilters() {
  const start = document.getElementById('newsDateStart')?.value || '';
  const end = document.getElementById('newsDateEnd')?.value || '';
  const category = document.getElementById('newsCategory')?.value || '';
  const keyword = (document.getElementById('newsKeyword')?.value || '').trim().toLowerCase();

  const filtered = allItems.filter(item => {
    if (item._parseError) return false;
    const inRange = inDateRange(item.date || item.recordTimestamp || '', start || null, end || null);
    if (!inRange) return false;
    if (category && item.category !== category) return false;
    if (!keyword) return true;
    const hay = [
      item.title,
      item.summary,
      item.category,
      (item.entities || []).join(' '),
      (item.sources || []).map(s => s.name).join(' ')
    ].join(' ').toLowerCase();
    return hay.includes(keyword);
  });

  filtered.sort((a, b) => {
    const da = Date.parse(a.date || a.recordTimestamp || '') || 0;
    const db = Date.parse(b.date || b.recordTimestamp || '') || 0;
    return db - da;
  });

  renderList(filtered);
}

async function loadNews() {
  const paths = [
    '/workspace/records/news/news.jsonl',
    '../records/news/news.jsonl',
    '../../records/news/news.jsonl'
  ];
  try {
    const { res } = await fetchFirst(paths);
    const text = await res.text();
    const records = parseJsonl(text).filter(r => !r._parseError);
    allRecords = records;
    allItems = flattenRecords(records);
    updateCategoryOptions(allItems);
    renderMeta();
    applyFilters();
  } catch (e) {
    const listEl = document.getElementById('newsList');
    if (listEl) listEl.innerHTML = '<div class="empty">Failed to load news records.</div>';
  }
}

function initFilters() {
  const keywordInput = document.getElementById('newsKeyword');
  const categorySelect = document.getElementById('newsCategory');
  const startInput = document.getElementById('newsDateStart');
  const endInput = document.getElementById('newsDateEnd');
  const debounced = debounce(applyFilters, 200);

  keywordInput?.addEventListener('input', debounced);
  categorySelect?.addEventListener('change', applyFilters);
  startInput?.addEventListener('change', applyFilters);
  endInput?.addEventListener('change', applyFilters);
}

export function initNews() {
  if (!document.getElementById('newsList')) return;
  initFilters();
  loadNews();
}

if (document.getElementById('newsList')) {
  initNews();
}
