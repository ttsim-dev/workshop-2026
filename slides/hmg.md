---
theme: academic
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  GETTSIM Workshop 2026 — what happened between 2024 and 2026
drawings:
  persist: false
transition: fade
title: Two Years
mdc: true
defaults:
  layout: center
---

# Two Years

### What happened to GETTSIM between 2024 and 2026

---

# The Release Log

<div class="timeline">
  <div class="when">2023-05-14</div>
  <div class="what">v0.7</div>
  <div class="gap">— 27 months —</div>
  <div class="when">2025-08-26</div>
  <div class="what">v1.0</div>
  <div class="when">2026-01-12</div>
  <div class="what">v1.1</div>
  <div class="when">2026-03-19</div>
  <div class="what">v1.2</div>
  <div class="when">2026-08-20</div>
  <div class="what">v1.3</div>
  <div class="when">2026-09-02</div>
  <div class="what">v1.3.1 — yesterday</div>
</div>

<br/>

---

# 2024 — Groundwork

<div class="timeline">
  <div class="when">2024-01</div>
  <div class="what"><code>soep-preparation</code> starts as its own repository</div>
  <div class="when">2024</div>
  <div class="what">Rebuild the infrastructure on <code>dags.tree</code> — the tree logic that
    everything since rests on</div>
  <div class="when">2024</div>
  <div class="what">Namespaces move to the module level: the taxes and transfers system
    becomes a nested structure instead of one flat list of names</div>
  <div class="when">2024-11</div>
  <div class="what">Model classes for policy functions and policy environments; move the
    project to pixi</div>
</div>

<br/>

No release, because none of it was usable yet on its own.

---

# 2025 — The Rewrite

**One pull request, seven months, merged 2025-07-24.**

It was not a refactoring. Almost everything changed:

- the taxes and transfers system became a **tree** of typed objects

- `compute_taxes_and_transfers` became **`main`**, driven by a DAG of its own

- parameters got real types, a JSON schema, and their own functions

- the whole thing became **vectorized and jittable**

<br/>


---

# The Split

<div class="pipeline">
  <div class="stage on">
    <div class="box">ttsim</div>
    <div class="what">the engine</div>
    <div class="when">any taxes &amp; transfers system</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage on">
    <div class="box">gettsim</div>
    <div class="what">the German law</div>
    <div class="when">functions, parameters, dates</div>
  </div>
</div>

**TTSIM** knows about DAGs, aggregation, time conversion, backends, and units. It knows
nothing about Germany.

**GETTSIM** is German law expressed in TTSIM's vocabulary.

The engine has its own test system, METTSIM — a small fictional country. It exists so
that TTSIM can be tested without German law getting in the way.

---

# The Offspring

<div class="pipeline">
  <div class="stage on">
    <div class="box">gettsim</div>
    <div class="what">the law</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage on">
    <div class="box">gettsim-personas</div>
    <div class="what">one household</div>
    <div class="when">since 2025-04</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage on">
    <div class="box">soep-preparation</div>
    <div class="what">real households</div>
    <div class="when">since 2024-01</div>
  </div>
</div>

Both exist because of the same complaint: *GETTSIM is great, but I cannot get data into
it.*

Personas answer it for a stylised household, `soep-preparation` for our standard data.
You will use both tomorrow.

---

# 2026 — Correctness (I)

The rewrite bought us the ability to check things.

**Static types.** `ty` runs over TTSIM and GETTSIM in CI.

**Runtime types (GEP 9, June 2026).** A package-wide beartype claw. Every
`@policy_function`, `@param_function`, `@agg_by_p_id_function`, … now *requires* an
annotation on every argument and on the return value — a missing one is an error at
decoration time, not a wrong number three hours later.

**Curated errors.** A typed exception hierarchy at the user-facing boundaries:
`InputDataError`, `TTTargetsError`, `PolicyFunctionDefinitionError`, …

<br/>

<div class="highlight">

When GETTSIM shouts at you this week, that is the point. It is much harder to get a
silently wrong number than it was two years ago.

</div>

---

# 2026 — Correctness (II): Units

