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

  // Per catalogus-entry een uitslag, met het nummer erbij. Dat het nummer hier
  // staat en niet in een handleiding, is het verschil tussen wel en niet
  // gebruikt worden: niemand zoekt zelf uit welk nummer bij een waarneming hoort.
  const REC = ['hotjar.com','hotjar.io','clarity.ms','mouseflow.com','fullstory.com','smartlook.com'];
  const SUB = third.filter(t => /script|css|font|image/i.test(t.type || ''));
  const long = document.cookie ? [] : [];
  const found = [
    { id: 'DPE-2026-0001', nl: 'Meten voor de toestemmingsvraag',
      hit: (vendors.length > 0 || withId.length > 0) && !!banner,
      why: `${vendors.length} meetpartij(en) aangesproken terwijl de banner nog onbeantwoord was` },
    { id: 'DPE-2026-0003', nl: 'Geen weigeroptie',
      hit: !!banner && !/weiger|afwijzen|noodzakelijk|reject|decline/i.test(banner.innerText || ''),
      why: 'in de zichtbare banner staat geen knop die weigeren mogelijk maakt' },
    { id: 'DPE-2026-0005', nl: 'Sessieopname',
      hit: third.some(t => REC.some(k => t.host.endsWith(k))),
      why: 'er wordt een partij aangesproken die sessies opneemt, niet alleen paginaweergaven' },
    { id: 'DPE-2026-0009', nl: 'Externe bron inladen',
      hit: SUB.length > 0,
      why: `${SUB.length} bron(nen) worden van een andere partij ingeladen bij het openen van de pagina` },
  ].filter(x => x.hit);

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
    #dpe-panel .dpe{display:flex;flex-direction:column;gap:7px;margin:12px 0 14px}
    #dpe-panel .d{display:block;padding:11px 13px;border-radius:7px;text-decoration:none;
      background:#1e2529;border:1px solid #2f3a40}
    #dpe-panel .d:hover{border-color:#4269d0;background:#1b2437}
    #dpe-panel .did{font-family:inherit;font-size:11.5px;color:#7c9be8;letter-spacing:.04em}
    #dpe-panel .dnl{display:block;font:600 15px/1.3 ui-sans-serif,system-ui;color:#e7ebe9;margin:3px 0 4px}
    #dpe-panel .dw{display:block;font-size:12px;color:#8b9491;line-height:1.5}
    #dpe-panel .note{color:#78827f;margin-top:12px;font-size:11.5px;max-width:80ch}
    #dpe-panel .cp{margin-top:10px;background:#262c2e;color:#e7ebe9;border:0;padding:6px 12px;
      border-radius:3px;cursor:pointer;font:inherit;font-size:12px}
  </style>
  <button class="x" aria-label="sluiten">&times;</button>
  <h2>${found.length ? found.length + ' bevinding' + (found.length > 1 ? 'en' : '') : 'Geen bevinding'} op ${esc(SITE)}</h2>
  ${found.length ? '<div class="dpe">' + found.map(f =>
    `<a class="d" href="https://totaledigitalewaarborging.nl/register/${f.id}" target="_blank" rel="noopener">
       <span class="did">${f.id}</span><span class="dnl">${esc(f.nl)}</span><span class="dw">${esc(f.why)}</span></a>`
  ).join('') + '</div>' : ''}
  <div class="sub">
    cookiebanner ${banner ? 'staat nog onbeantwoord op het scherm' : 'niet gevonden'} ·
    ${third.length} third-party resources · ${withId.length} met identifier ·
    ${tracking.length ? 'trackingcookies: ' + esc(tracking.join(', ')) : 'geen trackingcookies zichtbaar'}
  </div>
  ${vendors.map(v => `<span class="v">${esc(v)}</span>`).join('')}
  ${third.length ? `<table>${third.sort((a, b) => (b.id - a.id)).slice(0, 40).map(row).join('')}</table>` : ''}
  <button class="cp">Kopieer als tekst voor je DPIA of mail</button>
  <div class="note">
    Wat dit wel zegt: deze resources zijn geladen${banner ? ' terwijl de toestemmingsvraag nog openstond' : ''}.
    Wat dit niet ziet: HttpOnly-cookies, request-bodies, en verkeer in cross-origin iframes.
    Voor een sluitend bewijs is een HAR nodig; zie het register.
    Meet in een prive-venster en raak de banner niet aan, anders meet je iets anders.
  </div>`;
  document.body.appendChild(box);
  box.querySelector('.x').onclick = () => box.remove();
  box.querySelector('.cp').onclick = e => {
    // Plakbaar in een DPIA, een mail aan de leverancier of een melding. Ruwe
    // JSON helpt niemand die geen JSON leest, en dat is de meerderheid.
    const d = new Date().toISOString().slice(0, 10);
    const txt = [
      `Waarneming op ${SITE}, ${d}`,
      `Gemeten in een prive-venster, zonder de cookiebanner aan te raken.`,
      ``,
      found.length ? `Aangetroffen:` : `Geen van de getoetste bevindingen aangetroffen.`,
      ...found.map(f => `- ${f.id} (${f.nl}): ${f.why}. Zie totaledigitalewaarborging.nl/register/${f.id}`),
      ``,
      `Partijen die werden aangesproken: ${vendors.join(', ') || 'geen herkende'}`,
      tracking.length ? `Cookies gezet voor enige keuze: ${tracking.join(', ')}` : '',
      ``,
      `Dit is een eerste waarneming met een bookmarklet, geen sluitend bewijs.`,
      `Zij toont wat de pagina laadde voordat er iets gekozen was; zij ziet geen`,
      `HttpOnly-cookies, geen inhoud van verzoeken en niets in iframes van derden.`,
      `Vraag om een netwerkopname met datum voor een volledig beeld.`,
    ].filter(x => x !== undefined).join('\n');
    navigator.clipboard.writeText(txt);
    e.target.textContent = 'Gekopieerd, plak het in je DPIA of mail';
  };
})();
