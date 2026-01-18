export function parseJsonl(text) {
  return text.split(/\r?\n/).filter(Boolean).map(line => {
    try {
      return JSON.parse(line);
    } catch (e) {
      return { _parseError: true, raw: line };
    }
  });
}

export function extractDateOnly(value) {
  if (!value) return null;
  if (typeof value === 'string') {
    const m = value.match(/^(\d{4}-\d{2}-\d{2})/);
    if (m) return m[1];
  }
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return null;
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export function inDateRange(iso, start, end) {
  if (!start && !end) return true;
  const d = extractDateOnly(iso);
  if (!d) return false;
  if (start && d < start) return false;
  if (end && d > end) return false;
  return true;
}

export function parseDateInput(value) {
  if (!value) return null;
  const m = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return null;
  const y = Number(m[1]);
  const mo = Number(m[2]) - 1;
  const d = Number(m[3]);
  const dt = new Date(Date.UTC(y, mo, d));
  return Number.isNaN(dt.getTime()) ? null : dt;
}

export function formatDateUTC(date) {
  const yyyy = date.getUTCFullYear();
  const mm = String(date.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(date.getUTCDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export function formatDateShort(value) {
  if (!value) return '';
  if (typeof value === 'string') {
    const datePart = value.split('T')[0];
    return datePart || value;
  }
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return extractDateOnly(d);
}

export function formatTimeShort(value) {
  if (!value) return '';
  if (typeof value === 'string') {
    const match = value.match(/T(\d{2}:\d{2})/);
    if (match) return match[1];
  }
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  return `${hh}:${mm}`;
}

export function formatDateTime(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd} ${hh}:${min}`;
}

export function toText(val) {
  if (!val) return '';
  if (Array.isArray(val)) return val.join(', ');
  return String(val);
}

export function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

export function setActiveButton(buttons, active) {
  buttons.forEach(btn => btn.classList.toggle('active', btn === active));
}

export function clearActiveButtons(buttons) {
  buttons.forEach(btn => btn.classList.remove('active'));
}

export async function fetchFirst(paths) {
  let lastError = null;
  for (const p of paths) {
    try {
      const res = await fetch(p);
      if (res.ok) return { res, path: p };
    } catch (e) {
      lastError = e;
    }
  }
  throw lastError || new Error('all fetch attempts failed');
}
