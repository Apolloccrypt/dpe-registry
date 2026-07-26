# Establishing what a device contacts on its own

For DPE-2026-0012, device telemetry without function, and useful as the baseline
for DPE-2026-0014 as well.

A website can be inspected with the browser it is displayed in. A router, a
television or a car cannot: there is no console, no developer panel, and the
device is the last thing you should trust to report its own traffic. So you
measure it from outside, on the network it sits on.

This takes an evening of preparation and then runs by itself.

---

## What you are trying to establish

Not that the device talks to the internet. Everything does. What matters is
traffic that serves no function the owner asked for, continuing while the device
is doing nothing.

That is why the idle window is the whole method. A device left alone should be
close to silent. What it does anyway is the finding.

## What you need

- A way to see the device's traffic without the device knowing: a router that can
  mirror or log, a Raspberry Pi between the device and the network, or a laptop
  sharing its connection.
- Something to record with: `tcpdump` or Wireshark. Both are free and both write
  a file you can hand to someone else.
- Patience. A device with a daily cycle will not show it in ten minutes.

You do not need to break encryption. Which hosts are contacted, how often, and
how much data goes out is enough for this entry, and all of it is visible without
touching the contents.

## Step 1: put the device on its own segment

Give it a network where nothing else is talking, otherwise you will spend your
evening separating its traffic from your phone's. A guest network or a spare
router is enough.

Note the device's address. Everything below filters on it.

## Step 2: record the idle window

Start the capture, then leave the device completely alone. Do not open the app,
do not press a button, do not walk past a camera.

```
sudo tcpdump -i <interface> host <device-ip> -w idle.pcap
```

Twenty-four hours is not excessive. Many devices report on a daily rhythm, and a
ten-minute capture will miss it and give you false confidence that there is
nothing to see.

Write down, because you will need it in the write-up and will not remember:

- brand, model, firmware version, and the region the device is set to
- when the capture started and stopped
- whether anything was configured during setup that could explain traffic
- whether the device was newly installed or had been running for a while

## Step 3: see who it talked to

```
tcpdump -r idle.pcap -nn 'tcp[tcpflags] & tcp-syn != 0' | awk '{print $5}' | sort | uniq -c | sort -rn
tcpdump -r idle.pcap -nn port 53 | grep -oE '[A-Za-z0-9.-]+\.[a-z]{2,}' | sort -u
```

The first line lists what it connected to and how often. The second lists the
names it looked up, which is usually more informative than the addresses.

For each destination, ask the only question that matters: **which function that
the owner enabled requires this?** An update check is defensible. A connection
every five minutes to a host that has nothing to do with the product is what this
entry is about.

## Step 4: establish where it actually goes

Look up who the address belongs to and where it routes, not where the company is
headquartered. Those are different things and confusing them is the fastest way
to lose an otherwise solid finding: a brand can be based anywhere while its
traffic terminates somewhere else entirely, and the reverse happens just as often.

```
whois <ip>
```

A content delivery network in front of a service tells you little on its own. Say
so rather than overstating it.

## Step 5: work through the falsifiers

The entry lists them; these three do the work.

**Does a function the owner enabled explain this?** Turn that function off, capture
again, and see whether the traffic goes with it. If it does, this is not the entry.

**Can it be switched off?** If there is a setting, use it and capture again. Traffic
that continues is a stronger finding; traffic that stops means the fault is that it
was on by default, which is a different and weaker claim. Say which one you have.

**Does it survive a reboot and an update?** This is where DPE-2026-0014 begins. A
setting that resets on update is its own finding.

## Step 6: write it down so someone else can repeat it

State the model and firmware, the capture window, the destinations with their
frequency, which functions you disabled to test, and which falsifiers you could
not settle. Keep the pcap: it is the evidence, and someone else can read it
without your tooling.

Say what you did not establish. You saw where traffic went, not what was in it,
unless you inspected the contents and can show that. That distinction is the
difference between a finding that holds and one that gets picked apart.

---

## What this cannot show

- **What is in the payload**, unless it is unencrypted. Which host, how often and
  how much is what this method gives you, and for this entry that is enough.
- **Whether the data is personal.** A device identifier tied to a household
  usually is, but that is an argument you make, not something the capture proves.
- **Absence.** Nothing during your window does not mean nothing ever. A device may
  report weekly, or only after an event you did not trigger.

## A cheaper first look

No capture setup at hand? Point the device's DNS at a resolver that logs, such as
a Pi-hole, and read the query log after a day. That shows you the names it looks
up, which is often enough to know whether a proper capture is worth the evening.
It is a lead, not evidence: DNS queries do not prove a connection was made.
