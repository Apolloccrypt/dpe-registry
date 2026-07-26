# DPE · Data Protection Exposures

A catalogue of numbered faults in how systems handle personal data.

Researchers keep finding the same things, and those things have no name. So every
publication starts from nothing: the same explanation, the same legal grounding,
the same objections answered again. With a number, that happens once.

```
  DPE-2026-0001   Tracking before consent
                  A tag fires before the consent question has been answered.
```

## What this is for

**Not vulnerabilities.** There is nothing to exploit. The system does what its
builder intended, and that intention is the objection. A router phoning home to
another country gets no CVE because nothing is broken, and until now there was no
number to cite for it either. That gap is why this exists.

**Not accusations.** No company, product or domain appears in this catalogue.
Whoever establishes that a system exhibits one of these faults publishes that
themselves, under their own name, and cites the number. That keeps definitions
usable long after any individual site has been cleaned up.

**No severity.** No score, no judgement of harm, by design. CVE does not weigh
either; NVD does that, separately. How heavily a concrete case weighs depends on
that case, and belongs to whoever applies the entry.

## What is in an entry

| | |
|---|---|
| Mechanism | how the fault arises, and the fault it is most often confused with |
| Indicator | the concrete thing that settles it, checkable without interpretation |
| Detection quality | which method establishes it and how strongly, on a fixed scale |
| Falsifiers | what would refute it, and whether that can be checked from a capture |
| Reproduction | by hand, bookmarklet, script; never requiring tooling we own |
| Legal framing | provisions per jurisdiction, case law, and the standard objections answered |
| In practice | what to verify in a DPIA, how to word a procurement clause, what to hand a regulator |

Each entry lives at its own permanent address with the same content as JSON
beside it. Identifiers are never reused; a deprecated entry keeps its number and
its address, with the reason attached, because references to it exist elsewhere.

## The method is published too

[METHOD.md](METHOD.md) sets out how to go looking for these faults: define scope
before measuring, capture clean, take a baseline, vary one thing at a time, walk
the catalogue rather than your intuition, try to break your own finding, ask
before publishing. Versioned, because a measurement taken under 1.0 is not the
same claim as one taken under 2.0.

Security has the OWASP Testing Guide for this. Data protection had nothing, which
is why no two investigations were comparable.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [WANTED.md](WANTED.md), which lists
what we are actually stuck on rather than a wish list.

The cheapest useful contribution is reproducing an entry and reporting what you
saw, including when it did not reproduce. After that: a falsifier we missed, the
national provision for your jurisdiction, a reproduction script, a better title
for something we named badly, or a fault we have not written down because you
work on hardware and we mostly measure browsers.

You get credit in the entry, permanently. Anonymous is fine. And since this
catalogue names no companies, contributing costs you nothing but time.

## Layout

```
 catalogue/    the entries, one JSON each
 schema/       the entry schema, versioned
 law/          provisions, per jurisdiction
 caselaw/      rulings and decisions, with ECLI where one exists
 repro/        manuals, standalone scripts, the bookmarklet
 tools/        replay a rule against a capture, adapt scanner output
 METHOD.md     how to conduct a measurement
```

Build with `python3 build_catalogue.py && python3 build_pages.py`, publish with
`./deploy.sh <target>`. The deploy refuses to run if a single entry fails
validation.

## Status

Draft. Fourteen entries across web, apps, firmware, IoT and vehicles. Reproduction
scripts exist for four of them; the rest is in WANTED.md.

## Licence

Entries, schema and legal material under CC BY 4.0. Tooling under MIT. Both allow
anyone to continue this work, including the numbering, should this catalogue ever
stop. A reference made today has to still resolve in ten years.

Part of [Totale Digitale Waarborging](https://totaledigitalewaarborging.nl),
fourth axis: can you account for it in legal terms?
