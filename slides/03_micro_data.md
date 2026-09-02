---
theme: academic
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  GETTSIM Workshop 2026 — Stage 3, soep-preparation
drawings:
  persist: false
transition: fade
title: Stage 3 — From Raw SOEP to GETTSIM Inputs
mdc: true
defaults:
  layout: center
---

# Stage 3 — Micro Data

### `soep-preparation`: from raw SOEP to GETTSIM inputs

Marvin Immesberger

---

# Where You Are

<div class="pipeline">
  <div class="stage">
    <div class="box">gettsim</div>
    <div class="what">the law</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage">
    <div class="box">gettsim-personas</div>
    <div class="what">one household</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage on">
    <div class="box">soep-preparation</div>
    <div class="what">real households</div>
  </div>
</div>

<br/>

Same reform. Now on people who exist.

---

# The Problem

Raw SOEP is a pile of Stata files.

<br/>

- Variable names like `plb0022_h`, spread across modules and waves
- Every variable a `float64`, whatever it actually is
- Missing values encoded as `-1`, `-2`, `-3`, `-5`, `-8` — and they mean different things
- The same concept asked in three modules with three reference periods

<br/>

Everyone who works with SOEP writes this cleaning layer.

Everyone writes it again for the next project.

---

# What `soep-preparation` Does

Three tiers:

**1 · Clean raw variables.** Cast each variable to an adequate dtype, convert SOEP
missing codes to `pd.NA`, give it a readable name. One cleaned module per raw module.

**2 · Standard derived variables.** Things that follow directly from the raw data — a
birth month reconciled across modules, a BMI from height and weight.

**3 · GETTSIM-shaped derived variables.** German programme names aligned to GETTSIM's
spelling, reference periods made explicit so income can be aligned to its policy year.

<br/>

Plus a **metadata catalogue** and `create_final_dataset` to assemble the variables and
waves you need.

---

# What It Deliberately Does Not Do

- **Analysis.** It prepares data. It does not run models or produce results.

- **A fixed merged dataset.** You assemble what you need.

- **Reweighting.** SOEP design and longitudinal weights are passed through, not applied.

- **Imputation** beyond what SOEP delivers.

<br/>

<div class="highlight">

Cleaning codes and fixing dtypes is the **boring** half of data preparation, and the
half that is identical for everyone. The judgement calls — sample selection, what
counts as employed, which reference period is the right one — are still yours.

</div>

---

# The GETTSIM Mapping

`soep_preparation.gettsim_inputs` pairs each GETTSIM qname with the SOEP variable that
comes closest, and emits a table with qname column labels.

```python
gettsim_inputs = pd.read_feather(BLD / "gettsim_inputs" / "gettsim_inputs.arrow")
report = json.loads((BLD / "gettsim_inputs" / "mapping_report.json").read_text())
```

<br/>

<div class="caution">

**A discovery aid, not a ready-to-use input pipe.**

For each GETTSIM concept it records the SOEP variable that comes *closest*. A survey
proxy routinely differs in reference period, aggregation level, or exact definition —
and feeding it to GETTSIM directly can be *worse* than letting GETTSIM compute the node.

Use it to discover which SOEP variable approximates which qname. Then decide, per node.

</div>

---

# Ask GETTSIM What It Needs

Don't guess the input list, and don't read it off the mapping report — that report is
scoped to `soep-preparation`'s ambitions, not to *your* targets. Request it:

```python
main(
    main_target=MainTarget.templates.input_data_dtypes.tree,
    tt_targets=TTTargets.tree(TARGETS),
    policy_date_str=POLICY_DATE,
)
```

<br/>

Hand it a node you already know the value of, and GETTSIM drops that node's **entire
upstream subtree** from the list:

```python
input_data=InputData.tree(
    {"sozialversicherung": {"rente": {"altersrente": {"betrag_m": ...}}}}
)
```

<br/>

<div class="highlight">

Altersrente, Erwerbsminderungsrente, Arbeitslosengeld, Elterngeld, Unterhaltsvorschuss
— five overrides, and the list goes from **83 to 53** inputs.

Without them you owe GETTSIM a contribution history and an Elterngeld biography per
person. SOEP carries neither.

</div>

---

# The Gap

Some GETTSIM inputs have no SOEP source at all.

<br/>

You close it with **one mapper**. Every leaf is either a column of your DataFrame or a
constant — mapped and assumed sit side by side, in one tree:

```python
MAPPER = {
    "alter": "age",                                  # a column
    "einnahmen": {"bruttolohn_m": "bruttolohn_m"},   # a column
    "vermögen": 0.0,                                 # wealth unsurveyed since 2017
    "wohngeld": {"mietstufe_hh": 3},                 # no Gemeindekennziffer in SOEP
}

main(input_data=InputData.df_and_mapper(df=soep, mapper=MAPPER), ...)
```

<br/>

Where an input is simply **unobserved**, the household is dropped rather than
zero-filled — an unobserved rent would make a household look rent-free.

<br/>

<div class="text-gray-500">

Nothing is hidden: every constant carries its justification as a comment, next to the
columns it sits among.

</div>

---
layout: center
class: text-center
---

# So: Testing the Waters

The pipeline is real. The reform is real. The households are real.

<br/>

What comes out is **GETTSIM output on real households, not results**. It rests on one
year's cross-section, a column of assumed constants, a complete-case sample — and **no
asset test at all**: SOEP surveys wealth only in 2002, 2007, 2012 and 2017, so
`vermögen` is zero for everyone, which over-states entitlement.

Your own data cleaning is where that gets fixed, and it is most of the work. The
analysis on top of it is yours.

<br/>

What you are checking in the next hour is whether the road exists.

---
layout: default
---

# Task

**10:50–11:55**

1. Open `notebooks/03_micro_data.ipynb`. One machine per group — the one with SOEP.
2. Paste in your reform, or leave the demo reform in place.
3. Which inputs does *your* reform touch? Mapped column or assumed constant? Read the
   mapper and find out.
4. For anything assumed: decide what you would rather assume, and change it.
5. Run both environments over the sample and read the two result frames.

<br/>

<div class="text-gray-500">

Watch the aggregation levels. A household can hold more than one Bedarfsgemeinschaft,
and a `_bg` value is repeated on every one of its members — so summing across people
double-counts. The notebook stops at GETTSIM's output and points at the trap; the
weights, the sample and the aggregation are yours to choose.

</div>

