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

### soep-preparation: from raw SOEP to GETTSIM inputs

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

# What soep-preparation tries to solve

- Everyone is using SOEP data, but every researcher cleans it themselves
    - Setting correct variable data types
    - Giving variables sensible names
    - Recoding negatives to missings or 0
    - Deriving new variables from raw ones
    - Figuring out the reference period of each variable, and aligning them to a common
      reference period
- In GETTSIM's case also: Make decisions about which SOEP variable corresponds to which
  GETTSIM input
- soep-preparation is a centralised is an open-source library that does this for you

---

# What `soep-preparation` Does

Three tiers:

**Clean raw variables.** Cast each variable to an adequate dtype, convert SOEP
missing codes to `pd.NA`, give it a readable and standardized names.

**Standard derived variables.** Things that follow directly from the raw data — a
BMI from height and weight, income from regular employment, etc.

**A mapping to GETTSIM's inputs.** With an implied recommendation regarding which SOEP
variable to use for which GETTSIM input

---

# What It Deliberately Does Not Do

- **Analysis.** It prepares data. It does not run models or produce results.

- **A fixed merged dataset.** You assemble what you need.

- **Reweighting.** SOEP design and longitudinal weights are passed through, not applied.

- **Imputation** beyond what SOEP delivers (exception: assets in 2023).

<br/>

<div class="highlight">

Cleaning codes and fixing dtypes is the **boring** half of data preparation, and the
half that is identical for everyone. The judgement calls (sample selection, which
responses are sensible, etc) are still yours to make.

</div>

---

# The GETTSIM Mapping and Reference Periods

- How to obtain the GETTSIM mapping and the reference codes...



--- 

# Workflow

1. Place your data in `soep-preparation/data/V41`.
1. In your terminal run `pixi run pytask` to clean the data.
...
...
1. Use sensible defaults for the required inputs that are not in the SOEP.


---

# Testing the Waters

You probably won't have enough time to prepare the SOEP data to get a publishable
number.

Don't get stuck on details. Figure out whether the pipeline works for your needs.

---

# Task

**10:50–11:55**

1. Open `notebooks/03_micro_data.ipynb`.
1. Paste in your reform.
1. Find the SOEP data you need to compute your targets. Build a mapper from the SOEP
   names to the GETTSIM paths.
1. Invent sensible defaults for the other inputs.
1. Run GETTSIM using the status quo and reform environment.

