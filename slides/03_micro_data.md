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

# What soep-preparation Tries To Solve

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

```python
from soep_preparation.config import METADATA
from soep_preparation.gettsim_inputs.mapping import GAP_NOTES, get_soep_to_gettsim

mapping = get_soep_to_gettsim("2023-07-01")   # qname -> SOEP variable, or None
mapping["geburtsjahr"]                        # 'birth_year'

METADATA["gesetzliche_rente_y"]["reference"]  # 'previous_year'
```

The reference period (i.e., `current`, `previous_year`, `previous_month` and
`time_invariant`) lives in the metadata. See the recipe in the soep-preparation docs
(Naming conventions → Reference period).

---

# Testing the Waters

You probably won't have enough time to prepare the SOEP data to get a publishable
number.

Don't get stuck on details. Figure out whether the pipeline works for your needs.

---

# Task

**10:50–11:55**

1. The pytask run has written the cleaned modules and the metadata catalogue to `bld/`.
1. Find the SOEP variables you need using the metadata catalogue and
   run `create_final_dataset`.
1. Build a mapping table from the GETTSIM inputs you need to the data (`tree`, `dict` or
   `df_and_mapper`).
1. Fill the inputs you don't have in the SOEP with sensible defaults.
1. Drop households with any unobserved value.
1. Run both environments.

