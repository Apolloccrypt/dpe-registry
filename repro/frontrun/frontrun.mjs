#!/usr/bin/env node
//
// DPE registry · reproduction snippet · pattern: frontrun
// "A tag fires before the consent question has been answered."
//
// Standalone. One dependency: playwright. No registry tooling is involved, so
// anyone can run this and reach their own conclusion.
//
//   npm i playwright && npx playwright install chromium
//   node frontrun.mjs pgwoo.nl
//
// Writes <domain>-pre.har next to the script. Open it at trace.playwright.dev
// or in the Chrome devtools network panel; no install needed to read it.
//
// WHAT THIS DOES NOT DO: it does not click anything. That is the whole point.
// Every request it records happened before the visitor could answer.

import { chromium } from 'playwright';
import { writeFileSync } from 'node:fs';

const target = process.argv[2];
if (!target) {
  console.error('usage: node frontrun.mjs <domain>   e.g. node frontrun.mjs pgwoo.nl');
  process.exit(2);
}
const url = target.startsWith('http') ? target : `https://${target}`;
const site = new URL(url).hostname.replace(/^www\./, '');

// Hosts whose sole function is measurement or advertising. Deliberately short
// and auditable: a long list invites disagreement about its edges. Anything
// third-party that sets a cookie is reported regardless of this list.
const MEASUREMENT = [
  'google-analytics.com', 'analytics.google.com', 'googletagmanager.com',
  'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
  'hotjar.com', 'hotjar.io', 'clarity.ms', 'matomo.cloud',
  'facebook.net', 'facebook.com/tr', 'linkedin.com/px', 'ads.linkedin.com',
  'bat.bing.com', 'tiktok.com/i18n/pixel', 'snap.licdn.com',
];

// Registrable-domain approximation. Adequate for .nl/.com/.org and the common
// two-part suffixes; not a full public suffix list. Stated as a limitation
// rather than hidden, because attribution errors are how false findings happen.
const TWO_PART = new Set(['co.uk', 'org.uk', 'ac.uk', 'com.au', 'co.jp', 'com.br', 'co.nz']);
function registrable(host) {
  const p = host.split('.');
  if (p.length < 3) return host;
  const last2 = p.slice(-2).join('.');
  return TWO_PART.has(last2) ? p.slice(-3).join('.') : last2;
}
const siteRoot = registrable(site);

const browser = await chromium.launch();               // headless, clean profile
const context = await browser.newContext({
  locale: 'nl-NL',
  timezoneId: 'Europe/Amsterdam',
  recordHar: { path: `${site}-pre.har`, content: 'omit' },
});
const page = await context.newPage();

const requests = [];
page.on('request', r => {
  const h = new URL(r.url()).hostname;
  requests.push({
    host: h,
    root: registrable(h),
    thirdParty: registrable(h) !== siteRoot,
    method: r.method(),
    // An identifier-bearing request is the difference between "a font loaded"
    // and "someone was counted".
    carriesId: /(?:^|[?&])(?:cid|_ga|tid|gtm|uid|sid|dl|_p|en)=/.test(r.url()),
    url: r.url().slice(0, 200),
  });
});

// domcontentloaded plus a fixed settle window. Deliberately not
// networkidle: a page with long-polling never idles and the run would hang.
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
await page.waitForTimeout(6000);

// Is there anything to consent to in the first place? A banner that is absent
// changes the reading: no banner means no consent was sought at all.
const bannerText = await page.evaluate(() => {
  const hit = [...document.querySelectorAll('div,section,aside,dialog')].find(el => {
    const t = (el.innerText || '').toLowerCase();
    return t.length < 1200 && /cookie|toestemming|consent|accepteer|akkoord/.test(t)
      && getComputedStyle(el).display !== 'none';
  });
  return hit ? hit.innerText.trim().slice(0, 300) : null;
});

const cookies = await context.cookies();
await context.close();
await browser.close();

const third = requests.filter(r => r.thirdParty);
const measured = third.filter(r => MEASUREMENT.some(m => r.host.includes(m.split('/')[0])));
const idCookies = cookies.filter(c => registrable(c.domain.replace(/^\./, '')) !== siteRoot
  || /^_ga|^_gid|^_fbp|^_hj/.test(c.name));

const verdict = measured.length > 0 ? 'FRONTRUN DETECTED' : 'not detected';

console.log(`
DPE reproduction · pattern frontrun · ${site} · ${new Date().toISOString().slice(0, 10)}
${'='.repeat(72)}
consent banner present   ${bannerText ? 'yes' : 'NO (nothing was asked at all)'}
requests before answer   ${requests.length} total, ${third.length} third-party
measurement hosts hit    ${measured.length}
identifier-bearing       ${measured.filter(r => r.carriesId).length}
tracking cookies set     ${idCookies.length}${idCookies.length ? '  ' + idCookies.map(c => c.name).join(', ') : ''}
har                      ${site}-pre.har   (open at trace.playwright.dev)

VERDICT  ${verdict}
${'='.repeat(72)}`);

if (measured.length) {
  console.log('\nmeasurement requests fired before the visitor answered:');
  for (const r of measured) console.log(`  ${r.carriesId ? 'ID' : '  '}  ${r.method}  ${r.url}`);
}

// Cookie lifetimes: 399 days is Chrome's ceiling and its presence pre-consent
// is a separate pattern (maxstay).
const longest = cookies.filter(c => c.expires > 0)
  .sort((a, b) => b.expires - a.expires)[0];
if (longest) {
  const days = Math.round((longest.expires * 1000 - Date.now()) / 86400000);
  console.log(`\nlongest cookie lifetime  ${days} days  (${longest.name})`);
}

writeFileSync(`${site}-pre.json`, JSON.stringify(
  { site, measured_at: new Date().toISOString(), verdict, banner: bannerText,
    requests, cookies: cookies.map(c => ({ name: c.name, domain: c.domain, expires: c.expires })) },
  null, 2));

console.log(`\nraw result written to ${site}-pre.json`);
console.log(`
LIMITATIONS, read before citing this
  - one page load from one location; a CMP may geo-target other regions differently
  - registrable-domain check is an approximation, not a public suffix list
  - a first-party CNAME to a tracker reads as first-party here and would be missed
  - absence of a detection is not evidence of absence: tags can load on scroll,
    on interaction, or only on inner pages
`);
process.exit(measured.length ? 1 : 0);   // exit 1 on detection, for CI use
