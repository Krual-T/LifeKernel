import {
  parseJsonl,
  extractDateOnly,
  inDateRange,
  parseDateInput,
  formatDateUTC,
  formatDateShort,
  formatTimeShort,
  formatDateTime,
  toText,
  debounce,
  setActiveButton,
  clearActiveButtons
} from './common.js';

let allLifelog = [];
let lifelogRangeKey = null;
let lifelogSource = null;
let lifelogBase = null;
let lifelogFileIndex = null;

function groupByDate(entries) {
  const grouped = [];
  let lastDate = null;
  for (const e of entries) {
    const date = formatDateShort(e.timestamp || '');
    if (date && date !== lastDate) {
      grouped.push({ _dateHeader: date });
      lastDate = date;
    }
    grouped.push(e);
  }
  return grouped;
}

function renderLifelog(entries) {
  const list = document.getElementById('lifelogList');
  if (!list) return;
  list.innerHTML = '';
  if (entries.length === 0) {
    list.innerHTML = '<div class="card muted">No log entries found.</div>';
  } else {
    const timeline = document.createElement('div');
    timeline.className = 'timeline';
    const grouped = groupByDate(entries.filter(e => !e._parseError));
    for (const e of grouped) {
      if (e._dateHeader) {
        const header = document.createElement('div');
        header.className = 'timeline-date';
        header.textContent = e._dateHeader;
        timeline.appendChild(header);
        continue;
      }
      const item = document.createElement('div');
      item.className = 'timeline-item';
      const status = String(e.status || 'completed').toLowerCase();
      const statusClass = status === 'failed' ? 'status-failed' : (status === 'pending' ? 'status-pending' : 'status-completed');
      const time = formatTimeShort(e.timestamp || '');
      const files = (e.related_files || []).join(', ');
      const module = String(e.module || 'work').toLowerCase();
      const moduleClass = `module-${module}`;
      item.innerHTML = `
        <div class="timeline-time mono">${time || ''}</div>
        <div class="timeline-dot ${moduleClass}"></div>
        <div class="timeline-card">
          <div>${e.description || ''}</div>
          <div class="timeline-meta">
            <span class="meta-dot ${statusClass}"></span>
            <span>${e.module || 'work'}</span>
            <span>${e.status || ''}</span>
          </div>
          ${files ? `<div class="log-paths">${files}</div>` : ''}
        </div>
      `;
      timeline.appendChild(item);
    }
    list.appendChild(timeline);
  }
  renderLifelogTable(entries.filter(e => !e._parseError));
}

function renderLifelogTable(entries) {
  const table = [
    '<table>',
    '<thead><tr><th class="table-col-date">Time</th><th>Description</th></tr></thead>',
    '<tbody>'
  ];
  const grouped = groupByDate(entries);
  for (const e of grouped) {
    if (e._dateHeader) {
      table.push(`<tr class="date-separator"><td colspan="2">${e._dateHeader}</td></tr>`);
      continue;
    }
    const desc = e.description || e.raw || '';
    const files = (e.related_files || []).join(', ');
    const time = formatTimeShort(e.timestamp || '');
    const module = e.module || '';
    const status = e.status || '';
    const meta = module || status ? `<div class="timeline-meta"><span class="meta-dot"></span><span>${module}</span><span>${status}</span></div>` : '';
    table.push(`<tr><td><span class="mono">${time}</span></td><td>${desc}${meta}${files ? `<div class="log-paths">${files}</div>` : ''}</td></tr>`);
  }
  table.push('</tbody></table>');
  const tableEl = document.getElementById('lifelogTable');
  if (tableEl) tableEl.innerHTML = table.join('');
}

function applyLogFilters() {
  const startInput = document.getElementById('logDateStart');
  const endInput = document.getElementById('logDateEnd');
  const nameInput = document.getElementById('logNameFilter');
  if (!nameInput) return;

  const start = startInput?.value || null;
  const end = endInput?.value || null;
  const name = (nameInput.value || '').trim().toLowerCase();

  const logs = allLifelog.filter(e => {
    if (e._parseError) return false;
    const inRange = inDateRange(e.timestamp || '', start, end);
    const inName = !name || String(e.description || '').toLowerCase().includes(name);
    return inRange && inName;
  });
  logs.sort((a, b) => {
    const ta = Date.parse(a.timestamp || '') || 0;
    const tb = Date.parse(b.timestamp || '') || 0;
    return tb - ta;
  });

  renderLifelog(logs);
}

