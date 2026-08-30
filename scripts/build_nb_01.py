import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _nb import code, md, write

cells = [
    md("""
# Stage 1 — The policy environment

**Thursday, 14:00–16:30.**

By the end of this notebook you will have changed German tax-and-transfer law and seen
the number move.

The demo cells run as they are. They use one worked reform throughout: raising the rate
at which earnings between 520 € and 1000 € per month are withdrawn from Bürgergeld. The
cells marked **TODO** are yours — swap in your group's topic.

We work on **1 July 2023**, the date on which the Bürgergeld-Gesetz's new Freibetrag
schedule took effect. Keeping the same policy date across all three notebooks means your
reform travels unchanged from here to the micro data.
"""),
    code("""
import numpy as np
import pandas as pd
import plotly.express as px

from gettsim import (
    InputData,
    MainTarget,
    TTTargets,
    copy_environment,
    main,
)

POLICY_DATE = "2023-07-01"
"""),
    md("""
## 1 · The policy environment

A policy environment is a nested dictionary holding every parameter and every function
GETTSIM needs for a given date. You get one from `main`.
"""),
    code("""
status_quo = main(
    main_target=MainTarget.policy_environment,
    policy_date_str=POLICY_DATE,
)

sorted(status_quo)
"""),
    md("""
Each top-level key is a namespace. `bürgergeld` is the one this notebook works in; find
yours in the list above, or in `gettsim/src/gettsim/germany/`.
"""),
    code("""
sorted(status_quo["bürgergeld"])
"""),
    md("""
Leaves are either **parameters** or **functions**. The parameter we are after describes
how much earned income stays with the household. It is a piecewise linear schedule.
"""),
    code("""
freibetrag = status_quo["bürgergeld"][
    "parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg"
]
type(freibetrag)
"""),
    code("""
freibetrag.value
"""),
    md("""
Read the slopes: between 100 € and 520 € of monthly earnings, 20 % of each additional
euro stays with the household; between 520 € and 1000 €, 30 % does. That middle band is
what the Bürgergeld-Gesetz added.
"""),
    md("""
## 2 · Running GETTSIM once

We need input data. `gettsim-personas` provides ready-made example households; here is a
couple with one child on basic income support.
"""),
    code("""
from gettsim_personas import grundsicherung_für_erwerbsfähige

persona = grundsicherung_für_erwerbsfähige.Couple1Child(policy_date_str=POLICY_DATE)
print(persona.description)
"""),
    code("""
TARGETS = {"bürgergeld": {"betrag_m_bg": None}}

baseline = main(
    main_target=MainTarget.results.df_with_nested_columns,
    policy_date=persona.policy_date,
    input_data=InputData.tree(persona.input_data_tree),
    tt_targets=TTTargets.tree(TARGETS),
    include_warn_nodes=False,
)
baseline
"""),
    md("""
### Which inputs does a target need?

Ask GETTSIM rather than guessing. `templates.input_data_dtypes.tree` returns the inputs
required to reach your targets — useful when you move to your own data on Friday.
"""),
    code("""
template = main(
    main_target=MainTarget.templates.input_data_dtypes.tree,
    policy_date_str=POLICY_DATE,
    tt_targets=TTTargets.tree(TARGETS),
    include_warn_nodes=False,
)


def qnames(tree, prefix=""):
    for key, value in tree.items():
        path = f"{prefix}__{key}" if prefix else key
        if isinstance(value, dict):
            yield from qnames(value, path)
        else:
            yield path


print(f"{len(list(qnames(template)))} inputs required")
list(qnames(template))[:10]
"""),
    md("""
---

## TODO 1 — Your topic's status quo

*Find the namespace for your group's topic. Print the parameters and functions it
contains. Then get a status-quo number for it: pick a persona, or build an input tree by
hand from the template above.*
"""),
    code("""
# your code here
"""),
    md("""
---

# Part 2 — Implement the reform

## 3 · Changing a parameter

Three steps: copy the environment, build the new parameter object, put it back.
"""),
    code("""
reform = copy_environment(status_quo)
"""),
    md("""
`get_piecewise_parameters` rebuilds a piecewise schedule from a list of intervals. We
halve the retained share on the band the Bürgergeld-Gesetz created, between 520 € and
1000 €, from 30 % to 15 % — a withdrawal rate of 85 % instead of 70 %.
"""),
    code("""
from gettsim.tt import (
    PiecewisePolynomialParam,
    TTSIMUnit,
    get_piecewise_parameters,
)

steeper = PiecewisePolynomialParam(
    value=get_piecewise_parameters(
        func_type="piecewise_linear",
        parameter_list=[
            {"interval": "(-inf, 0)", "intercept": 0, "slope": 0},
            {"interval": "[0, 100)", "slope": 1.0},
            {"interval": "[100, 520)", "slope": 0.2},
            {"interval": "[520, 1000)", "slope": 0.15},  # was 0.3
            {"interval": "[1000, 1200)", "slope": 0.1},
            {"interval": "[1200, inf)", "slope": 0.0},
        ],
        leaf_name="parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg",
        xnp=np,
    ),
    input_unit=TTSIMUnit.EUR.PER_MONTH,
    output_unit=TTSIMUnit.EUR.PER_MONTH,
)

reform["bürgergeld"][
    "parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg"
] = steeper
"""),
    md("""
Pass the modified environment to `main` with `policy_environment=`.
"""),
    code("""
after = main(
    main_target=MainTarget.results.df_with_nested_columns,
    policy_date=persona.policy_date,
    policy_environment=reform,
    input_data=InputData.tree(persona.input_data_tree),
    tt_targets=TTTargets.tree(TARGETS),
    include_warn_nodes=False,
)

pd.DataFrame(
    {
        "status quo": baseline.to_numpy().ravel(),
        "reform": after.to_numpy().ravel(),
    }
)
"""),
    md("""
### The other parameter types

Parameters come in five shapes, and the recipe differs slightly for each:

| class | shape |
|---|---|
| `ScalarParam` | a single number |
| `DictParam` | a flat dictionary |
| `ConsecutiveIntLookupTableParam` | a lookup keyed by consecutive integers |
| `PiecewisePolynomialParam` | a schedule on the real line (used above) |
| `RawParam` | anything else, processed by a `ParamFunction` |

`gettsim/docs/how_to_guides/modifications_of_policy_environments.ipynb` has a worked
example of each. Find out which one your parameter is and follow that section.
"""),
    md("""
## 4 · Changing a function

Some reforms are not a number. GETTSIM picks between two withdrawal schedules depending
on whether children live in the Bedarfsgemeinschaft. Here we make the more generous
schedule apply only from the second child — which needs a new function *and* a new
parameter.

Write the function with `@policy_function`, give it the same name as the one it
replaces, and assign both the function and the new parameter into the environment. Copy
the original's signature and date range — GETTSIM matches on both.
"""),
    code("""
status_quo["bürgergeld"]["anrechnungsfreies_einkommen_m"]
"""),
    code("""
import inspect

print(inspect.getsource(status_quo["bürgergeld"]["anrechnungsfreies_einkommen_m"].function))
"""),
    md("""
Now our replacement. Arguments are other nodes, addressed by qname — a double underscore
separates namespaces.
"""),
    code("""
from types import ModuleType

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    ScalarParam,
    piecewise_polynomial,
    policy_function,
)


@policy_function(
    start_date="2023-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def anrechnungsfreies_einkommen_m(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    familie__anzahl_kinder_bis_17_bg: int,
    parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg: PiecewisePolynomialParamValue,
    parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg: PiecewisePolynomialParamValue,
    min_anzahl_kinder_für_höheren_freibetrag: int,
    xnp: ModuleType,
) -> float:
    \"\"\"Use the with-children schedule only from the nth child onwards.\"\"\"
    erwerbseinkommen_m = (
        einnahmen__bruttolohn_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
    )
    # Call piecewise_polynomial inside each branch rather than selecting the parameter
    # object first: GETTSIM vectorizes these functions, and a branch that returns a
    # parameter object would be vectorized into an array of them.
    if familie__anzahl_kinder_bis_17_bg >= min_anzahl_kinder_für_höheren_freibetrag:
        out = piecewise_polynomial(
            x=erwerbseinkommen_m,
            parameters=parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg,
            xnp=xnp,
        )
    else:
        out = piecewise_polynomial(
            x=erwerbseinkommen_m,
            parameters=parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg,
            xnp=xnp,
        )
    return out


reform_zweites_kind = copy_environment(status_quo)
reform_zweites_kind["bürgergeld"]["anrechnungsfreies_einkommen_m"] = (
    anrechnungsfreies_einkommen_m
)
reform_zweites_kind["bürgergeld"][
    "min_anzahl_kinder_für_höheren_freibetrag"
] = ScalarParam(value=2, unit=TTSIMUnit.COUNT.PER_BG)
"""),
    code("""
main(
    main_target=MainTarget.results.df_with_nested_columns,
    policy_date=persona.policy_date,
    policy_environment=reform_zweites_kind,
    input_data=InputData.tree(persona.input_data_tree),
    tt_targets=TTTargets.tree(TARGETS),
    include_warn_nodes=False,
)
"""),
    md("""
---

## TODO 2 — Implement your reform

*Parameter change, function override, or a node that does not exist yet — whatever your
topic needs. Keep the status-quo environment around; it is your control.*
"""),
    code("""
# your code here
"""),
    md("""
## TODO 3 — Compare against the status quo

*Run both environments on the same persona and look at the difference. A different
number is enough for today.*
"""),
    code("""
# your code here
"""),
    md("""
---

Keep `status_quo` and your reform environment: Stage 2 picks them up tomorrow morning.
"""),
]

write(Path(__file__).parent.parent / "notebooks" / "01_policy_environment.ipynb", cells)
print("written")