**GEP 10, accepted July 2026, shipped in v1.3.** Units are attached to functions,
parameters, inputs, rounding rules, and results — built on
[Pint](https://pint.readthedocs.io).

A `float` column can be wealth, monthly earnings, annual earnings, a share, or square
metres. Python is happy to add any of them together. TTSIM is not:

- **€/month vs €/year** — adding a monthly to an annual amount is rejected
- **level** — a household total combined with a Bedarfsgemeinschaft total is rejected
- **currency** — every regime is computed in the currency of its own statute; DM stays DM

The check runs when the policy environment is assembled, by evaluating the formulas with
unit-carrying test values.

It does *not* tell you that your formula matches the law. It tells you the arithmetic is
not nonsense.

---

# 2026 — Substance: SGB XII

**Grundsicherung im Alter (Kapitel 4, SGB XII), rewritten June 2026.**

- **Einsatzgemeinschaft** replaces the Einstandsgemeinschaft

- **gemischte Bedarfsgemeinschaften** (SGB II next to SGB XII) via the Vertikalmethode

- Freibeträge on pension income from *all three pillars*

- Bedarfsanteilmethode for Bürgergeld / ALG 2

- Grundrentenfreibetrag inside the Wohngeld calculation

- Beitragsbemessungsgrenzen and Durchschnittsentgelte back to 1949


---
layout: center
class: text-center
---

# The Interface

### What `main` actually is

---

# One Entry Point

```python
from gettsim import InputData, MainTarget, TTTargets, main

outputs_df = main(
    main_target=MainTarget.results.df_with_mapper,
    policy_date_str="2025-01-01",
    input_data=InputData.df_and_mapper(df=inputs_df, mapper=inputs_map),
    tt_targets=TTTargets(tree=targets_tree),
)
```

There is one function. You tell it **which object you want** (`main_target`) and give it
the **primitives** that object needs.

Behind it sits a second DAG — not the taxes and transfers system, but the pipeline that
builds and runs it. Ask for any node in it and GETTSIM computes exactly what that node
needs, and nothing else.

---
layout: default
---

# The Whole Thing

<iframe src="/interface_dag.html" class="dagframe"></iframe>

`gettsim.plot.dag.interface()` gives you this in your own session

---

# The Spine

<div class="spine">
  <div class="step"><div class="node">policy_date_str</div><div class="gloss">an ISO date — the only thing a policy environment needs</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">policy_environment</div><div class="gloss">the tree of policy functions, parameters and inputs in force on that date</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">specialized_environment</div><div class="gloss">that tree, narrowed to your targets and the shape of your data</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">tt_function</div><div class="gloss">one callable: columns in, columns out</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">raw_results</div><div class="gloss">the columns it returned, internals and all</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">results</div><div class="gloss">purged of internals, in the shape you asked for</div></div>
</div>

Your data joins at `specialized_environment`, as `processed_data`.

---

# Where Your Data Comes In

<div class="spine">
  <div class="step"><div class="node side">input_data.df_and_mapper</div><div class="gloss">a DataFrame plus a tree that maps your column names onto GETTSIM's</div></div>
  <div class="step"><div class="node side">input_data.tree / .flat / .qname</div><div class="gloss">the same data, if you would rather not go through a DataFrame</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">input_data_in_computation_currency</div><div class="gloss">your euros, converted into the statute's currency</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">processed_data</div><div class="gloss">sorted, dtype-canonicalised, ready for the DAG</div></div>
</div>

<br/>

Every shape ends up in the same place. Pick whichever is least work for you.

---

# Inside `specialized_environment`

<div class="spine">
  <div class="step"><div class="node">…with_derived_functions</div><div class="gloss">flatten the tree, then add what can be derived: aggregations to Bedarfsgemeinschaft or Steuernummer level, conversions between month and year — which is why it needs your column names, and therefore your data</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">…with_processed_params…</div><div class="gloss">run the parameter functions; every parameter object becomes a plain number</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">…with_partialled_params…</div><div class="gloss">bake those numbers into the functions — what is left depends only on columns</div></div>
  <p class="down">↓</p>
  <div class="step"><div class="node">tt_dag</div><div class="gloss">the graph of what remains; compile it and you have <code>tt_function</code></div></div>
</div>

<br/>

All four are `MainTarget.specialized_environment.…` — you can ask `main` for any of them.
Useful when a number surprises you and you want to see what the system looked like at
that point.

---

# What You Get For Free

**`MainTarget.`** and let your editor complete. `results`, `templates`,
`policy_environment`, `specialized_environment`, `labels`, `unit_checks`, `input_data`,
`tt_targets`, `rounding`, `backend`, `fail_if`, `warn_if`, …

<br/>

**Ask what data you need**, instead of guessing:

```python
main(
    main_target=MainTarget.templates.input_data_dtypes.tree,
    tt_targets=TTTargets.tree(TARGETS),
    policy_date_str="2025-01-01",
)
```

<br/>

**Ask for the policy environment**, modify it, hand it back. That is Stage 1 this
afternoon — and it is why the reform you write today still works tomorrow on personas and
on the SOEP.

---


# Two Years

- The engine is separate.

- The law is a tree you can read and change.

- The machine checks your types, your units, and your data.


### Now go break it.
