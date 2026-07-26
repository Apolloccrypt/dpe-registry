# Establishing that the off switch does not exist, or does not hold

For DPE-2026-0014, no working off switch.

This is a comparison, not an observation. A single capture showing traffic proves
nothing here; what proves it is that the traffic is the same with the setting on
as with it off, or that the setting quietly returns to on.

Set aside an afternoon plus one update cycle, which may be weeks. That waiting is
the reason this fault is rarely reported and often present.

---

## Before you start

Find every place a setting could live. This is where most attempts go wrong, and
a missed setting turns a finding into an embarrassment.

- the device's own interface
- the companion app, which frequently has options the device does not
- a web interface on the device's own address
- the manufacturer's account page, where account-level settings can override
  device-level ones

Write down what you found and where. If a control exists anywhere, however buried,
this entry does not apply. The fault is that it is missing or that it does not
hold, not that it is hard to find.

## The four captures

Capture the same idle window four times, using the method in
[`../DPE-2026-0012/MANUAL.md`](../DPE-2026-0012/MANUAL.md). One variable changes each time.

| # | State | What it tells you |
|---|---|---|
| 1 | setting on, or absent | the baseline |
| 2 | setting off | whether the control does anything at all |
| 3 | after a reboot | whether the choice survives a power cycle |
| 4 | after a firmware update | whether the choice survives maintenance |

Between each, read the setting back in the interface. A control that reverted is
already the finding, and you want to be able to say you checked rather than
assumed.

Record the firmware version at every step. "Reset on update" and "reset on reboot"
are different findings with different consequences, and the version is how you
tell them apart afterwards.

## Reading the result

**Captures 1 and 2 are the same.** The control does not do what it says. Report
which destinations survived, by name; a count is not checkable.

**Capture 3 differs from 2.** The choice does not survive a power cycle. For a
device that reboots after every power cut, that means the setting is effectively
temporary.

**Capture 4 differs from 2.** The choice does not survive maintenance. This is the
most consequential variant, because updates arrive without the owner doing
anything and the reversal is therefore silent.

**No control anywhere.** Then captures 3 and 4 are not needed and the finding is
simply that there is no way to refuse. Note that a manual is not a control: a
document explaining that data is collected does not let anyone stop it.

## Falsifiers

**Is the control somewhere you did not look?** The single most common error. Check
the companion app and the manufacturer's account page before you conclude
anything.

**Is the remaining traffic strictly necessary to operate the device?** A thermostat
that needs the cloud to function is a different discussion from one that reports
usage on the side. Disable the traffic at the network level and see what stops
working; if the device keeps doing its job, necessity is hard to maintain.

**Did you factory reset during testing?** That explains a reverted setting without
any fault. Note every reset you performed.

## What to write down

The four captures with their firmware versions, where you looked for a control and
what you found, which destinations survived which state, and what you could not
settle. Keep the captures.

State the variant precisely. "No off switch" and "the off switch resets on update"
are different claims, and using the stronger one when you measured the weaker is
how a solid finding gets taken apart.
