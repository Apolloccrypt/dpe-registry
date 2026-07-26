# DPE Exposure Vector, version 1.0

The vector describes **what was measured**. It carries no judgement of lawfulness
and no severity number. Severity labels and weightings are derived from it by
published rules (see the bottom of this document), and any such label is the
opinion of the party that assigned it.

The notation follows CVSS deliberately: a security professional reads it at a
glance, and a vector string is citable, diffable and machine-parseable.

## String form

    DPE:1.0/EV:M/CS:PRE/DC:ID+BEH/RC:3P/JU:3C/SC:NAT

Axes appear in fixed order. Every axis is mandatory. `DC` may carry several
values joined by `+`. Unknown or not-yet-determined values use `X`.

## Axes

### EV, Evidence

How the exposure is known. This is the most important axis, because it separates
what was observed from what was inferred.

| Value | Meaning |
|---|---|
| `M`  | Measured. Own instrumented capture, raw artefact retained (HAR, PCAP, CDP log). |
| `R`  | Reconstructed. Derived from artefacts not captured for this purpose, e.g. static decompilation, published configuration. |
| `T`  | Third-party report. Someone else measured it, artefact reviewed but not reproduced. |
| `S`  | Suspected. Consistent with the pattern, not established. Records at `S` are never published above TLP:AMBER. |

### CS, Consent state

At which point in the consent flow the exposure occurred. Requires a separate
capture per state; a single capture cannot establish this axis.

| Value | Meaning |
|---|---|
| `PRE` | Before the consent question was answered. |
| `REJ` | After consent was refused. |
| `ACC` | After consent was granted. |
| `NA`  | No consent mechanism present, or consent is not the applicable basis. |
| `X`   | Not determined. |

### DC, Data categories

What kind of personal data left. Combine with `+`.

| Value | Meaning |
|---|---|
| `ID`  | Technical identifier (cookie, device id, fingerprint, hashed e-mail). |
| `BEH` | Behaviour (pages, clicks, dwell, scroll). |
| `LOC` | Location (GPS, or IP used as location). |
| `CNT` | Content the person entered or requested (search term, form field, URL path revealing intent). |
| `SPC` | Special category under GDPR art. 9 (health, sexuality, religion, ethnicity, politics, union membership, biometrics for identification). |
| `IDD` | Identity document or facial image submitted for verification. |

### RC, Recipient

How far the data travelled in controller terms, not in network terms.

| Value | Meaning |
|---|---|
| `1P`  | First party only. |
| `PR`  | Processor under a documented processing agreement. |
| `3P`  | Named third party acting for its own purposes. |
| `UND` | Undefined audience. Real-time bidding broadcast or any flow where the set of recipients is not determinable at send time. |

### JU, Jurisdiction

Legal class of the destination. The concrete countries go in the `destinations`
field of the record, not in the vector, so the vector stays stable when a CDN
shifts an edge node.

| Value | Meaning |
|---|---|
| `EU`  | Destination inside the EEA. |
| `ADQ` | Third country covered by an adequacy decision. |
| `3C`  | Third country without adequacy. |
| `HR`  | High-risk jurisdiction: no adequacy, plus a statutory government access regime or an established pattern of onward transfer. |
| `X`   | Not determined. |

### SC, Scope

How wide the exposure reaches. This is what makes a record worth an institution's
attention, and `VND` is the reason the vendor layer exists.

| Value | Meaning |
|---|---|
| `ONE` | One deployment (a single site, app or endpoint). |
| `SEC` | A sector or an identifiable group of deployments. |
| `NAT` | National reach: the deployment serves a substantial share of the population. |
| `VND` | A vendor product, in its default or documented configuration. Every deployment of that product inherits the exposure. |

## Derived severity

Severity is not part of the vector. It is derived by rule, the rule is public,
and the rule is versioned so that a record from last year can still be read.

    rule dpe-severity-1.0

    critical   EV:M  and  DC contains SPC or IDD  and  CS:PRE or CS:REJ
               and  RC:3P or RC:UND
    high       EV:M  and  CS:PRE or CS:REJ  and  RC:3P or RC:UND
               or   EV:M  and  DC contains SPC or IDD  and  JU:3C or JU:HR
    medium     EV:M  and  (CS:PRE or CS:REJ or JU:3C or JU:HR)
    low        everything else at EV:M
    unrated    EV:R, EV:T or EV:S

Two consequences worth stating plainly. A record at `EV:S` is never rated, so a
suspicion can never be quoted as a severity. And `SC` does not enter the severity
rule at all: reach is reported separately, because a national scope makes an
exposure more important without making it worse.
