# DPE Measurement Method 1.0

How to run an investigation that produces findings other people can check. This
is the counterpart to the catalogue: the catalogue says what a fault is, this
says how you go looking for one.

It is versioned on purpose. A measurement taken under method 1.0 is not the same
claim as one taken under 2.0, and anything you publish should say which version
you used. That is the same reason a scanner pins its methodology hash: without
it, results from different years silently stop being comparable.

---

## 0. Before anything: what you may not do

Everything in this method loads a system the way an ordinary user would and
observes what it does on its own. That boundary is not only legal caution, it is
methodological: anything you can only see by logging in, submitting data or
circumventing a control cannot be reproduced by a third party, and a finding
nobody else can check is not a finding.

So: no logging into accounts that are not yours, no submitting forms with real
data, no circumventing authentication, no load beyond what a normal visit
generates. Where a fault can only be established behind such a boundary, record
it as reconstructed rather than measured, and say so.

## 1. Define the scope before you measure

Write this down first, because deciding afterwards is how selective results
happen.

- Which systems, named exactly. One domain, one app version, one firmware build.
- Which entries from the catalogue you are testing for. Testing for everything
  is not a scope, it is a hope.
- From which country you will measure, and why. Consent flows and telemetry
  behaviour are frequently region-dependent, and a Dutch finding measured from a
  US exit is not a Dutch finding.
- What would make you conclude the fault is absent. Decide this before you look.

## 2. Set up so the measurement means something

| Requirement | Why it matters |
|---|---|
| Clean profile per capture | A warm profile may carry consent granted earlier, which invalidates any pre-consent claim |
| One variable per capture | If two things differ between captures, the difference proves nothing |
| Record the exit country | See above; note it even when it seems irrelevant |
| Record versions | Browser, scanner, firmware, app build. Behaviour changes between them |
| Retain the raw artefact | HAR, PCAP or trace. A summary is not evidence |
| Timestamp everything | Both the capture and the consent event, so order can be established |

For devices, capture upstream at the gateway rather than on the device. A device
cannot be trusted to report its own traffic, and that is the whole point of
measuring it.

## 3. Take a baseline first

Before touching anything, record what the system does when left alone.

For a website that is the no-interaction capture: load the page, touch nothing,
wait long enough for late-firing tags, save. For a device it is the idle window:
leave it powered and unused, capture for long enough that periodic behaviour
appears. Twenty-four hours is not excessive for something with a daily cycle.

The baseline is where most findings actually come from, because it shows what
happens without anyone asking for anything.

## 4. Vary one thing at a time

The strongest evidence in this whole method is a comparison, not an observation.
A single capture showing traffic invites an argument about interpretation. Two
captures differing in exactly one respect leave no room for one.

For consent that means three separate captures, each with a fresh profile: no
interaction, explicit refusal, explicit acceptance. Read the consent state back
after clicking, because an unregistered click measures a failed click and not a
hollow refusal.

For devices it means capturing with the relevant setting on, then off, then
again after a reboot and after an update. A setting that does not survive an
update is a different finding from one that never worked.

## 5. Walk the catalogue, not your intuition

For every entry in scope, check its indicator against the capture. Use the
entry's stated method, not a variation you invented halfway through.

Attribute traffic through the HAR pageref or the initiator chain. Never through
the referer header: it is spoofable and measurement instrumentation spoofs it as
a matter of routine. This single rule prevents the most common false attribution
in this field.

Record negatives too. "Tested for, not found" is information, and a catalogue
where only positives are ever reported tells you nothing about coverage.

## 6. Try to break your own finding

Every entry lists what would refute it. Work through that list and record the
outcome of each: excluded, not excluded, or untested with the reason.

This is the step that separates a finding from an accusation, and it is the step
that gets skipped. An untested falsifier is not a failure as long as you say so;
an unmentioned one is.

Where a falsifier cannot be settled from the capture, say what would settle it.
Often that is a question only the operator can answer, and that question belongs
in your request for comment.

## 7. Establish duration where you can

A single capture is a moment. Archived source, snapshot services and version
histories turn that moment into a period, and a period is a different kind of
claim: an unbroken run of years cannot be repaired retroactively.

Report the strictly uninterrupted run, and report older non-contiguous traces
separately. Overstating continuity is the easiest way to lose an otherwise solid
finding.

## 8. Have someone else reproduce it

Independent reproduction is worth more than any amount of additional measurement
by you. Two routes, and both are cheap:

- Ask a third party to run the entry's reproduction and report what they saw.
- Run a public scanner that keeps a permanent result URL under its own control.
  That result is not yours, cannot be altered by the operator afterwards, and
  survives a clean-up performed after publication.

## 9. Ask before you publish

Give the operator the finding, the raw artefact and the reproduction, and a
deadline. Ask explicitly whether something is missing or misread; a mistake
found before publication costs nobody anything.

**Deadlines.** Thirty days is a reasonable default. That is shorter than the
ninety common for software vulnerabilities, and the difference is deliberate:
switching off a tag is not the same as building, testing and shipping a patch.
Extend once if a concrete remediation plan with a date is offered.

Do not let a party block publication by staying silent, and do not let one remove
a measurement because it has since been fixed. Note the fix with its date
instead. The point of a measurement is that it establishes a moment.

Record the response verbatim, including silence. That a party did not respond is
itself a fact, and paraphrasing a response is how disputes start.

## 10. Publish so it can be checked

State, every time:

- which catalogue entries you found and their numbers
- the method version, this document's, and the version of any tooling
- the measurement date and the country you measured from
- which falsifiers you excluded and which you did not
- where the raw artefact can be obtained

And state what you did not establish. Unlawfulness is for a supervisory authority
or a court. Intent is almost never measurable. Absence of a detection is not
absence of the fault. Saying so plainly costs you nothing and is the reason the
rest of the work holds.

---

## Version history

**1.0**, 2026-07-26. First published version. Cite as *DPE Measurement Method
1.0*.

Changes that alter what a measurement means get a new major version. Wording and
examples get a minor. If you publish under a version, that version stays
available at its own address for as long as this catalogue exists.
