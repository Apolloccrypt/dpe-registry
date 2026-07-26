#!/usr/bin/env node
//
// DPE reproduction · every web entry in the catalogue, in one run
//
//   npm i playwright && npx playwright install chromium
//   node check.mjs example.nl
//
// Takes three captures with a fresh profile each: no interaction, refuse,
// accept. Then applies each entry's indicator to them. Writes the HARs and a
// JSON result beside the script, so a third party can check the conclusion
// rather than take it.
//
// One dependency, no tooling owned by the catalogue. That is deliberate: an
// entry that can only be established with our own scanner is not a finding,
// it is a claim.
//
// WHAT IT CANNOT DO, up front:
//   - a first-party CNAME to a measurement host reads as first-party here
//   - it loads one page from one location; consent flows are often geo-targeted
//   - tags that fire on scroll or deeper pages stay out of view
//   - it never submits anything, so nothing behind a form is established
// Each of these is a falsifier on the entry it affects. Read them before citing.

import { chromium } from 'playwright';
import { writeFileSync } from 'node:fs';

const target = process.argv[2];
if (!target) {
  console.error('usage: node check.mjs <domain>');
  process.exit(2);
}
const url = target.startsWith('http') ? target : `https://${target}`;
const site = new URL(url).hostname.replace(/^www\./, '');

const TWO = new Set(['co.uk', 'org.uk', 'ac.uk', 'com.au', 'co.jp', 'com.br', 'co.nz']);
const reg = h => {
  const p = h.split('.');
  if (p.length < 3) return h;
  return TWO.has(p.slice(-2).join('.')) ? p.slice(-3).join('.') : p.slice(-2).join('.');
};
const ROOT = reg(site);

// Short and auditable on purpose. A finding never rests on this list alone:
// it rests on a third party receiving an identifier. The list only labels.
const KNOWN = {
  'google-analytics.com': 'Google Analytics', 'analytics.google.com': 'Google Analytics',
  'googletagmanager.com': 'Google Tag Manager', 'doubleclick.net': 'Google Ads',
  'googlesyndication.com': 'Google Ads', 'googleadservices.com': 'Google Ads',
  'hotjar.com': 'Hotjar', 'hotjar.io': 'Hotjar', 'clarity.ms': 'Microsoft Clarity',
  'mouseflow.com': 'Mouseflow', 'fullstory.com': 'FullStory', 'smartlook.com': 'Smartlook',
  'facebook.net': 'Meta Pixel', 'facebook.com': 'Meta', 'licdn.com': 'LinkedIn',
  'bat.bing.com': 'Microsoft Ads', 'criteo.com': 'Criteo', 'tiktok.com': 'TikTok',
  'ajax.googleapis.com': 'Google Hosted Libraries', 'gstatic.com': 'Google',
  'fonts.googleapis.com': 'Google Fonts', 'cloudflareinsights.com': 'Cloudflare',
};
const RECORDERS = ['hotjar.com', 'hotjar.io', 'clarity.ms', 'mouseflow.com', 'fullstory.com', 'smartlook.com'];
const ID_RE = /(?:^|[?&])(cid|tid|_ga|uid|sid|dl|en|gtm|fbp|hjid)=/i;
const TAG_RE = /\b(G-[A-Z0-9]{6,}|UA-\d{4,}-\d+|GTM-[A-Z0-9]{4,})\b/g;
const ACCEPT = /^(accepteer|accepteren|akkoord|alles accepteren|toestaan|accept|allow|agree|ok)/i;
const REFUSE = /^(weiger|weigeren|afwijzen|alleen noodzakelijk|necessary only|reject|decline|refuse)/i;