function setLogLoading(isLoading, message) {
  const logLoadingEl = document.getElementById('logLoading');
  if (logLoadingEl) {
    logLoadingEl.style.display = isLoading ? 'block' : 'none';
    logLoadingEl.textContent = message || '';
  }
  const startInput = document.getElementById('logDateStart');
  const endInput = document.getElementById('logDateEnd');
  if (startInput) startInput.disabled = isLoading;
  if (endInput) endInput.disabled = isLoading;
}

function normalizeListingHref(href) {
  if (!href) return '';
  let clean = href.split('?')[0].split('#')[0];
  try {
    clean = decodeURIComponent(clean);
  } catch (e) {
    // ignore decode errors
  }
  clean = clean.replace(/\\/g, '/');
  if (clean.startsWith('/')) clean = clean.slice(1);
  const idx = clean.indexOf('lifelog/');
  if (idx >= 0) clean = clean.slice(idx + 'lifelog/'.length);
  return clean;
}

function extractListingHrefs(html) {
  const hrefs = Array.from(html.matchAll(/href="([^"]+)"/g)).map(m => m[1]);
  if (hrefs.length > 0) return hrefs;
  const single = Array.from(html.matchAll(/href='([^']+)'/g)).map(m => m[1]);
  if (single.length > 0) return single;
  const dataHrefs = Array.from(html.matchAll(/data-href="([^"]+)"/g)).map(m => m[1]);
  if (dataHrefs.length > 0) return dataHrefs;
  const paths = Array.from(html.matchAll(/\/workspace\/lifelog\/(\d{4}\/\d{2}\/\d{2}\.jsonl)/g)).map(m => m[1]);
  if (paths.length > 0) return paths;
  return [];
}

function normalizeDirToken(value, length) {
  if (!value) return '';
  const token = value.endsWith('/') ? value.slice(0, -1) : value;
  if (token.length !== length) return '';
  return token + '/';
}

function getLifelogBases() {
  const path = location.pathname || '';
  const root = path.includes('/workspace/') ? '/workspace/' : '/';
  return [`${root}lifelog/`, '../lifelog/'];
}

async function tryListFilesFromDirectory() {
  const bases = getLifelogBases();
  for (const base of bases) {
    const res = await fetch(base);
    if (!res.ok) continue;
    const html = await res.text();
    const hrefs = extractListingHrefs(html);
    const items = hrefs.map(normalizeListingHref).filter(Boolean);
    const directFiles = items.filter(h => h.endsWith('.jsonl'));
    const yearDirs = items.map(h => normalizeDirToken(h, 4)).filter(Boolean);
    if (directFiles.length > 0) {
      const filtered = directFiles.filter(f => f.split('/').length >= 3);
      if (filtered.length > 0) return { base, files: filtered };
    }
    if (yearDirs.length > 0) {
      const files = [];
      for (const year of yearDirs) {
        const yearRes = await fetch(`${base}${year}`);
        if (!yearRes.ok) continue;
        const yearHtml = await yearRes.text();
        const yearItems = extractListingHrefs(yearHtml).map(normalizeListingHref).filter(Boolean);
        const monthDirs = yearItems.map(h => {
          let value = h;
          if (value.startsWith(year)) value = value.slice(year.length);
          if (value.startsWith('/')) value = value.slice(1);
          return normalizeDirToken(value, 2);
        }).filter(Boolean);
        if (monthDirs.length === 0) {
          const yearFiles = yearItems.filter(h => h.endsWith('.jsonl'));
          for (const file of yearFiles) {
            const name = file.includes('/') ? file.split('/').pop() : file;
            if (name) files.push(`${year}${name}`);
          }
        }
        for (const month of monthDirs) {
          const monthRes = await fetch(`${base}${year}${month}`);
          if (!monthRes.ok) continue;
          const monthHtml = await monthRes.text();
          const monthItems = extractListingHrefs(monthHtml).map(normalizeListingHref).filter(Boolean);
          const monthFiles = monthItems.filter(h => h.endsWith('.jsonl'));
          for (const file of monthFiles) {
            const name = file.includes('/') ? file.split('/').pop() : file;
            if (name) files.push(`${year}${month}${name}`);
          }
        }
      }
      if (files.length > 0) return { base, files };
    }
  }
  throw new Error('no directory listing');
}

