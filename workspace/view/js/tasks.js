import {
  parseJsonl,
  inDateRange,
  formatDateShort,
  debounce,
  fetchFirst,
  setActiveButton,
  clearActiveButtons
} from './common.js';

let allTasks = [];
let currentPage = 1;
const pageSize = 10;

function statusBadge(status) {
  const s = status || 'pending';
  const cls = s === 'done' ? 'status-done' : 'status-pending';
  return `<span class="badge ${cls}">${s}</span>`;
}

function priorityBadge(priority) {
  const p = priority || 'medium';
  const cls = p === 'high' ? 'priority-high' : (p === 'low' ? 'priority-low' : 'priority-medium');
  return `<span class="badge ${cls}">${p}</span>`;
}

function paginate(items) {
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  if (currentPage > totalPages) currentPage = totalPages;
  const start = (currentPage - 1) * pageSize;
  const end = start + pageSize;
  const pageInfo = document.getElementById('pageInfo');
  if (pageInfo) pageInfo.textContent = `Page ${currentPage} / ${totalPages}`;
  return items.slice(start, end);
}

function makeStatCard(title, value, accentClass) {
  const el = document.createElement('div');
  el.className = 'card stat-card';
  const accent = accentClass ? ` ${accentClass}` : '';
  const iconClass = title.toLowerCase().includes('pending') ? 'pending' : (title.toLowerCase().includes('done') ? 'done' : '');
  el.innerHTML = `<div class="label"><span class="stat-icon ${iconClass}"></span>${title}</div><div class="value${accent}">${value}</div>`;
  return el;
}

function renderTaskTable(tasks) {
  const table = [
    '<table>',
    '<thead><tr><th class="table-col-id">ID</th><th class="table-col-title">Title</th><th>Status</th><th>Priority</th><th>Module</th><th class="table-col-date">Created</th><th class="table-col-date">Completed</th><th class="table-col-date">Due</th></tr></thead>',
    '<tbody>'
  ];
  for (const t of tasks) {
    const idText = t.id || '';
    table.push(`<tr><td><span class="mono truncate" title="${idText}">${idText}</span></td><td>${t.title || ''}</td><td>${statusBadge(t.status)}</td><td>${priorityBadge(t.priority)}</td><td>${t.module || ''}</td><td><span class="mono">${formatDateShort(t.created_at)}</span></td><td><span class="mono">${formatDateShort(t.completed_at)}</span></td><td><span class="mono">${formatDateShort(t.due_time)}</span></td></tr>`);
  }
  table.push('</tbody></table>');
  const tableEl = document.getElementById('taskTable');
  if (tableEl) tableEl.innerHTML = table.join('');
}

function renderTasks(tasks) {
  const pending = tasks.filter(t => t.status !== 'done');
  pending.sort((a, b) => (a.due_time || '').localeCompare(b.due_time || ''));
  const done = tasks.filter(t => t.status === 'done');

  const summary = document.getElementById('taskSummary');
  if (summary) {
    summary.innerHTML = '';
    summary.appendChild(makeStatCard('Total', String(tasks.length), ''));
    summary.appendChild(makeStatCard('Pending', String(pending.length), 'stat-accent-pending'));
    summary.appendChild(makeStatCard('Done', String(done.length), 'stat-accent-done'));
  }

  const list = document.getElementById('taskList');
  if (list) {
    list.innerHTML = '';
    if (pending.length === 0) {
      list.innerHTML = '<div class="card muted">All caught up!</div>';
    } else {
      for (const t of pending) {
        const el = document.createElement('div');
        const priority = String(t.priority || 'medium').toLowerCase();
        const priorityClass = ['low', 'medium', 'high'].includes(priority) ? `task-priority-${priority}` : 'task-priority-medium';
        el.className = `card task-card ${priorityClass}`;
        el.innerHTML = `
          <div class="task-title">${t.title || ''}</div>
          <div class="task-meta">
            <span class="pill">${t.module || 'work'}</span>
            <span>Status ${statusBadge(t.status)} | Priority ${priorityBadge(t.priority)} | Due <span class="mono">${formatDateShort(t.due_time) || '-'}</span></span>
          </div>
          <div>${t.details || ''}</div>
        `;
        list.appendChild(el);
      }
    }
  }

  const paged = paginate(tasks);
  renderTaskTable(paged);
}

