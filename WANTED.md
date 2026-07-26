# Wanted

Open questions we are stuck on. Not a wish list and not an empty numbering: every
line below is a concrete gap, with what an answer would look like.

Whoever closes one is credited in the entry, permanently.

---

## Detection we have no good indicator for

**DPE-2026-0012, device telemetry, made scriptable.**
The manual route works: capture at the gateway, leave the device alone, see what
goes out anyway. What is missing is an indicator a script can test. Where it
breaks down: distinguishing a legitimate update check from telemetry cannot be
derived from the traffic alone.

*What helps:* an idle capture of a consumer device, with model and firmware
version, plus your reasoning for why a given flow is or is not functional. A
negative result is useful too.

**DPE-2026-0013, bundled components in pinned applications.**
Components with certificate pinning cannot simply be read along with. We do not
want a method that amounts to breaking someone else's application.

*What helps:* an approach that stays within bounds and still establishes which
hosts a component contacts. Static inventory plus DNS observation may be enough;
we do not know.

**DPE-2026-0007, fingerprinting without a debugging protocol.**
Establishing it currently requires hooking property reads through the debugger.
An ordinary user cannot do that.

*What helps:* a bookmarklet-style route that shows a third-party script reading
device characteristics, without a debugger attached.

## Faults that certainly exist but are not here yet

We see them but cannot define them sharply enough to justify a number.

- A television establishing what is on screen and reporting it. Demonstrably
  real; we have no measurement setup.
- A vehicle sharing location or driving behaviour with the manufacturer with no
  setting that stops it. Touches DPE-2026-0012 and 0014 but probably deserves its
  own number.
- School and parenting applications. No measurements exist in our sources at all.
- Payment terminals beyond the web checkout. DPE-2026-0025 is written from the
  mechanism rather than from a measurement, which is weaker than the rest of the
  catalogue and should be strengthened or narrowed.

*What helps:* a description of the mechanism, and above all the boundary. When is
this the fault and when is it ordinary operation?

## Jurisdictions outside the Netherlands

The faults are the same across the EEA; only the citation differs. `law/` holds
Dutch and EU provisions only.

*What helps:* the national provision in your country implementing the same EU
rule, in the format of an existing file. For Germany that is presumably §25
TDDDG, for Belgium an article in the electronic communications act, but we are
not at home there and would rather not guess.

Two files are already marked `verified: false` because the article numbers come
from knowledge rather than from checking the text: `nl-uavg-46` and
`nl-sv-126jj`. Someone who can check them against the source would settle that.

## Case law

Three rulings are in. There is far more, and rulings that **narrow** an entry are
especially welcome: those make an entry usable in a discussion rather than only
in an accusation.

*What helps:* the ECLI, the holding in two sentences, and which entry it touches.

## Reproduction routes

Most entries share `repro/web/check.mjs`, which tests eight of them in one run.
The remaining ones have no route of their own, and several device entries can
only be done by hand.

*What helps:* a script for one entry. That is a contained piece of work of about
an hour, and it is the most concrete contribution available.
`repro/web/check.mjs` is the model: standalone, one dependency, and it reports
what it cannot see.

## Naming

A title that does not stick will not be used. These are worth a second opinion:

- **DPE-2026-0021**, "Probing the visitor's own device". Accurate but long.
- **DPE-2026-0023**, "Presence revealed by an automatic reply". Describes the
  mechanism well and reads awkwardly.
- **DPE-2026-0029**, "Failed capture read as a clean result". Correct, but it
  should be recognisable to someone who has just made that mistake.

A proposal works if it is descriptive rather than a codename, describes the
behaviour of the system rather than the harm to the person, and can be said out
loud in a conversation with an editor.

---

## How to send something

An issue is enough. A pull request is welcome but not expected. Loose notes in an
issue are fine too: we will write it up and you appear as contributor.

See [CONTRIBUTING.md](CONTRIBUTING.md).
