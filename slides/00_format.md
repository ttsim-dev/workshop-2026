---
theme: academic
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  GETTSIM Workshop 2026 — workshop format and group formation
drawings:
  persist: false
transition: fade
title: Workshop Format and Group Formation
mdc: true
defaults:
  layout: center
---

# Workshop Format

### GETTSIM Workshop 2026 · Bonn

---

# The Next Two Days

You work **in a group**, on **one policy reform you care about**.

<br/>

The reform is taken once around the ecosystem:

- **Thursday afternoon** — find it in the law, then change the law

- **Friday morning** — see what it does to a household

- **Friday late morning** — see what how it interacts with data from the SOEP

<br/>

On Friday we are interested in your experiences: What worked well, what didn't? What do
you need to make it work better?

---

# The Round Trip

<div class="pipeline">
  <div class="stage on">
    <div class="box">gettsim</div>
    <div class="what">the law</div>
    <div class="when">Stage 1 · Thu 14:00</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage on">
    <div class="box">gettsim-personas</div>
    <div class="what">one household</div>
    <div class="when">Stage 2 · Fri 09:15</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage on">
    <div class="box">soep-preparation</div>
    <div class="what">real households</div>
    <div class="when">Stage 3 · Fri 10:50</div>
  </div>
</div>

<br/>

We will give you example code for each stage. Feel free to use it, or not.

---

# One Reform, Three Stages

**Stage 1.** Find your topic in GETTSIM's implementation of current law. Make sure the
current status quo looks right. Then implement the reform via a custom policy
environment.

**Stage 2.** Put your reform on a (range of) **Musterhaushalte** and vary a dimension —
earnings, rent, pension income. How does your reform change household's buget
constraint?

**Stage 3.** Take the same reform to SOEP. Who gains, who loses, what does it cost?

---

# If You Have No Topic

Some suggestions:

<div class="briefs">

**Grundsicherung im Alter after the Alterssicherungskommission**
Freibetrag on statutory pensions for everyone. 

**A capital pension and the Nettoersatzrate**
How does the planned gesetzliche Kapitalrente affect the net replacement rates of poor
and rich retirees?

**Familiensplitting instead of Ehegattensplitting**
Pick your favorite implementation and see how it affects income taxes.

</div>

---

# Matchmaking

**Requirement**: At least one person with a GETTSIM installation and SOEP access
**Group Formation**: Tell the audience what you want to work on, then people can
self-select

---

# Use all the help you can get

Just a few months ago, this roundtrip would have taken days for newbies. 

Use all the help you can get:

    - Your group members
    - Your favorite AI
    - The GETTSIM documentation
    - The example notebook
    - Hans-Martin and me

It's finish that you finish somewhat on time so that we can continue. Don't overengineer.

---
layout: center
class: text-center
---

# Raise Your Hand

Which reform do you want to work on?