function applyTaskFilters() {
  const startInput = document.getElementById('taskDateStart');
  const endInput = document.getElementById('taskDateEnd');
  const nameInput = document.getElementById('taskNameFilter');
  if (!nameInput) return;

  const start = startInput?.value || null;
  const end = endInput?.value || null;
  const name = (nameInput.value || '').trim().toLowerCase();
  const taskStatus = document.getElementById('taskStatus')?.value || 'all';
  const taskPriority = document.getElementById('taskPriority')?.value || 'all';
  const taskModule = document.getElementById('taskModule')?.value || 'all';

  const tasks = allTasks.filter(t => {
    const dateField = t.due_time || t.created_at || '';
    const inRange = inDateRange(dateField, start, end);
    const inName = !name || String(t.title || '').toLowerCase().includes(name);
    const inStatus = taskStatus === 'all' || t.status === taskStatus;
    const inPriority = taskPriority === 'all' || t.priority === taskPriority;
    const inModule = taskModule === 'all' || t.module === taskModule;
    return inRange && inName && inStatus && inPriority && inModule;
  });

  renderTasks(tasks);
}

export async function loadTasks(statusEl) {
  try {
    const candidates = [
      '../tasks/tasks.jsonl',
      './tasks/tasks.jsonl',
      '/tasks/tasks.jsonl',
      '/workspace/tasks/tasks.jsonl'
    ];
    const result = await fetchFirst(candidates);
    const text = await result.res.text();
    allTasks = parseJsonl(text);
    applyTaskFilters();
    if (statusEl) {
      statusEl.textContent = `Loaded tasks: ${result.path.replace(/^\//, '')}`;
    }
  } catch (e) {
    if (statusEl) {
      statusEl.textContent = 'Cannot read tasks.jsonl. Use Live Preview with access to workspace files.';
    }
  }
}

export function initTasks() {
  const nameInput = document.getElementById('taskNameFilter');
  if (!nameInput) return;

  const debouncedTaskFilter = debounce(() => {
    currentPage = 1;
    applyTaskFilters();
  }, 300);

  const taskQuickButtons = Array.from(document.querySelectorAll('[data-task-range]'));

  nameInput.addEventListener('input', debouncedTaskFilter);
  document.getElementById('taskStatus')?.addEventListener('change', () => { currentPage = 1; applyTaskFilters(); });
  document.getElementById('taskPriority')?.addEventListener('change', () => { currentPage = 1; applyTaskFilters(); });
  document.getElementById('taskModule')?.addEventListener('change', () => { currentPage = 1; applyTaskFilters(); });
  document.getElementById('taskDateStart')?.addEventListener('change', () => { clearActiveButtons(taskQuickButtons); currentPage = 1; applyTaskFilters(); });
  document.getElementById('taskDateEnd')?.addEventListener('change', () => { clearActiveButtons(taskQuickButtons); currentPage = 1; applyTaskFilters(); });

  taskQuickButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      setActiveButton(taskQuickButtons, btn);
      const val = btn.getAttribute('data-task-range');
      if (val === 'today') {
        setTaskRangeDays(1);
      } else {
        const days = Number(val);
        if (!Number.isNaN(days)) setTaskRangeDays(days);
      }
      currentPage = 1;
      applyTaskFilters();
    });
  });

  document.getElementById('prevPage')?.addEventListener('click', () => {
    currentPage = Math.max(1, currentPage - 1);
    applyTaskFilters();
  });
  document.getElementById('nextPage')?.addEventListener('click', () => {
    currentPage += 1;
    applyTaskFilters();
  });
}

function setTaskRangeDays(days) {
  const today = new Date();
  const end = formatDateUTC(today);
  const startDate = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()));
  if (days > 0) {
    startDate.setUTCDate(startDate.getUTCDate() - (days - 1));
  }
  const start = formatDateUTC(startDate);
  const startInput = document.getElementById('taskDateStart');
  const endInput = document.getElementById('taskDateEnd');
  if (startInput) startInput.value = start;
  if (endInput) endInput.value = end;
}
