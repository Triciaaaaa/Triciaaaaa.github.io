---
title: "Who Decides the Exception: The Three Gates of Distributed Shutdown"
description: Pausing a multi-principal system decomposes into three necessary gates. Detection, attribution, intervention. Every observed safety failure jams in exactly one of them.
date: 2026-08-02
cover: /art/abstract/calm-ink.jpg
coverAlt: A black-ink abstraction of Poussin's Landscape with a Calm, water and a castle silhouette
coverCaption: fig. · landscape with a calm<br />n. poussin, 1650–51 / riso print
tags: [research-note]
---

If something goes wrong, switch it off. This is the oldest intuition in AI safety, and the least interrogated. The off-switch problem for a single agent has a mature literature; but nothing worth worrying about today is a single agent. The systems that matter are multi-principal: several developers, several deployers, several regulators, each seeing one corner of the whole.

At that point "switch it off" stops being a button and becomes a **problem of sovereignty**: when no single principal holds enough information to act alone, who has the authority to decide the state of exception?

## The three gates

Our approach is to decompose "pausing a multi-principal system" into three gates that any legitimate pause must pass through:

1. **Detection** — someone has to see the anomaly first. In distributed deployment the signals are scattered across different principals' logs, each individually below threshold.
2. **Attribution** — seeing is not enough; you must be able to say whose component, and which layer of interaction, produced the problem. When attribution fails, every principal sincerely believes the fault lies elsewhere.
3. **Intervention** — attribution settled, someone must actually hold the stop capability, at a cost of exercise low enough that somebody is willing to move first.

The value of the decomposition is that **every safety failure observed so far maps to exactly one gate**. It gives failure an address.

## What the lower bounds mean

The technical core of the paper is a set of conditional lower bounds: for each gate, how much information a principal must hold to make a legitimate pause decision. The political meaning of these bounds is more interesting than the mathematical one — they show that under certain information structures, *no* single principal can legitimately decide the exception.

In other words: Schmitt's sovereign is ruled out by theorem. Two options remain — design information-sharing mechanisms that feed the bounds, or admit that the system is structurally unpausable. The latter should be read as a red light visible before deployment, not after.

---

This is the informal waymark for a paper currently under review. I wrote it to remind myself that every step of formalization must translate back into the three old questions: who, by what right, answerable to whom.
