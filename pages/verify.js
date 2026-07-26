const TWO = new Set(['co.uk','org.uk','ac.uk','com.au','co.jp','com.br','co.nz']);
const reg = h => { const p=h.split('.'); if(p.length<3) return h;
  return TWO.has(p.slice(-2).join('.')) ? p.slice(-3).join('.') : p.slice(-2).join('.'); };
const KNOWN = {'google-analytics.com':'Google Analytics','analytics.google.com':'Google Analytics',
  'googletagmanager.com':'Google Tag Manager','doubleclick.net':'Google Ads',
  'googlesyndication.com':'Google Ads','googleadservices.com':'Google Ads',
  'hotjar.com':'Hotjar','hotjar.io':'Hotjar','clarity.ms':'Microsoft Clarity',
  'facebook.net':'Meta Pixel','facebook.com':'Meta','licdn.com':'LinkedIn',
  'ajax.googleapis.com':'Google Hosted Libraries','gstatic.com':'Google','fonts.googleapis.com':'Google Fonts'};
const ID_RE = /(?:^|[?&])(cid|tid|_ga|uid|sid|dl|en|gtm|fbp|hjid)=/i;
const esc = s => String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

const RULES = {
  frontrun: {
    name:'Frontrun', qod:95, basis:'traffic-property',
    one:'Een tag vuurt voordat de toestemmingsvraag is beantwoord.',
    run(e, root){
      const third = e.filter(r => reg(r.host) !== root);
      const meas  = third.filter(r => r.vendor || r.id);
      return {
        hit: meas.length > 0, rows: meas,
        stats: {'entries':e.length,'third-party':third.length,'met identifier':third.filter(r=>r.id).length,
                'meethosts':new Set(meas.filter(r=>r.vendor).map(r=>r.vendor)).size},
        fals: [
          {ok: meas.some(r=>r.id), t:'getoetst',
           c:'Draagt minstens een verzoek een identifier? Zonder identifier is de gevolgtrekking zwakker.'},
          {ok: false, t:'niet toetsbaar uit een HAR',
           c:'Is de meethost een first-party CNAME naar het doeldomein? Dat vereist DNS-resolutie op het meetmoment.'},
          {ok: false, t:'niet toetsbaar uit een HAR',
           c:'Was de opname gemaakt zonder interactie en met een schoon profiel? Dat staat in de opnamecondities, niet in het bestand.'},
        ]};
    }},
  maxstay: {
    name:'MaxStay', qod:95, basis:'traffic-property',
    one:'Een cookie met maximale bewaartermijn, gezet voor de vraag.',
    run(e, root){
      const rows = [];
      for (const r of e) for (const c of r.cookies) {
        const m = /max-age=(\d+)/i.exec(c.raw||'');
        const days = m ? Math.round(+m[1]/86400) : (c.expires ? Math.round((new Date(c.expires)-Date.now())/864e5) : null);
        if (days !== null && days >= 180)
          rows.push({host:r.host, vendor:r.vendor, id:days>=390, url:`${c.name} · ${days} dagen`});
      }
      return {hit: rows.some(r=>r.id), rows,
        stats:{'cookies >= 180d':rows.length,'op of boven 390d':rows.filter(r=>r.id).length},
        fals:[{ok:false,t:'handmatig',c:'Is de cookie strikt noodzakelijk voor een door de bezoeker gevraagde dienst? Dat is een oordeel, geen meting.'}]};
    }},
  hotlink: {
    name:'Hotlink', qod:95, basis:'traffic-property',
    one:'Een bron van een derde inladen is bij elke weergave een doorgifte.',
    run(e, root){
      const rows = e.filter(r => reg(r.host) !== root && /script|css|font|image/i.test(r.type||''));
      return {hit: rows.length > 0, rows,
        stats:{'externe bronnen':rows.length,'unieke hosts':new Set(rows.map(r=>r.host)).size},
        fals:[{ok:false,t:'handmatig',c:'Wordt de bron via een eigen proxy geserveerd? Dan staat er een andere host in de HAR en valt deze bevinding weg.'}]};
    }},
  sideload: {
    name:'Sideload', qod:97, basis:'set-comparison',
    one:'Een meet-ID in het verkeer dat niet in de opgehaalde HTML staat.',
    run(e, root, doc){
      const ids = new Set();
      for (const r of e) for (const m of r.url.matchAll(/\b(G-[A-Z0-9]{6,}|UA-\d{4,}-\d+|GTM-[A-Z0-9]{4,})\b/g)) ids.add(m[1]);
      const rows = [...ids].map(id => ({host:'—', vendor:id, id: doc ? !doc.includes(id) : false,
        url: doc ? (doc.includes(id) ? 'staat ook in de HTML' : 'ONTBREEKT in de HTML: via een container geladen')
                 : 'geen HTML-document in deze HAR, niet te vergelijken'}));
      return {hit: rows.some(r=>r.id), rows,
        stats:{'gevonden ID\'s':ids.size,'niet in de HTML':rows.filter(r=>r.id).length},
        fals:[{ok:!!doc,t:doc?'getoetst':'niet toetsbaar',
          c:'Staat het ID dynamisch samengesteld in de HTML? Deze check zoekt de volledige string; een gesplitst ID zou gemist worden.'}]};
    }},
};

