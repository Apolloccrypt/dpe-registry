#!/usr/bin/env python3
"""Bouwt de catalogus: de fouten zelf, genummerd en uniek.

Een entry beschrijft een fouttype, zoals CWE een zwakteklasse beschrijft. Er
staat geen organisatie in, geen product en geen domein. Wie constateert dat een
systeem deze fout vertoont, publiceert dat zelf en verwijst naar het nummer.

Dat is niet alleen netter maar ook robuuster: een definitie veroudert niet als
een site wordt opgeschoond, en het register hoeft niemand aan te spreken.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "catalogue"
NOW = "2026-07-26T00:00:00Z"
ME = [{"name": "Mick Beer", "role": "proposed", "date": "2026-07-26"}]

# Wat een entry uitdrukkelijk niet doet. De eerste twee zijn de belangrijkste:
# de catalogus standaardiseert de bevinding, hij weegt hem niet. Dat is dezelfde
# scheiding als tussen CVE en NVD, en ze bestaat omdat een register dat geen
# oordeel velt ook niet op zijn oordeel aan te vallen is.
LIMITS = [
    "harm; the catalogue standardises a finding so it can be referred to, it does not weigh it",
    "severity; there is no score here, by design. Weighing belongs to whoever applies the entry to a concrete case",
    "unlawfulness; that is for a supervisory authority or a court",
    "intent; a fault is usually a build decision, not a plan",
    "absence: not finding it in one capture is not evidence that it is not there",
]

SLUGS = {'Tracking before consent': 'tracking-before-consent', 'Refusal without effect': 'refusal-without-effect', 'No refusal option': 'no-refusal-option', 'Maximum cookie lifetime': 'maximum-cookie-lifetime', 'Session recording': 'session-recording', 'User input to third parties': 'user-input-to-third-parties', 'Device fingerprinting': 'device-fingerprinting', 'Third-party hosted form': 'third-party-hosted-form', 'Third-party resource loading': 'third-party-resource-loading', 'Undisclosed recipient': 'undisclosed-recipient', 'Tag loaded outside the source': 'tag-loaded-outside-source', 'Device telemetry without function': 'device-telemetry-without-function', 'Bundled component collection': 'bundled-component-collection', 'No working off switch': 'no-working-off-switch'}

E = []


def entry(**kw):
    kw["schema_version"] = "2.0"
    kw.setdefault("applies_to", ["web"])
    kw.setdefault("status", "active")
    kw.setdefault("credit", ME)
    kw.setdefault("does_not_establish", LIMITS)
    kw.setdefault("changes", [{"at": NOW, "actor": "registry",
                               "entries": ["Entry created.", "Name assigned.",
                                           "Detection method and falsifiers defined.",
                                           "Legal provisions linked."]}])
    kw["slug"] = SLUGS[kw["name"]]
    kw["name_nl"] = kw.pop("name_nl")
    E.append(kw)


def repro(*tiers, scanners=()):
    """Alleen routes die daadwerkelijk bestaan.

    Een entry die verwijst naar een script dat er niet is, belooft iets wat het
    register niet waarmaakt, en dat is precies het verwijt dat we anderen maken.
    Ontbreekt alles, dan staat dat er zichtbaar bij in plaats van dat het wordt
    weggepoetst."""
    m = [{"tier": t[0], "path": t[1], **({"expect": t[2]} if len(t) > 2 else {})}
         for t in tiers if (ROOT / t[1]).exists()]
    if not m:
        m = [{"tier": "manual", "path": "METHOD.md",
              "expect": "no dedicated reproduction exists yet; follow the general method and the indicator above"}]
    return {"methods": m, "public_scanners": list(scanners)}


# ---------------------------------------------------------------- consent

entry(id="DPE-2026-0001", name="Tracking before consent", name_nl="Meten voor de toestemmingsvraag", family="consent",
      summary="A tag fires before the consent question has been answered.",
      mechanism={
          "what": "On page load, requests go to a measurement or advertising party at a moment when the visitor has not been able to make a choice. There may be a banner or there may not be; either way something was measured before anything was asked. An identifier is usually set at the same time, making the visitor recognisable on a later visit.",
          "why_it_matters": "Consent that arrives after the processing is not consent for that processing. Someone opening a page about an illness, a legal conflict or a benefit claim has already signalled that to a third party, and the option not to do so never existed.",
          "common_causes": ["tag hardcoded in the page rather than behind the consent gate",
                            "consent tool blocks cookie placement but not script or container loading",
                            "tag added through a dashboard by a team that does not know about the gate"],
          "not_this": "If the tag fires but refusing changes nothing, that is Refusal without effect: this entry is about the moment, that one about the effect of the choice. Both can be present at once and they are separate faults, because an operator can fix one and leave the other.",
      },
      detection={
          "indicator": "A request to a third-party host carrying an identifier parameter or setting an identifier cookie, timestamped before the consent event. Absent a consent event, the whole capture qualifies.",
          "method": "network-with-identifier", "qod": 95,
          "capture_requirements": ["clean profile; a warm one may carry earlier consent",
                                   "no interaction: nothing accepted, refused or dismissed",
                                   "record the country the capture egressed from; consent flows are often geo-targeted"],
          "attribution": ["har-pageref", "cdp-initiator"]},
      falsifiers=[
          {"condition": "The measurement host is a first-party CNAME to the target domain.",
           "checkable": "manual", "if_true": "reclassify",
           "note": "Still an exposure, but not third-party by host. Needs DNS resolution at capture time."},
          {"condition": "The request carries no identifier and sets no cookie.",
           "checkable": "automated", "if_true": "weaken",
           "note": "There is traffic, but the inference about personal data is weaker."},
          {"condition": "Consent was granted in an earlier session on the same profile.",
           "checkable": "automated", "if_true": "drop"},
          {"condition": "The tag only fired because the capture clicked something.",
           "checkable": "automated", "if_true": "drop"}],
      reproduction=repro(("manual", "repro/frontrun/MANUAL.md", "measurement requests visible before touching the banner"),
                         ("bookmarklet", "repro/bookmarklet/frontrun.bookmarklet.txt"),
                         ("script", "repro/frontrun/frontrun.mjs", "at least one request to a measurement host before interaction, plus an identifier cookie"),
                         scanners=("urlscan.io", "webbkoll", "blacklight")),
      legal={"provisions": ["nl-tw-11-7a", "eu-gdpr-6-1-a"], "caselaw": ["cjeu-planet49"],
             "rebuttals": [
                 {"objection": "Analytics falls under the strictly-necessary exemption.",
                  "answer": "The exemption covers what is necessary for a service the user asked for. Audience measurement is necessary for the operator, not for the visitor. Where the analytics party also uses the data for its own purposes, the argument fails entirely."},
                 {"objection": "The servers are in the EU.",
                  "answer": "That answers a different question. This fault is about the moment, not the destination. An entry can be present with the recipient squarely inside the EEA."},
                 {"objection": "It was one oversight, since fixed.",
                  "answer": "Testable. Archived source shows how long the tag was there. An unbroken run of years is not an oversight, and it cannot be repaired retroactively."},
                 {"objection": "Our consent tool handles this.",
                  "answer": "Measure it rather than assume it. A tool that blocks cookie placement may leave container loading untouched."}]},
      related=["DPE-2026-0002", "DPE-2026-0003", "DPE-2026-0005"],
      seen_in_the_wild={"confirmed": True, "first_documented": "2026-05-27"})

entry(id="DPE-2026-0002", name="Refusal without effect", name_nl="Weigeren zonder effect", family="consent",
      summary="Refusing consent does not change what leaves the browser.",
      mechanism={
          "what": "The site asks for consent and registers the refusal, but the tags that the refusal should stop do not sit behind the gate. The screen confirms the choice; the wire shows the same traffic as before.",
          "why_it_matters": "A refusal that changes nothing makes the right to withhold and to withdraw consent a formality. The visitor believes they have decided something and they have not.",
          "common_causes": ["tags hardcoded rather than gated",
                            "consent tool blocks cookies but not the loading of scripts or containers",
                            "banner is informational and wired to nothing"],
          "not_this": "If nothing was asked before the tag fired, that is Tracking before consent. If no refusal option is offered at all, that is No refusal option.",
      },
      detection={
          "indicator": "Set comparison: the third-party hosts contacted after an explicitly registered refusal are equal to, or a superset of, those contacted without any interaction. There is no third reading.",
          "method": "differential", "qod": 97,
          "capture_requirements": ["two separate captures, each with a fresh profile",
                                   "read the consent state back after clicking refuse; an unregistered click measures a failed click, not a hollow refusal",
                                   "identical conditions otherwise: same page, same window, same country"],
          "attribution": ["har-pageref", "cdp-initiator"]},
      falsifiers=[
          {"condition": "The refusal was not registered.", "checkable": "automated", "if_true": "drop",
           "note": "The most important one: it turns a finding into a measurement error."},
          {"condition": "The banner does block, but later than the capture window.",
           "checkable": "automated", "if_true": "drop"},
          {"condition": "The surviving requests are strictly necessary for a service the visitor asked for.",
           "checkable": "not-from-capture", "if_true": "reclassify",
           "note": "A judgement per host. Never excluded automatically; an entry may be cited with this untested as long as that is stated."}],
      reproduction=repro(("manual", "repro/hollowno/MANUAL.md", "identical host sets in the no-action and refuse captures"),
                         ("script", "repro/hollowno/hollowno.mjs"),
                         scanners=("urlscan.io", "webbkoll")),
      legal={"provisions": ["eu-gdpr-6-1-a", "nl-tw-11-7a"], "caselaw": ["cjeu-planet49"],
             "rebuttals": [
                 {"objection": "The banner is there, so the visitor has a choice.",
                  "answer": "The choice exists on screen and not on the wire. Consent requires an active act of the user; an act without effect is not such an act."},
                 {"objection": "This is analytics, which needs no consent.",
                  "answer": "Then the banner should not have listed it, and there would be no refusal to honour. A party cannot both treat something as consent-bound and ignore the refusal."}]},
      related=["DPE-2026-0001", "DPE-2026-0004"],
      seen_in_the_wild={"confirmed": True, "first_documented": "2026-05-27"})

entry(id="DPE-2026-0003", name="No refusal option", name_nl="Geen weigeroptie", family="consent",
      summary="The consent dialogue offers acceptance and no way to refuse.",
      mechanism={
          "what": "The banner presents an accept control, and refusing requires either leaving the site or navigating a path that does not lead to a working refusal.",
          "why_it_matters": "A choice with one option is not a choice. Consent must be freely given, and it is not free if the only way out is to leave.",
          "common_causes": ["banner template with a single call to action",
                            "refusal hidden behind a settings layer that does not save",
                            "closing the banner counted as acceptance"],
          "not_this": "If a refusal option exists but does nothing, that is Refusal without effect. Here the option is absent.",
      },
      detection={
          "indicator": "No refusal affordance in the banner DOM: no control whose action registers a negative consent state, at any layer reachable from the first screen.",
          "method": "static-source", "qod": 60,
          "capture_requirements": ["inspect every layer of the dialogue, not only the first screen",
                                   "dismissing by clicking away is not a refusal; check what state it writes"],
          "attribution": ["cdp-initiator"]},
      falsifiers=[
          {"condition": "A refusal exists on a second layer of the dialogue.",
           "checkable": "manual", "if_true": "drop"},
          {"condition": "The site sets no consent-bound technology at all, so no refusal is required.",
           "checkable": "automated", "if_true": "drop"}],
      reproduction=repro(("manual", "repro/onedoor/MANUAL.md", "no control in the dialogue that writes a negative consent state"),
                         scanners=("urlscan.io",)),
      legal={"provisions": ["eu-gdpr-6-1-a"], "caselaw": ["cjeu-planet49"],
             "rebuttals": [{"objection": "Visitors can refuse in their browser settings.",
                            "answer": "Consent is sought by the controller and must be refusable where it is sought. Delegating that to the browser does not discharge it."}]},
      related=["DPE-2026-0002"], seen_in_the_wild={"confirmed": True})

entry(id="DPE-2026-0004", name="Maximum cookie lifetime", name_nl="Maximale bewaartermijn", family="retention",
      summary="An identifier cookie is set for the maximum lifetime a browser accepts, before the question is answered.",
      mechanism={
          "what": "At page load, before any consent interaction, a cookie is placed with a lifetime at or near the ceiling the browser permits, currently 399 days in Chromium-based browsers.",
          "why_it_matters": "The visitor is recognisable for over a year on the basis of a decision they were never given. Storage limitation requires a term tied to the purpose, not to the technical maximum.",
          "common_causes": ["default retention of the measurement setup left untouched",
                            "cookie placed outside the consent gate, so the term was never considered"],
          "not_this": "If the cookie is set only after consent, this is a retention question and not this entry. The pre-consent placement is what makes it a fault here.",
      },
      detection={
          "indicator": "A Set-Cookie with max-age at or above 34128000 seconds (399 days), or an equivalent Expires, issued before the consent event.",
          "method": "network-with-identifier", "qod": 95,
          "capture_requirements": ["clean profile", "no interaction", "read Set-Cookie headers, not only the cookie jar"],
          "attribution": ["har-pageref"]},
      falsifiers=[
          {"condition": "The cookie is strictly necessary for a service the visitor requested.",
           "checkable": "manual", "if_true": "drop"},
          {"condition": "The lifetime is set by the browser, not by the server.",
           "checkable": "automated", "if_true": "drop"}],
      reproduction=repro(("manual", "repro/maxstay/MANUAL.md", "a cookie with a lifetime near 399 days, present before any interaction"),
                         ("bookmarklet", "repro/bookmarklet/frontrun.bookmarklet.txt"),
                         ("script", "repro/maxstay/maxstay.mjs"),
                         scanners=("urlscan.io", "webbkoll")),
      legal={"provisions": ["nl-tw-11-7a", "eu-gdpr-6-1-a"], "caselaw": ["cjeu-planet49"],
             "rebuttals": [{"objection": "399 days is the industry default.",
                            "answer": "A default is not a purpose. Storage limitation asks what term the purpose requires, and the browser ceiling is not an answer to that question."}]},
      related=["DPE-2026-0001"], seen_in_the_wild={"confirmed": True})

# ---------------------------------------------------------------- data

entry(id="DPE-2026-0005", name="Session recording", name_nl="Sessieopname", family="data",
      summary="The session itself is recorded, not merely the page view.",
      mechanism={
          "what": "A session-recording script captures behaviour inside the page: mouse movement, scrolling, clicks and often keystrokes in form fields, replayable afterwards as a film of the visit.",
          "why_it_matters": "This is a different order of collection from counting page views. What someone typed and then deleted, where they hesitated, which field they returned to: none of that is needed to run a website, and all of it is revealing.",
          "common_causes": ["recording script loaded outside the consent gate",
                            "field masking left off, so entered text is captured too"],
          "not_this": "Ordinary page-view analytics is not this entry. The distinguishing feature is capture of in-page behaviour.",
      },
      detection={
          "indicator": "A request to a session-recording endpoint of a recording vendor, carrying a site identifier, at page load.",
          "method": "network-with-identifier", "qod": 95,
          "capture_requirements": ["clean profile", "no interaction",
                                   "note whether field masking is active; unmasked input raises the stakes considerably"],
          "attribution": ["har-pageref", "cdp-initiator"]},
      falsifiers=[
          {"condition": "The vendor processes only aggregated data without session capture.",
           "checkable": "manual", "if_true": "drop"},
          {"condition": "Recording starts only after consent is granted.",
           "checkable": "automated", "if_true": "drop"},
          {"condition": "All input fields are masked at source.",
           "checkable": "manual", "if_true": "weaken"}],
      reproduction=repro(("manual", "repro/overshoulder/MANUAL.md", "a request to a recording vendor endpoint before consent"),
                         ("script", "repro/overshoulder/overshoulder.mjs"),
                         scanners=("blacklight", "urlscan.io")),
      legal={"provisions": ["eu-gdpr-6-1-a", "nl-tw-11-7a"],
             "rebuttals": [{"objection": "The recording servers are in the EU.",
                            "answer": "Where the recording is stored says nothing about whether it should have been made. Location is a separate question from lawfulness of collection."}]},
      seen_in_the_wild={"confirmed": True})

entry(id="DPE-2026-0006", name="User input to third parties", name_nl="Invoer naar derden", family="data",
      summary="What the visitor typed or looked for reaches a third party.",
      mechanism={
          "what": "A search term, form field or URL path that reveals intent is passed to an analytics or advertising party, usually as a parameter or as part of a page title.",
          "why_it_matters": "The content of a query says far more than the fact of a visit. A search on a health site, a benefits portal or a legal service is close to a statement about the person, and it leaves in plain text.",
          "common_causes": ["query string included in the page URL that analytics reports verbatim",
                            "form values passed into event parameters",
                            "page titles constructed from user input"],
          "not_this": "An identifier alone is not this entry; that is ordinary tracking. What matters here is that the content itself travels.",
      },
      detection={
          "indicator": "A value entered or searched by the visitor appears verbatim, or trivially encoded, in a request to a host under a different registrable domain.",
          "method": "network-observed", "qod": 90,
          "capture_requirements": ["use a distinctive search term so it can be found unambiguously in the capture",
                                   "check both query parameters and POST bodies"],
          "attribution": ["har-pageref"]},
      falsifiers=[
          {"condition": "The value is hashed or truncated beyond recovery before leaving.",
           "checkable": "manual", "if_true": "weaken"},
          {"condition": "The receiving host is a processor under a documented agreement, self-hosted.",
           "checkable": "not-from-capture", "if_true": "reclassify"}],
      reproduction=repro(("manual", "repro/telltale/MANUAL.md", "the distinctive search term visible in an outbound request"),
                         scanners=("urlscan.io",)),
      legal={"provisions": ["eu-gdpr-6-1-a"],
             "rebuttals": [{"objection": "We do not send personal data, only the page URL.",
                            "answer": "If the URL contains what the visitor typed, then the URL is the personal data. The container does not change the content."}]},
      seen_in_the_wild={"confirmed": True})

entry(id="DPE-2026-0007", name="Device fingerprinting", name_nl="Apparaatherkenning", family="data",
      summary="The device is recognised by its characteristics, without any stored identifier.",
      mechanism={
          "what": "Scripts read properties that together make a device distinctive: time zone, screen metrics, fonts, canvas or WebGL rendering, enumerated navigator fields. No cookie is stored, so cookie controls do not touch it.",
          "why_it_matters": "Recognition without storage escapes exactly the controls people are told to use. Clearing cookies and refusing consent leave the technique untouched.",
          "common_causes": ["anti-fraud or bot-detection library that also serves marketing",
                            "advertising script with built-in fingerprinting"],
          "not_this": "Reading a time zone to localise a page is not this entry. The distinguishing feature is enumeration of multiple properties by a third party.",
      },
      detection={
          "indicator": "Calls to canvas, WebGL, font enumeration, time zone or navigator property enumeration originating from a script under a different registrable domain, before consent.",
          "method": "network-observed", "qod": 90,
          "capture_requirements": ["hook the property reads through the debugging protocol; a HAR alone does not show them",
                                   "record which script initiated each read"],
          "attribution": ["cdp-initiator"]},
      falsifiers=[
          {"condition": "The properties are read by a first-party script, not a third party.",
           "checkable": "automated", "if_true": "reclassify"},
          {"condition": "The reads serve a functional purpose such as localisation or accessibility.",
           "checkable": "not-from-capture", "if_true": "weaken",
           "note": "Purpose cannot be established from a capture. The entry establishes the reading, not the intent."}],
      reproduction=repro(("manual", "repro/silhouette/MANUAL.md", "property reads by third-party scripts before consent"),
                         ("script", "repro/silhouette/silhouette.mjs"),
                         scanners=("blacklight",)),
      legal={"provisions": ["nl-tw-11-7a", "eu-gdpr-6-1-a"],
             "rebuttals": [{"objection": "We set no cookies.",
                            "answer": "The cookie provision covers storing and reading information on the device, not only cookies. Reading device characteristics for recognition is within its scope."}]},
      seen_in_the_wild={"confirmed": True})

# ---------------------------------------------------------------- chain

entry(id="DPE-2026-0008", name="Third-party hosted form", name_nl="Formulier bij een derde", family="chain",
      summary="A form that looks like part of the site is hosted by a third party that profiles on its own account.",
      mechanism={
          "what": "A signup, contact or newsletter form lives on a domain belonging to a marketing platform. The visitor believes they are dealing with the site; the platform sets its own identifiers and builds its own record.",
          "why_it_matters": "The visitor cannot see who they are actually handing data to. Interest categories ticked on such a form become a profile at a party the person never chose.",
          "common_causes": ["marketing platform hosting the form on a vendor subdomain",
                            "embedded form in an iframe from another registrable domain"],
          "not_this": "A processor hosting a form under the controller's own domain and instructions is not this entry.",
      },
      detection={
          "indicator": "Set-Cookie from a host under a different registrable domain than the site that linked to the form, at page load and before any submission.",
          "method": "network-with-identifier", "qod": 95,
          "capture_requirements": ["never submit the form; establish the fields, not the processing after sending",
                                   "record the fields offered, since that shows what profile would be built"],
          "attribution": ["har-pageref"]},
      falsifiers=[
          {"condition": "The cookies are strictly necessary to operate the form.",
           "checkable": "not-from-capture", "if_true": "weaken"},
          {"condition": "The form domain is a CNAME under the controller's own domain, operated as a processor.",
           "checkable": "manual", "if_true": "reclassify"}],
      reproduction=repro(("manual", "repro/handover/MANUAL.md", "cookies set by the form host at load, without a consent layer"),
                         ("script", "repro/handover/handover.mjs"),
                         scanners=("urlscan.io", "webbkoll")),
      legal={"provisions": ["eu-gdpr-44", "eu-gdpr-6-1-a"], "caselaw": ["cjeu-fashion-id"],
             "rebuttals": [{"objection": "That is our supplier's platform, not our site.",
                            "answer": "Fashion ID holds that a controller who arranges for visitor data to reach a third party is jointly responsible for that collection and transmission. Linking to the form is arranging it."}]},
      related=["DPE-2026-0009"], seen_in_the_wild={"confirmed": True})

entry(id="DPE-2026-0009", name="Third-party resource loading", name_nl="Externe bron inladen", family="transfer",
      summary="A resource loaded straight from a third party makes every page view a transfer.",
      mechanism={
          "what": "A font, script library or image is loaded directly from an external provider instead of being served by the site. Each page view sends the visitor's IP address, and often more, to that provider.",
          "why_it_matters": "It needs no consent interaction to establish and no tracking intent to occur. It happens on the first byte, to every visitor, including those who refuse everything.",
          "common_causes": ["CDN link copied from documentation",
                            "theme or template that references external fonts by default"],
          "not_this": "This entry is about the mechanism of loading, not about the destination country. Where the data goes is a separate axis; a hotlink within the EEA is still a hotlink.",
      },
      detection={
          "indicator": "A subresource request to a host under a different registrable domain, present in the initial document, issued without any interaction.",
          "method": "network-observed", "qod": 90,
          "capture_requirements": ["capture from a clean profile with no interaction",
                                   "establish the destination separately; do not infer it from the vendor's headquarters"],
          "attribution": ["har-pageref"]},
      falsifiers=[
          {"condition": "The resource is served locally through a proxy or self-hosted copy.",
           "checkable": "automated", "if_true": "drop"},
          {"condition": "The request carries no data capable of identifying the visitor.",
           "checkable": "manual", "if_true": "weaken",
           "note": "An IP address reaches the provider in any case; that is the core of the German Google Fonts ruling."}],
      reproduction=repro(("manual", "repro/hotlink/MANUAL.md", "a request to an external provider at page load, with no interaction"),
                         ("bookmarklet", "repro/bookmarklet/frontrun.bookmarklet.txt"),
                         ("script", "repro/hotlink/hotlink.mjs"),
                         scanners=("urlscan.io", "webbkoll", "webpagetest")),
      legal={"provisions": ["eu-gdpr-44", "eu-gdpr-6-1-a"],
             "caselaw": ["lg-muenchen-google-fonts", "cjeu-fashion-id"],
             "rebuttals": [
                 {"objection": "An IP address is not personal data here.",
                  "answer": "The Munich ruling on Google Fonts treats hotlinking a provider resource as a transfer of personal data, precisely because the IP reaches the provider."},
                 {"objection": "Our hosting is in the Netherlands.",
                  "answer": "Storage location and loaded components are different things. The transfer runs through what the page pulls in, not through where it is stored."}]},
      related=["DPE-2026-0008"], seen_in_the_wild={"confirmed": True})

# ------------------------------------------------------- transparency, method

entry(id="DPE-2026-0010", name="Undisclosed recipient", name_nl="Niet-vermelde ontvanger", family="transparency",
      summary="A recipient of personal data is missing from the party's own privacy statement.",
      mechanism={
          "what": "Measurement shows data going to a party that the published privacy statement does not mention, or the statement asserts something the traffic contradicts, such as that no personal data is processed or that all recipients are inside the EEA.",
          "why_it_matters": "The statement is the one place a person can check what happens to their data. If it is wrong, informed consent is impossible by construction, and every other control rests on nothing.",
          "common_causes": ["statement not updated when the measurement setup changed",
                            "tags added by a team that does not maintain the statement"],
          "not_this": "This is not about whether the processing was lawful. It is about the gap between the measurement and the party's own account of it.",
      },
      detection={
          "indicator": "Set difference: recipients observed in the capture minus recipients named in the privacy statement of the same date is non-empty. Both sources belong to the party; the researcher only does the arithmetic.",
          "method": "document-comparison", "qod": 97,
          "capture_requirements": ["use the statement as it stood on the measurement date, from an archive",
                                   "search the whole statement and any cookie overview, not just the recipients list"],
          "attribution": ["document-diff", "har-pageref"]},
      falsifiers=[
          {"condition": "The recipient is named elsewhere in the statement or in a linked cookie overview.",
           "checkable": "manual", "if_true": "drop"},
          {"condition": "The statement was updated outside the measured window.",
           "checkable": "manual", "if_true": "drop"}],
      reproduction=repro(("manual", "repro/offbooks/MANUAL.md", "a recipient present in the capture and absent from the statement of the same date"),
                         scanners=("wayback", "urlscan.io")),
      legal={"provisions": ["eu-gdpr-6-1-a"],
             "rebuttals": [{"objection": "The statement is generic on purpose.",
                            "answer": "Article 13 requires the recipients or categories of recipients. A statement that omits a category entirely is not generic but incomplete."}]},
      seen_in_the_wild={"confirmed": True})

entry(id="DPE-2026-0011", name="Tag loaded outside the source", name_nl="Tag buiten de broncode", family="method",
      summary="Tags fire from a container while appearing nowhere in the page source.",
      mechanism={
          "what": "A tag manager loads measurement or advertising tags at runtime. The identifiers of those tags are not in the delivered HTML, so reading the source suggests they are gone while the traffic shows otherwise.",
          "why_it_matters": "Mostly a methodological trap rather than a harm in itself, and that is why it is catalogued. A researcher who checks only the source concludes that tracking stopped when it did not. It also means the operator can change what runs without any change to the site.",
          "common_causes": ["tags migrated from hardcoded to container-managed",
                            "marketing team with dashboard access and no deployment"],
          "not_this": "Not every container is this entry. It applies when a tag observed in traffic cannot be found in the delivered source.",
      },
      detection={
          "indicator": "A property or measurement identifier present in network traffic and absent from the fetched HTML document. A set comparison, not an observation.",
          "method": "differential", "qod": 97,
          "capture_requirements": ["fetch and retain the HTML document in the same capture",
                                   "search for the full identifier and for split forms; dynamic assembly would otherwise be missed"],
          "attribution": ["cdp-initiator", "har-pageref"]},
      falsifiers=[
          {"condition": "The identifier is present in the source but assembled dynamically.",
           "checkable": "automated", "if_true": "drop"},
          {"condition": "The initiator is another script rather than the container.",
           "checkable": "automated", "if_true": "reclassify"}],
      reproduction=repro(("manual", "repro/sideload/MANUAL.md", "a measurement identifier in traffic that is absent from the HTML"),
                         ("script", "repro/sideload/sideload.mjs"),
                         scanners=("urlscan.io",)),
      legal={"provisions": ["eu-gdpr-6-1-a"],
             "rebuttals": [{"objection": "We removed the tracking; it is not in our code.",
                            "answer": "Absence from the source is not absence from the traffic. The container is the reliable indicator, and its version history shows what ran when."}]},
      related=["DPE-2026-0001"], seen_in_the_wild={"confirmed": True})


# ------------------------------------------- apparaten, firmware, apps
# Hier zit het gat dat CVE niet dekt. Een router die telemetrie naar een derde
# land stuurt is niet te exploiteren; hij doet wat de bouwer wilde. Precies
# daarom bestaat er geen nummer voor, en precies daarom hoort het hier.

entry(id="DPE-2026-0012", name="Device telemetry without function", name_nl="Apparaat belt naar huis", family="telemetry",
      applies_to=["firmware", "iot", "network-device", "vehicle"],
      summary="A device contacts a server abroad without any function that requires it.",
      not_a_vulnerability="Nothing is exploitable and nothing is broken. The device does what its builder intended, and the objection is to that intention. A vulnerability register has no place to put this, which is why it has gone unrecorded.",
      mechanism={
          "what": "Firmware opens connections to hosts that serve no function the owner asked for: a fixed endpoint contacted at boot, at intervals, or on every state change. The payload may be status, configuration, usage patterns or an identifier of the device or its owner.",
          "why_it_matters": "The owner bought a device, not a subscription to being observed. Unlike a website there is no browser to inspect it with, no consent dialogue, and often no way to switch it off without breaking the product. The traffic continues for the life of the device, which for a router or a car is a decade.",
          "common_causes": ["vendor telemetry enabled by default with no setting to disable it",
                            "chipset SDK contacting the chip maker rather than the device brand",
                            "update or time service pointed at a fixed host in the vendor's home jurisdiction"],
          "not_this": "A firmware update check against the vendor is expected behaviour and not this entry. What distinguishes it is traffic without a function the owner asked for, or a destination that has nothing to do with the product."},
      detection={
          "indicator": "Outbound connections from the device to hosts that persist when every user-facing function is idle, established from a network capture at the gateway rather than from the device itself.",
          "method": "network-observed", "qod": 90,
          "capture_requirements": [
              "capture upstream of the device, on the router or an inline tap; the device cannot be trusted to report its own traffic",
              "idle baseline first: leave the device untouched and record what it does anyway",
              "record firmware version and region setting; behaviour frequently differs per region",
              "establish the destination by address and routing, never by where the vendor is headquartered"],
          "attribution": ["process-trace", "vendor-statement"]},
      falsifiers=[
          {"condition": "The traffic serves a function the owner enabled, such as remote access or cloud backup.",
           "checkable": "manual", "if_true": "drop"},
          {"condition": "The endpoint is a content delivery network fronting a service in another jurisdiction.",
           "checkable": "manual", "if_true": "reclassify",
           "note": "Where an operator is based says nothing about where the data goes. Establish the destination, not the origin of the company."},
          {"condition": "The connection carries no data beyond what is needed to check for updates.",
           "checkable": "manual", "if_true": "weaken"},
          {"condition": "The behaviour can be switched off in the interface and was left on.",
           "checkable": "manual", "if_true": "weaken",
           "note": "Still relevant if it is on by default, but it changes the finding from cannot to did not."}],
      reproduction={"methods": [
          {"tier": "manual", "path": "repro/homecall/MANUAL.md",
           "expect": "connections to hosts unrelated to any function the owner enabled, while the device sits idle"},
          {"tier": "script", "path": "repro/homecall/idle-baseline.sh",
           "expect": "a list of destinations contacted during an idle window, with volumes and intervals"}],
          "public_scanners": []},
      legal={"provisions": ["eu-gdpr-44", "eu-gdpr-6-1-a"],
             "rebuttals": [
                 {"objection": "This is anonymous diagnostic data.",
                  "answer": "A device identifier tied to a household is not anonymous, and diagnostics that report usage patterns describe the people using it. Establish what is in the payload before accepting the label."},
                 {"objection": "It is in the terms and conditions.",
                  "answer": "Consent must be specific and freely given. A term buried in a document accepted once at setup, with no way to refuse and keep the product working, is neither."},
                 {"objection": "The servers belong to our chip supplier, not to us.",
                  "answer": "The party placing the product on the market chose that component. Responsibility for what a shipped device does is not transferred by subcontracting it."}]},
      related=["DPE-2026-0013"], seen_in_the_wild={"confirmed": True})

entry(id="DPE-2026-0013", name="Bundled component collection", name_nl="Meeliftende component", family="telemetry",
      applies_to=["mobile-app", "desktop", "firmware"],
      summary="A bundled component collects on its own account, alongside the function the app performs.",
      not_a_vulnerability="The component works exactly as documented by its maker. There is no flaw to fix, only a decision to include it, and vulnerability registers have nowhere to record a decision.",
      mechanism={
          "what": "An application ships a third-party library that, beyond the service it provides to the app, gathers device identifiers, installed applications, location or contacts and sends them to its own infrastructure. The developer may not have read what it does.",
          "why_it_matters": "The user chose the app, not the passenger. The collection continues in the background, is invisible in the interface, and often reaches parties that trade in the data rather than use it.",
          "common_causes": ["analytics or advertising SDK with collection enabled by default",
                            "monetisation library added for revenue rather than function",
                            "component inherited from a framework or a white-label build"],
          "not_this": "A processor library operating strictly on the developer's instructions is not this entry. The distinguishing feature is collection on the component's own account."},
      detection={
          "indicator": "Outbound requests from the application to hosts of a bundled component, carrying device or user identifiers, at moments unrelated to any user action in that app.",
          "method": "network-with-identifier", "qod": 95,
          "capture_requirements": [
              "intercept on the device with a trusted proxy; certificate pinning may need addressing and that fact belongs in the write-up",
              "start from a fresh install and record what happens before the first screen is dismissed",
              "list the bundled components statically as well, so traffic can be matched to a component"],
          "attribution": ["process-trace", "har-pageref"]},
      falsifiers=[
          {"condition": "The traffic serves the function the user invoked.",
           "checkable": "manual", "if_true": "drop"},
          {"condition": "The identifiers are resettable and not tied to the device permanently.",
           "checkable": "manual", "if_true": "weaken"},
          {"condition": "The component is configured to collect nothing and the traffic is a heartbeat only.",
           "checkable": "manual", "if_true": "weaken"}],
      reproduction={"methods": [
          {"tier": "manual", "path": "repro/sidecar/MANUAL.md",
           "expect": "requests to component hosts carrying identifiers, before any user action"},
          {"tier": "script", "path": "repro/sidecar/inventory.sh",
           "expect": "a list of bundled components with the hosts each contacts"}],
          "public_scanners": []},
      legal={"provisions": ["eu-gdpr-6-1-a", "eu-gdpr-44"], "caselaw": ["cjeu-fashion-id"],
             "rebuttals": [
                 {"objection": "The SDK is the supplier's responsibility.",
                  "answer": "The developer decided to ship it. Fashion ID holds that arranging for data to reach a third party makes you jointly responsible for that reaching."},
                 {"objection": "We only use it for crash reporting.",
                  "answer": "Then the traffic should be limited to crashes. Establish what the payload contains when nothing has crashed."}]},
      related=["DPE-2026-0012", "DPE-2026-0008"], seen_in_the_wild={"confirmed": True})

entry(id="DPE-2026-0014", name="No working off switch", name_nl="Geen werkende uitschakeling", family="consent",
      applies_to=["firmware", "iot", "vehicle", "mobile-app"],
      summary="The setting that would stop the collection does not exist, or does not survive.",
      not_a_vulnerability="Nothing is broken from the builder's point of view. The absence of an off switch is a product decision, and there is no security register that records product decisions.",
      mechanism={
          "what": "A device or application collects data with no control to prevent it, or with a control that resets on update, on reboot or after a period, so the collection resumes without the owner doing anything.",
          "why_it_matters": "Consent that cannot be withdrawn is not consent. On a device this bites harder than on a website, because the owner cannot walk away from something they paid for and installed in their home or their car.",
          "common_causes": ["setting absent from the interface entirely",
                            "preference stored in volatile configuration and lost on firmware update",
                            "regional default reapplied after an update"],
          "not_this": "If a control exists and holds, this entry does not apply, however buried the control is. The distinguishing feature is that it is missing or does not survive."},
      detection={
          "indicator": "Collection continues after the control is set to off, or the control returns to on after a reboot or update, established by capturing before and after.",
          "method": "differential", "qod": 97,
          "capture_requirements": [
              "capture with the control on, then off, then again after a reboot and after an update",
              "record the firmware version at each step; a reset on update is a different finding from a reset on reboot"],
          "attribution": ["process-trace"]},
      falsifiers=[
          {"condition": "The control exists elsewhere, for instance in a companion app or a web interface.",
           "checkable": "manual", "if_true": "drop"},
          {"condition": "The remaining traffic is strictly necessary to operate the device.",
           "checkable": "manual", "if_true": "reclassify"},
          {"condition": "The reset was caused by a factory reset performed during testing.",
           "checkable": "manual", "if_true": "drop"}],
      reproduction={"methods": [
          {"tier": "manual", "path": "repro/deadend/MANUAL.md",
           "expect": "identical outbound traffic with the control on and off, or the control reverting after a reboot"}],
          "public_scanners": []},
      legal={"provisions": ["eu-gdpr-6-1-a"],
             "rebuttals": [{"objection": "The device cannot function without it.",
                            "answer": "Then say so, and establish it. Necessity is a claim that can be tested by disabling the traffic and seeing what stops working."}]},
      related=["DPE-2026-0002", "DPE-2026-0003", "DPE-2026-0012"], seen_in_the_wild={"confirmed": True})


def main():
    # Koppeling naar DPIA, inkoop en klacht staat apart, omdat het per entry
    # geschreven is en niet af te leiden valt uit de definitie.
    prac = json.loads((ROOT / "tools" / "in_practice.json").read_text(encoding="utf-8"))
    # Een gedeeld script voor alle webfouten, in plaats van tien losse. Wie
    # meet wil een run doen en alles tegelijk toetsen, niet tien keer hetzelfde.
    WEB = {"DPE-2026-0001", "DPE-2026-0002", "DPE-2026-0003", "DPE-2026-0004",
           "DPE-2026-0005", "DPE-2026-0007", "DPE-2026-0009", "DPE-2026-0011"}
    for x in E:
        if x["id"] in prac:
            x["in_practice"] = prac[x["id"]]
        if x["id"] in WEB:
            x["reproduction"]["methods"].insert(1, {
                "tier": "script", "path": "repro/web/check.mjs",
                "expect": f'the run reports {x["id"]} as present, with the detail behind it'})
    # Laatste zeef: welke route ook is opgegeven, alleen wat bestaat blijft
    # staan. Een verwijzing naar een script dat er niet is, is een belofte die
    # het register niet waarmaakt.
    for x in E:
        live = [m for m in x["reproduction"]["methods"] if (ROOT / m["path"]).exists()]
        x["reproduction"]["methods"] = live or [{
            "tier": "manual", "path": "METHOD.md",
            "expect": "no dedicated reproduction exists yet; follow the general method and the indicator above"}]
    OUT.mkdir(parents=True, exist_ok=True)
    # Alleen de eigen entries opruimen. Deze generator is niet de enige bron:
    # bijdragen van anderen staan als losse bestanden in dezelfde map en die
    # mogen door een build niet verdwijnen.
    mine = {x["id"] for x in E}
    for f in OUT.glob("DPE-*.json"):
        if f.stem in mine:
            f.unlink()
    for e in E:
        (OUT / (e["id"] + ".json")).write_text(
            json.dumps(e, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fam = {}
    for e in E:
        fam[e["family"]] = fam.get(e["family"], 0) + 1
    print(f"{len(E)} fouten in de catalogus")
    print("families: " + ", ".join(f"{k}={v}" for k, v in sorted(fam.items())))
    print("namen:    " + ", ".join(e["name"] for e in E))


if __name__ == "__main__":
    main()