async function getLifelogFileIndex() {
  if (Array.isArray(lifelogFileIndex)) return lifelogFileIndex;
  try {
    const result = await tryListFilesFromDirectory();
    lifelogBase = result.base;
    lifelogFileIndex = result.files || [];
    return lifelogFileIndex;
  } catch (e) {
    lifelogFileIndex = null;
    return null;
  }
}

async function loadLifelogByFiles(files, base, statusEl) {
  const baseDir = base || lifelogBase || '../lifelog/';
  if (!files || files.length === 0) {
    allLifelog = [];
    applyLogFilters();
    if (statusEl) statusEl.textContent = 'No lifelog files found.';
    return;
  }
  setLogLoading(true, `Loading... 0/${files.length}`);
  const texts = [];
  const batchSize = 20;
  try {
    for (let i = 0; i < files.length; i += batchSize) {
      const batch = files.slice(i, i + batchSize);
      const results = await Promise.all(batch.map(f => fetch(`${baseDir}${f}`).then(r => r.ok ? r.text() : '')));
      texts.push(...results);
      const done = Math.min(i + batchSize, files.length);
      setLogLoading(true, `Loading... ${done}/${files.length}`);
    }
    allLifelog = texts.flatMap(t => t ? parseJsonl(t) : []);
    applyLogFilters();
    if (statusEl) statusEl.textContent = `Loaded lifelog: ${allLifelog.length} entries`;
  } catch (e) {
    allLifelog = [];
    applyLogFilters();
    if (statusEl) statusEl.textContent = 'Failed to load lifelog.';
  } finally {
    setLogLoading(false, '');
  }
}

async function resolveLifelogBaseByProbe(file) {
  const bases = getLifelogBases();
  for (const base of bases) {
    try {
      const res = await fetch(`${base}${file}`);
      if (res.ok || res.status === 404) return base;
    } catch (e) {
      // ignore and continue
    }
  }
  return '../lifelog/';
}

async function loadLifelogByRange(start, end, statusEl) {
  if (!start || !end) return;
  const startDate = parseDateInput(start);
  const endDate = parseDateInput(end);
  if (!startDate || !endDate) return;
  const files = [];
  for (let d = new Date(startDate); d <= endDate; d.setUTCDate(d.getUTCDate() + 1)) {
    files.push(`${formatDateUTC(d).replace(/-/g, '/')}.jsonl`);
  }
  const index = await getLifelogFileIndex();
  if (index && index.length) {
    const set = new Set(index);
    const filtered = files.filter(f => set.has(f));
    await loadLifelogByFiles(filtered, lifelogBase || await resolveLifelogBaseByProbe(files[0]), statusEl);
    return;
  }
  const base = lifelogBase || await resolveLifelogBaseByProbe(files[0]);
  lifelogBase = base;
  await loadLifelogByFiles(files, base, statusEl);
}

async function loadAllLifelog(statusEl) {
  try {
    const files = await getLifelogFileIndex();
    if (files && files.length > 0) {
      await loadLifelogByFiles(files, lifelogBase, statusEl);
      lifelogSource = 'listing';
      lifelogRangeKey = null;
      return;
    }
    throw new Error('no files from listing');
  } catch (e) {
    allLifelog = [];
    applyLogFilters();
    if (statusEl) statusEl.textContent = 'Cannot list lifelog files. Use date range to load.';
    const start = document.getElementById('logDateStart')?.value || null;
    const end = document.getElementById('logDateEnd')?.value || null;
    if (start && end) {
      await loadLifelogByRange(start, end, statusEl);
      lifelogSource = 'range';
      lifelogRangeKey = `${start}..${end}`;
    }
  }
}

async function ensureLifelogLoaded(start, end, statusEl) {
  if (start && end) {
    const key = `${start}..${end}`;
    if (lifelogSource !== 'range' || lifelogRangeKey !== key) {
      lifelogRangeKey = key;
      lifelogSource = 'range';
      await loadLifelogByRange(start, end, statusEl);
    }
    return;
  }
  if (!allLifelog.length || lifelogSource !== 'listing') {
    await loadAllLifelog(statusEl);
  }
}

