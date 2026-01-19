import { parseJsonl, formatDateTime, toText } from './common.js';

let allKnowledge = [];
let knowledgeTimer = null;

function renderKnowledge(items) {
  const list = document.getElementById('knowledgeList');
  if (!list) return;
  list.innerHTML = '';
  if (items.length === 0) {
    list.innerHTML = '<div class="empty muted">鏆傛棤鐭ヨ瘑鍗＄墖銆?/div>';
    return;
  }
  for (const item of items) {
    const card = document.createElement('div');
    card.className = 'card';
    const tags = Array.isArray(item.tags) ? item.tags : [];
    card.innerHTML = `
      <div class="knowledge-title">${item.title || '(未命名)'}</div>
      <div class="knowledge-meta">
        <span class="mono">${formatDateTime(item.timestamp)}</span>
        ${tags.map(t => `<span class="tag">${t}</span>`).join('')}
      </div>
      <div class="kv">
        ${item.summary ? `<div class="kv-row"><div class="kv-key">摘要</div><div>${item.summary}</div></div>` : ''}
        ${item.problem ? `<div class="kv-row"><div class="kv-key">问题</div><div>${item.problem}</div></div>` : ''}
        ${item.symptom ? `<div class="kv-row"><div class="kv-key">现象</div><div>${item.symptom}</div></div>` : ''}
        ${item.root_cause ? `<div class="kv-row"><div class="kv-key">根因</div><div>${item.root_cause}</div></div>` : ''}
        ${item.solution ? `<div class="kv-row"><div class="kv-key">解决方案</div><div>${item.solution}</div></div>` : ''}
        ${item.environment ? `<div class="kv-row"><div class="kv-key">环境</div><div>${item.environment}</div></div>` : ''}
        ${item.examples ? `<div class="kv-row"><div class="kv-key">示例</div><div>${toText(item.examples)}</div></div>` : ''}
      </div>
    `;
    list.appendChild(card);
  }
}

function applyKnowledgeFilters() {
  const search = (document.getElementById('knowledgeSearch')?.value || '').trim().toLowerCase();
  if (!search) {
    renderKnowledge(allKnowledge);
    return;
  }
  const filtered = allKnowledge.filter(item => {
    const blob = JSON.stringify(item).toLowerCase();
    return blob.includes(search);
  });
  renderKnowledge(filtered);
}

function getKnowledgeBase() {
  const path = location.pathname || '';
  const root = path.includes('/workspace/') ? '/workspace/' : '/';
  return `${root}knowledge/knowledge.jsonl`;
}

async function loadKnowledge() {
  const status = document.getElementById('knowledgeStatus');
  try {
    const res = await fetch(getKnowledgeBase(), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    const items = parseJsonl(text).filter(i => !i._parseError);
    items.sort((a, b) => (Date.parse(b.timestamp || '') || 0) - (Date.parse(a.timestamp || '') || 0));
    allKnowledge = items;
    if (status) status.textContent = `已加载 ${items.length} 条`;
    applyKnowledgeFilters();
  } catch (e) {
    if (status) status.textContent = '无法读取 knowledge.jsonl。请使用 Live Server。';
    renderKnowledge([]);
  }
}

export function initKnowledge() {
  const search = document.getElementById('knowledgeSearch');
  if (!search) return;

  search.addEventListener('input', applyKnowledgeFilters);
  document.getElementById('knowledgeRefresh')?.addEventListener('click', loadKnowledge);
  document.getElementById('knowledgeAutoRefresh')?.addEventListener('change', () => {
    if (document.getElementById('knowledgeAutoRefresh')?.checked) {
      loadKnowledge();
    }
  });

  if (knowledgeTimer) clearInterval(knowledgeTimer);
  knowledgeTimer = setInterval(() => {
    const checkbox = document.getElementById('knowledgeAutoRefresh');
    if (checkbox && checkbox.checked) loadKnowledge();
  }, 10000);

  loadKnowledge();
}
