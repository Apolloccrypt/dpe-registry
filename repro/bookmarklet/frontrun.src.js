/*
 * DPE registry · in-browser check · patterns: frontrun, maxstay, hotlink
 *
 * A bookmarklet. Drag it to your bookmarks bar, open any site in a private
 * window, do NOT touch the cookie banner, then click it.
 *
 * Why this works without installing anything: the Resource Timing API keeps a
 * complete list of every resource the page has loaded, including full URLs with
 * their query strings, from before you clicked. So a bookmarklet fired after
 * the fact still sees what happened at load time.
 *
 * What it cannot see, stated up front:
 *   - HttpOnly cookies (by design)
 *   - request and response bodies; only URLs
 *   - anything loaded inside a cross-origin iframe
 *   - whether a request was blocked or actually answered
 * For those you need the HAR route. This is a first check, not a court exhibit.
 */
(() => {
  const SITE = location.hostname.replace(/^www\./, '');
  const TWO = new Set(['co.uk', 'org.uk', 'ac.uk', 'com.au', 'co.jp', 'com.br', 'co.nz']);
  const reg = h => {
    const p = h.split('.');
    if (p.length < 3) return h;
    return TWO.has(p.slice(-2).join('.')) ? p.slice(-3).join('.') : p.slice(-2).join('.');
  };
  const ROOT = reg(SITE);

  // Deliberately short and auditable. A finding does not rest on this list:
  // it rests on a third party receiving an identifier. The list only labels.
  const KNOWN = {
    'google-analytics.com': 'Google Analytics', 'analytics.google.com': 'Google Analytics',
    'googletagmanager.com': 'Google Tag Manager', 'doubleclick.net': 'Google Ads',
    'googlesyndication.com': 'Google Ads', 'googleadservices.com': 'Google Ads',
    'hotjar.com': 'Hotjar (session recording)', 'hotjar.io': 'Hotjar (session recording)',
    'clarity.ms': 'Microsoft Clarity (session recording)',
    'facebook.net': 'Meta Pixel', 'facebook.com': 'Meta',
    'linkedin.com': 'LinkedIn', 'licdn.com': 'LinkedIn',
    'bing.com': 'Microsoft Ads', 'tiktok.com': 'TikTok', 'criteo.com': 'Criteo',
    'ajax.googleapis.com': 'Google Hosted Libraries', 'gstatic.com': 'Google',
    'fonts.googleapis.com': 'Google Fonts',
  };
  const ID_RE = /(?:^|[?&])(cid|tid|_ga|uid|sid|dl|en|gtm|fbp|hjid)=/i;

  const res = performance.getEntriesByType('resource');
  const third = [];
  for (const r of res) {
    let h;
    try { h = new URL(r.name).hostname; } catch { continue; }
    if (reg(h) === ROOT) continue;
    const label = Object.keys(KNOWN).find(k => h.endsWith(k));
    third.push({ host: h, url: r.name, vendor: label ? KNOWN[label] : null,
                 id: ID_RE.test(r.name), type: r.initiatorType });
  }

  // A cookie banner still on screen means nothing was answered yet.
  const banner = [...document.querySelectorAll('div,section,aside,dialog')].find(el => {
    const t = (el.innerText || '').toLowerCase();
    return t.length < 1200 && /cookie|toestemming|consent|accepteer|akkoord|privacy/.test(t)
      && el.offsetHeight > 30 && getComputedStyle(el).display !== 'none';
  });

  const cookies = document.cookie.split(';').map(c => c.trim().split('=')[0]).filter(Boolean);
  const tracking = cookies.filter(c => /^(_ga|_gid|_gcl|_fbp|_hj|_uet|_tt)/.test(c));

  const vendors = [...new Set(third.filter(t => t.vendor).map(t => t.vendor))];
  const withId = third.filter(t => t.id);
  const hit = vendors.length > 0 || withId.length > 0;

  // ---- report, rendered over the page ------------------------------------
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const row = t => `<tr><td>${t.id ? '<b title="carries an identifier">ID</b>' : ''}</td>
    <td>${esc(t.vendor || '')}</td><td class="h">${esc(t.host)}</td>
    <td class="u" title="${esc(t.url)}">${esc(t.url.slice(0, 110))}</td></tr>`;

  const old = document.getElementById('dpe-panel'); if (old) old.remove();
  const box = document.createElement('div');
  box.id = 'dpe-panel';
  box.innerHTML = `<style>
    #dpe-panel{position:fixed;inset:auto 0 0 0;z-index:2147483647;max-height:72vh;overflow:auto;
      background:#14181a;color:#e7ebe9;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;
      border-top:3px solid ${hit ? '#d99a5c' : '#5fbfae'};box-shadow:0 -8px 30px #0008;padding:16px 18px}
    #dpe-panel h2{margin:0 0 4px;font:600 15px/1.3 ui-sans-serif,system-ui;letter-spacing:.01em}
    #dpe-panel .sub{color:#8b9491;margin-bottom:12px}
    #dpe-panel .v{display:inline-block;padding:2px 8px;border-radius:2px;margin:0 6px 6px 0;
      background:${hit ? '#3a2a18' : '#16302c'};color:${hit ? '#d99a5c' : '#5fbfae'}}
    #dpe-panel table{border-collapse:collapse;width:100%;margin-top:8px;font-size:11.5px}
    #dpe-panel td{padding:3px 8px 3px 0;border-bottom:1px solid #262c2e;vertical-align:top}
    #dpe-panel td.h{color:#e7ebe9;white-space:nowrap}
    #dpe-panel td.u{color:#78827f;word-break:break-all}
    #dpe-panel b{color:#d99a5c}
    #dpe-panel .x{position:absolute;top:10px;right:14px;cursor:pointer;color:#78827f;
      font-size:20px;line-height:1;background:none;border:0}
    #dpe-panel .note{color:#78827f;margin-top:12px;font-size:11.5px;max-width:80ch}
    #dpe-panel .cp{margin-top:10px;background:#262c2e;color:#e7ebe9;border:0;padding:6px 12px;
      border-radius:3px;cursor:pointer;font:inherit;font-size:12px}
  </style>
  <button class="x" aria-label="sluiten">&times;</button>
  <h2>${hit ? 'Meetverkeer aangetroffen' : 'Geen meetverkeer aangetroffen'} op ${esc(SITE)}</h2>
  <div class="sub">
    cookiebanner ${banner ? 'staat nog onbeantwoord op het scherm' : 'niet gevonden'} ·
    ${third.length} third-party resources · ${withId.length} met identifier ·
    ${tracking.length ? 'trackingcookies: ' + esc(tracking.join(', ')) : 'geen trackingcookies zichtbaar'}
  </div>
  ${vendors.map(v => `<span class="v">${esc(v)}</span>`).join('')}
  ${third.length ? `<table>${third.sort((a, b) => (b.id - a.id)).slice(0, 40).map(row).join('')}</table>` : ''}
  <button class="cp">Kopieer als JSON voor een melding</button>
  <div class="note">
    Wat dit wel zegt: deze resources zijn geladen${banner ? ' terwijl de toestemmingsvraag nog openstond' : ''}.
    Wat dit niet ziet: HttpOnly-cookies, request-bodies, en verkeer in cross-origin iframes.
    Voor een sluitend bewijs is een HAR nodig; zie het register.
    Meet in een prive-venster en raak de banner niet aan, anders meet je iets anders.
  </div>`;
  document.body.appendChild(box);
  box.querySelector('.x').onclick = () => box.remove();
  box.querySelector('.cp').onclick = e => {
    navigator.clipboard.writeText(JSON.stringify({
      site: SITE, measured_at: new Date().toISOString(), banner_present: !!banner,
      third_party: third, tracking_cookies: tracking, user_agent: navigator.userAgent,
    }, null, 2));
    e.target.textContent = 'Gekopieerd';
  };
})();