async function capture(mode) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    locale: 'nl-NL', timezoneId: 'Europe/Amsterdam',
    recordHar: { path: `${site}-${mode}.har`, content: 'omit' },
  });
  const page = await ctx.newPage();
  const reqs = [];
  const fp = new Set();

  // Property reads that indicate fingerprinting. Injected before any page
  // script runs, so a third-party script cannot avoid the hook.
  await ctx.addInitScript(() => {
    window.__dpe = [];
    const mark = k => { try { window.__dpe.push(k); } catch {} };
    const c = HTMLCanvasElement.prototype;
    const od = c.toDataURL; c.toDataURL = function (...a) { mark('canvas'); return od.apply(this, a); };
    const dtf = Intl.DateTimeFormat.prototype.resolvedOptions;
    Intl.DateTimeFormat.prototype.resolvedOptions = function () { mark('timezone'); return dtf.call(this); };
    for (const p of ['hardwareConcurrency', 'deviceMemory', 'plugins', 'languages']) {
      const d = Object.getOwnPropertyDescriptor(Navigator.prototype, p);
      if (d && d.get) Object.defineProperty(Navigator.prototype, p, {
        get() { mark('navigator.' + p); return d.get.call(this); }, configurable: true });
    }
  });

  page.on('request', r => {
    let h; try { h = new URL(r.url()).hostname.replace(/^www\./, ''); } catch { return; }
    reqs.push({ host: h, third: reg(h) !== ROOT, url: r.url(),
                vendor: Object.keys(KNOWN).find(k => h.endsWith(k)) ? KNOWN[Object.keys(KNOWN).find(k => h.endsWith(k))] : null,
                id: ID_RE.test(r.url()), type: r.resourceType() });
  });

  const setCookies = [];
  page.on('response', async r => {
    const v = await r.headerValue('set-cookie').catch(() => null);
    if (v) for (const line of v.split('\n')) {
      const m = /max-age=(\d+)/i.exec(line);
      setCookies.push({ name: line.split('=')[0].trim(),
                        days: m ? Math.round(+m[1] / 86400) : null,
                        host: (() => { try { return new URL(r.url()).hostname; } catch { return ''; } })() });
    }
  });

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(5000);
  const doc = await page.content();

  // Banner state before touching anything, plus whether a refusal exists at all.
  const banner = await page.evaluate(() => {
    const el = [...document.querySelectorAll('div,section,aside,dialog')].find(x => {
      const t = (x.innerText || '').toLowerCase();
      return t.length < 1500 && /cookie|toestemming|consent|accepteer|akkoord/.test(t)
        && x.offsetHeight > 30 && getComputedStyle(x).display !== 'none';
    });
    if (!el) return null;
    return { text: el.innerText.slice(0, 400),
             buttons: [...el.querySelectorAll('button,a[role=button],input[type=button],[class*=btn]')]
               .map(b => (b.innerText || b.value || '').trim()).filter(Boolean).slice(0, 12) };
  });

  let clicked = null;
  if (mode !== 'noop' && banner) {
    const want = mode === 'reject' ? REFUSE : ACCEPT;
    const btn = (banner.buttons || []).find(t => want.test(t));
    if (btn) {
      try {
        await page.getByRole('button', { name: btn, exact: false }).first().click({ timeout: 4000 });
        clicked = btn;
        await page.waitForTimeout(4000);
      } catch { clicked = null; }
    }
  }

  const marks = await page.evaluate(() => window.__dpe || []).catch(() => []);
  marks.forEach(m => fp.add(m));
  const cookies = await ctx.cookies();
  await ctx.close();
  await browser.close();
  return { mode, reqs, setCookies, cookies, doc, banner, clicked, fp: [...fp] };
}

// ---------------------------------------------------------------- entries

const R = {};
const add = (id, title, verdict, detail) => { R[id] = { id, title, verdict, detail }; };
const hostsOf = c => new Set(c.reqs.filter(r => r.third).map(r => r.host));
const measOf = c => c.reqs.filter(r => r.third && (r.vendor || r.id));

