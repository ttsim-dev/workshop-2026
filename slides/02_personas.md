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

Marvin Immesberger

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

Yesterday you changed the law and one number moved.

Today you vary a household along one dimension and watch the whole budget constraint
move.

---

# The Problem Personas Solve

GETTSIM needs **close to a hundred input columns** to compute everything it covers.

<br/>

If you only care about the income tax, you should not have to invent an employment
biography to get a number out.

<br/>

A persona gives you:

- a **minimal set of inputs** for one question,
- with the nodes you do not care about **overridden** — pension benefits set to zero
  when you are looking at the income tax,
- plus sensible **tax-transfer targets** and a **policy date**.

<br/>

<div class="text-gray-500">

And when you do bring your own data: a persona is the worked example of what
GETTSIM wants it to look like.

</div>

---

# What a Persona Is

Four things, ready to hand to `main`:

```python
from gettsim_personas import grundsicherung_für_erwerbsfähige

persona = grundsicherung_für_erwerbsfähige.SingleAdult(policy_date_str="2023-07-01")

persona.description        # what it is for, and what was zeroed out
persona.input_data_tree    # the households
persona.tt_targets_tree    # the quantities
persona.policy_date
```

<br/>

Read `persona.description` before you use one. It tells you what has been assumed away.

---

# What Exists

| module | personas |
|---|---|
| `einkommensteuer_sozialabgaben` | `Couple1Child` |
| `gesetzliche_altersrente` | `SingleWithFixedPublicPension`, `CoupleWithFixedPublicPension` |
| `grundsicherung_für_erwerbsfähige` | `SingleAdult`, `Single1Child`, `CoupleNoChildren`, `Couple1Child`, `Couple2Children`, `Couple1ChildInKarenzzeit` |
| `grundsicherung_im_alter` | `SingleNoChild`, `Single1Child`, `CoupleNoChild`, `Couple1Child` |

<br/>

That is a short list, and deliberately so.

If none fits your topic, **writing one is a legitimate use of this session** — each is a
handful of small decorated functions in `gettsim-personas/src/_gettsim_personas/de/`.

---

# Varying a Household

Earnings have their own sweep:

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
    input_data_to_upsert={"wohnen": {"bruttokaltmiete_m_hh": np.linspace(300, 1200, 91)}}
)
```

<div class="text-gray-500 text-sm">

Order matters: positions in the input arrays encode who is who. `[0, 0, 4000]` and
`[4000, 0, 0]` are different households.

</div>

---

# What You Are Looking For

Run the same grid under both environments, plot them on one axis, then **difference it**.

<br/>

- The **budget constraint**: disposable income against gross earnings.

- The **kinks**: where the slope changes — where one more euro earned is retained at a
  different rate.

<br/>

A reform either **moves** a kink, **creates** one, or **removes** one.

Which of the three did yours do?

---
layout: default
---

# Task

**09:15–10:20**

1. Open `notebooks/02_personas.ipynb`. Run it once as it stands.
2. Paste your reform into the marked cell near the top.
   *Thursday did not finish? Leave the cell alone and use the demo reform.*
3. Pick your persona. If none fits, write one.
4. Choose the dimension your reform actually varies along — earnings is the default,
   but rent, age, or pension income may be the right one.
5. Run the grid under both environments. Plot them together.
6. Difference it. Find your kinks.

<br/>

<div class="text-gray-500">Write down what the kinks did. It is the interesting sentence.</div>

