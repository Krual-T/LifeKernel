import { loadTabPartials, initTabs } from './tabs.js';
import { initTasks, loadTasks } from './tasks.js';
import { initLogs } from './logs.js';
import { initKnowledge } from './knowledge.js';

function showCorsNotice() {
  const notice = document.getElementById('corsNotice');
  if (!notice) return;
  if (location.protocol === 'file:') {
    notice.style.display = 'block';
    notice.innerHTML = '妫€娴嬪埌 file:// 璁块棶锛岃浣跨敤 Live Server 鎵撳紑椤甸潰銆?;
  }
}

async function initApp() {
  await loadTabPartials();
  initTabs();

  const statusEl = document.getElementById('status');
  initTasks();
  await loadTasks(statusEl);

  initLogs(statusEl);
  initKnowledge();

  showCorsNotice();
}

document.addEventListener('DOMContentLoaded', initApp);