let har = null, ruleKey = 'frontrun';
const $ = s => document.querySelector(s);

$('#rules').innerHTML = Object.entries(RULES).map(([k,r]) =>
  `<button class="rule" data-k="${k}" aria-pressed="${k===ruleKey}">
     <b>${r.name}</b><span>${esc(r.one)}</span><em>QoD ${r.qod} · ${r.basis}</em></button>`).join('');
$('#rules').addEventListener('click', ev => {
  const b = ev.target.closest('.rule'); if (!b) return;
  ruleKey = b.dataset.k;
  document.querySelectorAll('.rule').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.k===ruleKey)));
  render();
});

const drop = $('#drop'), file = $('#file');
drop.onclick = () => file.click();
drop.onkeydown = e => { if (e.key==='Enter'||e.key===' ') { e.preventDefault(); file.click(); } };
drop.ondragover = e => { e.preventDefault(); drop.classList.add('over'); };
drop.ondragleave = () => drop.classList.remove('over');
drop.ondrop = e => { e.preventDefault(); drop.classList.remove('over'); load(e.dataTransfer.files[0]); };
file.onchange = e => load(e.target.files[0]);

function load(f) {
  if (!f) return;
  const rd = new FileReader();
  rd.onload = () => {
    try { har = JSON.parse(rd.result); } catch { alert('Dit is geen geldig HAR-bestand.'); return; }
    if (!har.log || !Array.isArray(har.log.entries)) { alert('Geen log.entries gevonden; dit lijkt geen HAR.'); return; }
    drop.querySelector('b').textContent = f.name;
    drop.querySelector('span').textContent = `${har.log.entries.length} verzoeken geladen · ${(f.size/1024).toFixed(0)} kB`;
    render();
  };
  rd.readAsText(f);
}

function parse() {
  const entries = har.log.entries.map(en => {
    let host = ''; try { host = new URL(en.request.url).hostname.replace(/^www\./,''); } catch {}
    const label = Object.keys(KNOWN).find(k => host.endsWith(k));
    const setc = (en.response.headers||[]).filter(h => /^set-cookie$/i.test(h.name));
    return { host, url: en.request.url, type: (en.response.content||{}).mimeType || '',
      vendor: label ? KNOWN[label] : null, id: ID_RE.test(en.request.url),
      cookies: setc.map(h => ({ name: (h.value.split('=')[0]||'').trim(), raw: h.value,
        expires: (/expires=([^;]+)/i.exec(h.value)||[])[1] })) };
  });
  // eerste HTML-document: het referentiepunt voor site-root en voor sideload
  const docEntry = har.log.entries.find(e => /text\/html/i.test((e.response.content||{}).mimeType||''));
  let root = '';
  try { root = reg(new URL((docEntry||har.log.entries[0]).request.url).hostname.replace(/^www\./,'')); } catch {}
  const docText = docEntry && docEntry.response.content ? (docEntry.response.content.text || '') : '';
  return { entries, root, docText };
}

function render() {
  if (!har) return;
  const { entries, root, docText } = parse();
  const rule = RULES[ruleKey];
  const res = rule.run(entries, root, docText);
  const out = $('#out'); out.classList.remove('hidden');
  out.innerHTML = `
  <div class="verdict ${res.hit?'hit':'no'}">
    <p class="vh">${res.hit ? rule.name + ' aangetroffen' : rule.name + ' niet aangetroffen'}</p>
    <p class="vm">doeldomein ${esc(root)} · regel ${esc(ruleKey)} v1 · QoD ${rule.qod} · grondslag ${rule.basis}</p>
    <div class="grid">${Object.entries(res.stats).map(([k,v]) =>
      `<div><span>${esc(k)}</span><b>${v}</b></div>`).join('')}</div>
    ${res.rows.length ? `<div class="tw"><table><thead><tr><th></th><th>Partij</th><th>Host</th><th>Bijzonderheid</th></tr></thead>
      <tbody>${res.rows.slice(0,60).map(r =>
        `<tr><td>${r.id?'<span class="idflag">ID</span>':''}</td><td class="v">${esc(r.vendor||'')}</td>
         <td>${esc(r.host)}</td><td class="u">${esc(r.url.slice(0,150))}</td></tr>`).join('')}</tbody></table></div>
      ${res.rows.length>60?`<p class="note">${res.rows.length-60} regels niet getoond.</p>`:''}` : ''}
    <h2 style="margin-top:24px">Wat dit zou ontkrachten</h2>
    <ul class="fal">${res.fals.map(f =>
      `<li><span class="t ${f.ok?'':'warn'}">${esc(f.t)}</span><span class="c">${esc(f.c)}</span></li>`).join('')}</ul>
    <p class="note">Een uitslag hier is de uitkomst van een regel op een opname. Of het record klopt,
    hangt ook af van de condities waaronder die opname is gemaakt: schoon profiel, geen interactie,
    en de locatie van waaruit is gemeten. Die staan in het record, niet in het bestand.</p>
  </div>`;
}
