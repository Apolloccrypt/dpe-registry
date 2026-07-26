# Contributing

This catalogue improves the way CVE entries improve: because people who use them
send back what they ran into. You do not need to be a researcher, and you do not
need permission.

Whatever you contribute, your name stays attached to the entry, permanently and
citably. Anonymous is fine and changes nothing about how it is handled.

---

## First, the thing that makes this cheap for you

**This catalogue names no companies.** No organisation, no product, no domain
appears in any entry. So contributing here does not expose you to anyone: you are
describing a class of fault, not accusing a party.

If you want to publish that a specific system exhibits a fault, that is your
publication under your own name, and [METHOD.md](METHOD.md) sets out how to do
that so it holds up. This repository is not involved in that and does not host it.

**One boundary applies to everything here.** Every method in this catalogue loads
a system the way an ordinary user would and observes what it does on its own. No
logging into accounts that are not yours, no submitting data, no circumventing
controls, no load beyond a normal visit. That is not only caution: anything you
can only see by crossing that line cannot be reproduced by anyone else, and a
finding nobody can check is not a finding.

---

## Four ways in

### 1. Reproduce an entry · 5 minutes

The cheapest useful contribution, and the one that makes the catalogue trustworthy
rather than merely opinionated.

Pick an entry, follow its reproduction, and report what you saw. Every entry has a
route that needs nothing but a browser.

**A failed reproduction is at least as valuable.** If our indicator does not fire
where it should, or fires where it should not, the entry is wrong and we want to
know. Mention which country you measured from: consent flows and telemetry are
frequently region-dependent, and that explains a difference more often than an
error does.

### 2. Sharpen an entry · 15 minutes

Read one entry critically and tell us what is missing.

- a falsifier we did not list, meaning an objection the entry currently cannot
  answer
- an indicator that is looser than it looks, one that would also fire on
  legitimate behaviour
- a boundary we drew badly against a neighbouring entry
- a better title, if we named something in a way that does not stick

### 3. Add a jurisdiction or a ruling · 30 minutes

The faults are the same across the EEA; only the citation differs. Right now
`law/` holds Dutch and EU provisions only.

Send the national provision in your country that implements the same EU rule, in
the format of an existing file in `law/`. For case law: the ECLI, the holding in
two sentences, and which entry it touches.

**Rulings that narrow an entry are especially welcome.** They make it usable in a
discussion rather than only in an accusation.

### 4. Write an entry or a script · an afternoon

A fault we have not described, or a reproduction script for one of the entries
that lacks one. [WANTED.md](WANTED.md) lists what we are actually stuck on, which
is a better starting point than an empty template.

We mostly measure browsers. If you work on firmware, routers, televisions, cars
or apps, you will see things we cannot.

---

## What an entry has to contain

Not a form to fill in. These are the parts that make an entry usable by someone
who is not you.

| Part | Why |
|---|---|
| The mechanism | how the fault arises, technically, without naming a vendor |
| An indicator | something checkable without interpretation |
| Capture requirements | conditions a measurement must meet, or it produces a confident wrong answer |
| Falsifiers | at least one, and honesty about which cannot be settled from a capture |
| A reproduction | one route that needs no tooling this project owns |
| Provisions | which rules it engages, per jurisdiction |
| The boundary | the neighbouring fault it will be confused with, and the dividing line |

Two things you never provide: the number and any severity. The number is assigned
on acceptance so simultaneous submissions cannot collide. Severity does not exist
here at all, by design.

**Titles.** The English title is a noun phrase that describes the fault, never a
codename. The Dutch title follows the same rule: a noun phrase, no finite verb,
addressing nobody, and readable on its own outside the table it appears in. A
title that only works as a row in a list will be rewritten, because most people
meet it as a link or in a sentence somewhere else.

**Legal.** State `legal.applies`. Almost every entry is `to-processing` and then
at least one provision is cited. An entry that describes a fault in a finding
rather than in a processing operation is `to-a-finding` and cites no provision at
all: there is none that binds the researcher, and quoting one against them is the
first thing an opponent will take apart.

---

## How to send it

Open an issue. A pull request is welcome but not expected, and loose notes in an
issue are fine too: we will write it up and you appear as contributor.

Expect an answer within five working days, including when the answer is no, with
the reason. A submission left hanging is our failure and you may hold us to it.