function setLogRangeDays(days) {
  const today = new Date();
  const end = formatDateUTC(today);
  const startDate = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()));
  if (days > 0) {
    startDate.setUTCDate(startDate.getUTCDate() - (days - 1));
  }
  const start = formatDateUTC(startDate);
  const startInput = document.getElementById('logDateStart');
  const endInput = document.getElementById('logDateEnd');
  if (startInput) startInput.value = start;
  if (endInput) endInput.value = end;
}

function initLogDefaults() {
  const today = new Date();
  const end = formatDateUTC(today);
  const startDate = new Date(Date.UTC(today.getUTCFullYear() - 1, today.getUTCMonth(), today.getUTCDate()));
  const start = formatDateUTC(startDate);
  const startInput = document.getElementById('logDateStart');
  const endInput = document.getElementById('logDateEnd');
  if (startInput && !startInput.value) startInput.value = start;
  if (endInput && !endInput.value) endInput.value = end;
  return { start, end };
}

export function initLogs(statusEl) {
  const nameInput = document.getElementById('logNameFilter');
  if (!nameInput) return;

  const debouncedLogFilter = debounce(async () => {
    const start = document.getElementById('logDateStart')?.value || null;
    const end = document.getElementById('logDateEnd')?.value || null;
    await ensureLifelogLoaded(start, end, statusEl);
    applyLogFilters();
  }, 300);

  const logQuickButtons = Array.from(document.querySelectorAll('[data-range]'));

  nameInput.addEventListener('input', debouncedLogFilter);
  document.getElementById('logDateStart')?.addEventListener('change', async () => {
    clearActiveButtons(logQuickButtons);
    const start = document.getElementById('logDateStart')?.value || null;
    const end = document.getElementById('logDateEnd')?.value || null;
    if (start && end) {
      lifelogRangeKey = `${start}..${end}`;
      lifelogSource = 'range';
      await loadLifelogByRange(start, end, statusEl);
    }
    applyLogFilters();
  });
  document.getElementById('logDateEnd')?.addEventListener('change', async () => {
    clearActiveButtons(logQuickButtons);
    const start = document.getElementById('logDateStart')?.value || null;
    const end = document.getElementById('logDateEnd')?.value || null;
    if (start && end) {
      lifelogRangeKey = `${start}..${end}`;
      lifelogSource = 'range';
      await loadLifelogByRange(start, end, statusEl);
    }
    applyLogFilters();
  });

  logQuickButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      setActiveButton(logQuickButtons, btn);
      const val = btn.getAttribute('data-range');
      if (val === 'today') {
        setLogRangeDays(1);
      } else {
        const days = Number(val);
        if (!Number.isNaN(days)) setLogRangeDays(days);
      }
      const start = document.getElementById('logDateStart')?.value || null;
      const end = document.getElementById('logDateEnd')?.value || null;
      if (start && end) {
        lifelogRangeKey = `${start}..${end}`;
        lifelogSource = 'range';
        await loadLifelogByRange(start, end, statusEl);
      }
      applyLogFilters();
    });
  });

  const viewButtons = Array.from(document.querySelectorAll('.view-button'));
  if (viewButtons.length) {
    const lifelogTablePanel = document.getElementById('lifelogTablePanel');
    const lifelogListPanel = document.getElementById('lifelogListPanel');
    function setLifelogView(view) {
      viewButtons.forEach(btn => {
        const isActive = btn.dataset.view === view;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      });
      if (lifelogTablePanel) lifelogTablePanel.style.display = view === 'table' ? 'block' : 'none';
      if (lifelogListPanel) lifelogListPanel.style.display = view === 'timeline' ? 'block' : 'none';
    }
    viewButtons.forEach(btn => {
      btn.addEventListener('click', () => setLifelogView(btn.dataset.view));
    });
    setLifelogView('timeline');
  }

  const { start: defaultStart, end: defaultEnd } = initLogDefaults();
  lifelogRangeKey = `${defaultStart}..${defaultEnd}`;
  lifelogSource = 'range';
  loadLifelogByRange(defaultStart, defaultEnd, statusEl);
}
