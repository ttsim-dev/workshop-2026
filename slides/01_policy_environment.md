---
theme: academic
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  GETTSIM Workshop 2026 — Stage 1, the policy environment
drawings:
  persist: false
transition: fade
title: Stage 1 — The Policy Environment
mdc: true
defaults:
  layout: center
---

# Stage 1 — The Policy Environment

### Change the law, watch the number move

Marvin Immesberger

---

# Where You Are

<div class="pipeline">
  <div class="stage on">
    <div class="box">gettsim</div>
    <div class="what">the law</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage">
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

GETTSIM is the German tax and transfer system as executable code — every parameter and
every rule, dated.

Today you find your topic in it, and then you change it.

---

# One Function

Everything goes through `main`. You tell it what you want back.

```python
from gettsim import MainTarget, main

main(main_target=MainTarget.policy_environment, ...)              # the law
main(main_target=MainTarget.templates.input_data_dtypes.tree, ...) # what do I need?
main(main_target=MainTarget.results.df_with_nested_columns, ...)   # numbers
```

<br/>

The rest of the arguments say **when**, **on whom**, and **what to compute**:

```python
policy_date_str="2023-07-01"          # or policy_environment=<your reform>
input_data=InputData.tree(...)        # the households
tt_targets=TTTargets.tree(...)        # the quantities you want
```

---

# The Policy Environment Is a Tree

A nested dictionary: namespaces, and inside them **parameters** and **functions**.

```python
status_quo = main(
    main_target=MainTarget.policy_environment,
    policy_date_str="2023-07-01",
)

sorted(status_quo)                # every namespace — find yours here
sorted(status_quo["bürgergeld"])  # its parameters and functions
```

<br/>

<div class="text-gray-500">

The namespaces mirror the directories under `gettsim/src/gettsim/germany/`.
If you can find the folder, you can find the namespace.

</div>

---

# Changing a Parameter

Three steps. Copy, build the new object, put it back.

```python
reform = copy_environment(status_quo)

reform["bürgergeld"]["parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg"] = (
    PiecewisePolynomialParam(
        value=get_piecewise_parameters(
            func_type="piecewise_linear",
            parameter_list=[
                {"interval": "[100, 520)", "slope": 0.2},
                {"interval": "[520, 1000)", "slope": 0.15},   # was 0.3
                ...
            ],
            leaf_name="parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg",
            xnp=np,
        ),
    )
)
```

Then hand it to `main` as `policy_environment=reform`.

---

# Your Parameter Has a Shape

| class | shape |
|---|---|
| `ScalarParam` | a single number |
| `DictParam` | a flat dictionary |
| `ConsecutiveIntLookupTableParam` | a lookup keyed by consecutive integers |
| `PiecewisePolynomialParam` | a schedule on the real line |
| `RawParam` | anything else, processed by a `ParamFunction` |

<br/>

Check yours with `type(...)`, then follow the matching section of

`gettsim/docs/how_to_guides/modifications_of_policy_environments.ipynb`

— it has a worked example of each.

---

# When a Reform Is Not a Number

Write a replacement function, give it **the same name** as the one it replaces, and
copy the original's signature and date range.

```python
@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anrechnungsfreies_einkommen_m(
    einnahmen__bruttolohn_m: float,
    familie__anzahl_kinder_bis_17_bg: int,
    parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    ...
```

Arguments are other nodes, addressed by **qname** — a double underscore separates
namespaces. To read the original:

```python
inspect.getsource(status_quo["bürgergeld"]["anrechnungsfreies_einkommen_m"].function)
```

---
layout: default
---

# Task

**Until 14:45 — the status quo**

1. `cp notebooks/01_policy_environment.ipynb notebooks/01_<yourgroup>.ipynb`
2. Find your namespace in `sorted(status_quo)`. Print its parameters and functions.
3. Which leaf is your reform? Read it. `type()` it.
4. Get **one status-quo number** out: pick a persona, run `main`.

<br/>

**15:30–16:30 — the reform**

5. `copy_environment`, change the leaf, run again. A different number is enough.
6. Keep both environments around. Tomorrow picks them up.

<br/>

<div class="text-gray-500">Stuck for more than ten minutes? Hand up.</div>