function assess(noop, reject, accept) {
  // 0001 tracking before consent
  const m = measOf(noop);
  add('DPE-2026-0001', 'Tracking before consent', m.length ? 'present' : 'not-found',
      { measurement_requests: m.length, with_identifier: m.filter(r => r.id).length,
        vendors: [...new Set(m.map(r => r.vendor).filter(Boolean))] });

  // 0002 refusal without effect (differential; only if a refusal was actually made)
  if (reject && reject.clicked) {
    const a = hostsOf(noop), b = hostsOf(reject);
    const survivors = [...b].filter(h => Object.keys(KNOWN).some(k => h.endsWith(k)));
    add('DPE-2026-0002', 'Refusal without effect', survivors.length ? 'present' : 'not-found',
        { clicked: reject.clicked, hosts_noop: a.size, hosts_reject: b.size, survivors });
  } else {
    add('DPE-2026-0002', 'Refusal without effect', 'not-assessed',
        { reason: reject && reject.banner ? 'no refusal control found to click' : 'no banner found' });
  }

  // 0003 no refusal option
  if (noop.banner) {
    const has = (noop.banner.buttons || []).some(t => REFUSE.test(t));
    add('DPE-2026-0003', 'No refusal option', has ? 'not-found' : 'present',
        { buttons: noop.banner.buttons });
  } else {
    add('DPE-2026-0003', 'No refusal option', 'not-assessed',
        { reason: 'no consent dialogue detected; nothing was asked at all' });
  }

  // 0004 maximum cookie lifetime, pre-consent
  const long = noop.setCookies.filter(c => c.days && c.days >= 390);
  const jar = noop.cookies.filter(c => c.expires > 0
    && (c.expires * 1000 - Date.now()) / 864e5 >= 390);
  add('DPE-2026-0004', 'Maximum cookie lifetime', (long.length || jar.length) ? 'present' : 'not-found',
      { from_headers: long.map(c => `${c.name} ${c.days}d`),
        from_jar: jar.map(c => `${c.name} ${Math.round((c.expires * 1000 - Date.now()) / 864e5)}d`) });

  // 0005 session recording
  const rec = noop.reqs.filter(r => RECORDERS.some(k => r.host.endsWith(k)));
  add('DPE-2026-0005', 'Session recording', rec.length ? 'present' : 'not-found',
      { hosts: [...new Set(rec.map(r => r.host))] });

  // 0007 device fingerprinting
  add('DPE-2026-0007', 'Device fingerprinting', noop.fp.length ? 'present' : 'not-found',
      { reads: noop.fp, note: 'reads are hooked before page scripts run; attribution per script needs the trace' });

  // 0009 third-party resource loading
  const sub = noop.reqs.filter(r => r.third && ['script', 'stylesheet', 'font', 'image'].includes(r.type));
  add('DPE-2026-0009', 'Third-party resource loading', sub.length ? 'present' : 'not-found',
      { count: sub.length, hosts: [...new Set(sub.map(r => r.host))].slice(0, 12) });

  // 0011 tag loaded outside the source (set comparison)
  const ids = new Set();
  noop.reqs.forEach(r => { for (const mm of r.url.matchAll(TAG_RE)) ids.add(mm[1]); });
  const missing = [...ids].filter(i => !noop.doc.includes(i));
  add('DPE-2026-0011', 'Tag loaded outside the source', missing.length ? 'present' : 'not-found',
      { ids_seen: [...ids], not_in_html: missing });
}

// ---------------------------------------------------------------- run

console.log(`DPE web check · ${site} · ${new Date().toISOString().slice(0, 10)}\n`);
const noop = await capture('noop');
console.log(`  noop    ${noop.reqs.length} requests, banner ${noop.banner ? 'present' : 'absent'}`);
const reject = await capture('reject');
console.log(`  reject  ${reject.reqs.length} requests, clicked ${reject.clicked || 'nothing'}`);
const accept = await capture('accept');
console.log(`  accept  ${accept.reqs.length} requests, clicked ${accept.clicked || 'nothing'}\n`);

assess(noop, reject, accept);

const W = { present: 'PRESENT', 'not-found': 'not found', 'not-assessed': 'not assessed' };
for (const r of Object.values(R))
  console.log(`${r.id}  ${W[r.verdict].padEnd(13)} ${r.title}\n${' '.repeat(16)}${JSON.stringify(r.detail)}`);

const out = { site, measured_at: new Date().toISOString(), method: 'DPE Measurement Method 1.0',
  conditions: { profile: 'clean per capture', interaction: 'none / refuse / accept',
                locale: 'nl-NL', timezone: 'Europe/Amsterdam',
                exit_country: 'set this yourself; consent flows are geo-targeted' },
  results: Object.values(R),
  captures: ['noop', 'reject', 'accept'].map(m => `${site}-${m}.har`) };
writeFileSync(`${site}-dpe.json`, JSON.stringify(out, null, 2));

console.log(`
Wrote ${site}-dpe.json and three HAR files. Open a HAR at https://trace.playwright.dev
to check any of this yourself.

Before citing a PRESENT verdict, work through that entry's falsifiers at
totaledigitalewaarborging.nl/register. This script cannot resolve a first-party
CNAME, measures one page from one location, and never submits anything. A
not-found is not evidence of absence.`);
process.exit(Object.values(R).some(r => r.verdict === 'present') ? 1 : 0);
