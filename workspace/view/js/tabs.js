export async function loadTabPartials() {
  const panels = Array.from(document.querySelectorAll('.tab-panel[data-src]'));
  for (const panel of panels) {
    const src = panel.getAttribute('data-src');
    if (!src) continue;
    try {
      const res = await fetch(src);
      panel.innerHTML = res.ok ? await res.text() : '<div class="warn">鏃犳硶鍔犺浇鏍囩鍐呭銆?/div>';
    } catch (e) {
      panel.innerHTML = '<div class="warn">鏃犳硶鍔犺浇鏍囩鍐呭锛岃浣跨敤 Live Server銆?/div>';
    }
  }
}

export function initTabs() {
  const tabButtons = Array.from(document.querySelectorAll('.tab-button'));
  const tabPanels = Array.from(document.querySelectorAll('.tab-panel'));
  function activateTab(name) {
    tabButtons.forEach(btn => {
      const isActive = btn.dataset.tab === name;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
    tabPanels.forEach(panel => {
      panel.classList.toggle('active', panel.id === `tab-${name}`);
    });
  }
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => activateTab(btn.dataset.tab));
  });
  return activateTab;
}
