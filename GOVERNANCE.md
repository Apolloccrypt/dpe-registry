# Governance

A catalogue that depends on one person is not a standard. This document exists to
make that dependency visible and, over time, unnecessary.

It is deliberately short. The catalogue names no organisations, so most of the
machinery a disclosure register needs does not apply here: there is nobody to
notify, nothing under embargo and no party with a right of reply. What remains is
the question of who may change a definition, and on what grounds.

---

## Roles

**Contributor.** Anyone. Proposes entries, reproduces them, sharpens a falsifier,
adds a jurisdiction, or argues that an entry is wrong. Needs no permission and no
account beyond GitHub. Credited in the entry, or anonymous if preferred.

**Editor.** May accept a proposal, assign a number, and mark an entry deprecated.
Editors are listed by name in the repository, so it is visible who is shaping the
catalogue.

At the time of writing there is one editor. That is a starting condition, not a
design, and this document exists to be able to leave it behind.

## What an editor may not do

These limits exist so that an outcome does not depend on who happened to handle
it.

- **Assign a severity.** There is none in the schema and none may be introduced
  without a major version. The catalogue standardises a finding so it can be
  referenced; weighing belongs to whoever applies it to a concrete case.
- **Name a party in an entry.** No organisation, product or domain, ever, in any
  field. An entry that needs a vendor name to be understood is not yet properly
  described.
- **Change an entry silently.** Every change is an appended line in `changes`,
  and that list is append-only. An entry whose earlier lines were edited is
  rejected.
- **Reuse a number.** Not after deprecation, not after a merge. References exist
  elsewhere and they must keep resolving.
- **Accept an entry without a falsifier.** If nothing would refute it, it is not
  a finding but an opinion.

## Changing a definition

Entries shift as the field learns. What matters is that a reader in five years
can tell what an entry meant when it was cited.

- **Sharpening** an indicator, adding a falsifier, adding a jurisdiction: a
  normal change, appended to `changes`.
- **Narrowing or widening the scope** of an entry: only if the old reading stays
  legible. Say in `changes` what shifted and when.
- **Replacing an entry** with a better-defined one: the old entry gets status
  `superseded` and points at the new one. It stays online.
- **Withdrawing** an entry that turned out to be wrong: status `deprecated`, with
  the reason. It stays online too. A finding that vanishes cannot be checked, and
  someone cited it.

The schema and the measurement method carry their own version numbers. A change
that alters what a measurement means requires a new major version; wording and
examples get a minor one.

## Conflict of interest

An editor does not decide on an entry that concerns work they were paid for.
That situation is not hypothetical: whoever maintains a standard tends to be the
same person who is asked to apply it. Where the catalogue is maintained by one
party and services are sold on top of it, those should sit in separate legal
entities, and it should be visible which is which.

Measuring the catalogue's own infrastructure is encouraged. Anyone who measures
others should be measuring themselves.

## Becoming an editor

Organisations with a demonstrable stake can join: research groups, civil society
organisations, newsrooms, supervisory authorities. Conditions: endorse this
document, and have contributed either three accepted entries or ten
reproductions.

That threshold is low on purpose. It exists to establish that someone knows the
method, not to keep the door shut.

## If this stops

Everything is under CC BY 4.0 for the entries and MIT for the tooling, in a
public repository. Anyone may continue or take over this catalogue, including the
numbering. That is not a fallback but the point: a reference made today has to
still mean something in ten years, whether or not the people behind it are still
here.
