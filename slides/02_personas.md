---
theme: academic
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  GETTSIM Workshop 2026 — Stage 2, personas
drawings:
  persist: false
transition: fade
title: Stage 2 — Musterhaushalte
mdc: true
defaults:
  layout: center
---

# Stage 2 — Musterhaushalte

### `gettsim-personas`

---

# Where You Are

<div class="pipeline">
  <div class="stage">
    <div class="box">gettsim</div>
    <div class="what">the law</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage on">
    <div class="box">gettsim-personas</div>
    <div class="what">one household</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage">
    <div class="box">soep-preparation</div>
    <div class="what">real households</div>
  </div>
</div>

<br/>

Yesterday you changed the law and (hopefully) numbers moved.

Today you vary a household along one dimension and watch the whole budget constraint
move.

---

# The Problem Personas Solve

GETTSIM needs **close to a hundred input columns** to compute everything it covers.


If you only care about the income tax, you should not have to invent an employment
biography to get a number out.


A persona gives you:

- a **minimal set of inputs** for one question,
- with the nodes you do not care about **overridden** — e.g. pension benefits set to zero
  when you are looking at the income tax of a young adult,
- plus sensible **tax-transfer targets**.

---

# What a Persona Is

Four things, ready to hand to `main`:

```python
from gettsim_personas import grundsicherung_für_erwerbsfähige

persona = grundsicherung_für_erwerbsfähige.SingleAdult(policy_date_str="2023-07-01")

persona.description        # what it is for, and what was zeroed out
persona.input_data_tree    # the example input data
persona.tt_targets_tree    # the TT targets
persona.policy_date
```

<br/>

Read `persona.description` before you use one. It tells you what its purpose is.

---

# What Exists

| module | personas |
|---|---|
| `einkommensteuer_sozialabgaben` | `Couple1Child` |
| `gesetzliche_altersrente` | `SingleWithFixedPublicPension`, `CoupleWithFixedPublicPension` |
| `grundsicherung_für_erwerbsfähige` | `SingleAdult`, `Single1Child`, `CoupleNoChildren`, `Couple1Child`, `Couple2Children`, `Couple1ChildInKarenzzeit` |
| `grundsicherung_im_alter` | `SingleNoChild`, `Single1Child`, `CoupleNoChild`, `Couple1Child` |

<br/>

If none fits your topic, either

- write a new persona (and create a PR such that others can use it -- don't worry, it's
  easy), or
- start from an existing persona and manipulate its input data tree.

---

# Varying a Household

Varying earnings is built in:

```python
Single = grundsicherung_für_erwerbsfähige.SingleAdult

swept = Single(
    policy_date_str=POLICY_DATE,
    bruttolohn_m_linspace_grid=Single.LinspaceGrid(
        p0=Single.LinspaceRange(bottom=0, top=2_000),
        n_points=201,
    ),
)
```

Anything else — rent, age, pension income — goes through `upsert_input_data`:

```python
persona.upsert_input_data(
    input_data_to_upsert={"wohnen": {"bruttokaltmiete_m_hh": YOUR_INPUT_DATA_HERE}}
)
```

`gettsim-personas` scales all other inputs to match your upserted input data.

---
layout: default
---

# Task

**09:15–10:20**

1. Open `notebooks/02_personas.ipynb`.
2. Paste your reform into the marked cell near the top.
3. Pick your persona. If none fits, write one.
4. Choose the dimension your reform actually varies along — earnings is the default,
   but rent, age, or pension income may be the right one.
5. Run the grid under both environments. Plot them together.
