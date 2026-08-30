import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _nb import code, md, write

cells = [
    md("""
# Stage 2 — Musterhaushalte

**Friday, 09:15–10:20.**

Yesterday you changed the law and watched one number move. Today you vary a household
along a dimension and watch the whole budget constraint move.

Same reform as yesterday: a steeper withdrawal of earnings between 520 € and 1000 € per
month from Bürgergeld. Same policy date, 1 July 2023.
"""),
    code("""
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from gettsim import InputData, MainTarget, TTTargets, copy_environment, main
from gettsim.tt import (
    PiecewisePolynomialParam,
    TTSIMUnit,
    get_piecewise_parameters,
)
from gettsim_personas import grundsicherung_für_erwerbsfähige

POLICY_DATE = "2023-07-01"
"""),
    md("""
## 1 · Rebuild the two policy environments

Same three steps as yesterday, in one cell. Substitute your own reform here.
"""),
    code("""
status_quo = main(
    main_target=MainTarget.policy_environment,
    policy_date_str=POLICY_DATE,
)

reform = copy_environment(status_quo)
reform["bürgergeld"][
    "parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg"
] = PiecewisePolynomialParam(
    value=get_piecewise_parameters(
        func_type="piecewise_linear",
        parameter_list=[
            {"interval": "(-inf, 0)", "intercept": 0, "slope": 0},
            {"interval": "[0, 100)", "slope": 1.0},
            {"interval": "[100, 520)", "slope": 0.2},
            {"interval": "[520, 1000)", "slope": 0.15},
            {"interval": "[1000, 1200)", "slope": 0.1},
            {"interval": "[1200, inf)", "slope": 0.0},
        ],
        leaf_name="parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg",
        xnp=np,
    ),
    input_unit=TTSIMUnit.EUR.PER_MONTH,
    output_unit=TTSIMUnit.EUR.PER_MONTH,
)
"""),
    md("""
## 2 · What a persona is

A `Persona` is a household structure, input data, tax-transfer targets and a policy date
— all four ready to hand to `main`.
"""),
    code("""
persona = grundsicherung_für_erwerbsfähige.SingleAdult(policy_date_str=POLICY_DATE)
print(persona.description)
"""),
    code("""
persona.tt_targets_tree
"""),
    md("""
Which personas exist:

| module | personas |
|---|---|
| `einkommensteuer_sozialabgaben` | `Couple1Child` |
| `gesetzliche_altersrente` | `SingleWithFixedPublicPension`, `CoupleWithFixedPublicPension` |
| `grundsicherung_für_erwerbsfähige` | `SingleAdult`, `Single1Child`, `CoupleNoChildren`, `Couple1Child`, `Couple2Children`, `Couple1ChildInKarenzzeit` |
| `grundsicherung_im_alter` | `SingleNoChild`, `Single1Child`, `CoupleNoChild`, `Couple1Child` |

That is a short list. If none fits your topic, writing one is a legitimate use of this
session — the classes in `gettsim-personas/src/gettsim_personas/` are the template.
"""),
    md("""
## 3 · Varying earnings

`LinspaceGrid` sweeps `bruttolohn_m` for one or more `p_id`s. Everything else in the
household stays put.
"""),
    code("""
Single = grundsicherung_für_erwerbsfähige.SingleAdult

swept = Single(
    policy_date_str=POLICY_DATE,
    bruttolohn_m_linspace_grid=Single.LinspaceGrid(
        p0=Single.LinspaceRange(bottom=0, top=2_000),
        n_points=201,
    ),
)

swept.input_data_tree["einnahmen"]["bruttolohn_m"][:8]
"""),
    md("""
To vary anything other than `bruttolohn_m` — rent, age, number of children — use
`upsert_input_data` instead:

```python
persona.upsert_input_data(
    input_data_to_upsert={"wohnen": {"bruttokaltmiete_m_hh": np.linspace(300, 1200, 91)}}
)
```

**Order matters.** GETTSIM uses positions in the input arrays to represent household
relationships. For a three-person household, `[0, 0, 4000]` and `[4000, 0, 0]` describe
completely different households. Check the structure before you overwrite anything.
"""),
    md("""
## 4 · Running the grid under both environments

Nothing here is hidden in a helper — this is the loop, written out.
"""),
    code("""
TARGETS = {
    "einnahmen": {"bruttolohn_m": None},
    "bürgergeld": {"betrag_m_bg": None},
    "einkommensteuer": {"betrag_m_sn": None},
    "solidaritätszuschlag": {"betrag_m_sn": None},
    "sozialversicherung": {"beiträge_versicherter_m": None},
    "kindergeld": {"betrag_m": None},
    "kinderzuschlag": {"betrag_m_bg": None},
    "wohngeld": {"betrag_m_wthh": None},
}


def run(policy_environment, persona):
    \"\"\"Run one persona under one policy environment; return a flat DataFrame.\"\"\"
    result = main(
        main_target=MainTarget.results.df_with_nested_columns,
        policy_date=persona.policy_date,
        policy_environment=policy_environment,
        input_data=InputData.tree(persona.input_data_tree),
        tt_targets=TTTargets.tree(TARGETS),
        include_warn_nodes=False,
    )
    result.columns = ["__".join(c).strip("_") for c in result.columns]
    return result.reset_index()


before = run(status_quo, swept)
after = run(reform, swept)
before.head()
"""),
    md("""
### Disposable income

GETTSIM has no single `disposable income` node, so we build it — and this is where you
have to be careful about **aggregation levels**. Every GETTSIM quantity is computed at
the level the law defines it on, and the suffix says which:

| suffix | level |
|---|---|
| *(none)* | the individual |
| `_bg` | Bedarfsgemeinschaft — the SGB II needs unit |
| `_sn` | Steuernummer — jointly assessed spouses |
| `_wthh` | wohngeldrechtlicher Teilhaushalt |
| `_hh` | household |

Group-level values are repeated on every member of the group, so summing them naively
across people double-counts. Here the persona is a single adult, so all five levels
coincide and we can add them directly. On real data they do not — Friday's third
notebook aggregates each component at its own level.
"""),
    code("""
def disposable_income(df):
    \"\"\"Monthly disposable income. Valid only where HH = BG = SN = WTHH.\"\"\"
    return (
        df["einnahmen__bruttolohn_m"]
        - df["einkommensteuer__betrag_m_sn"]
        - df["solidaritätszuschlag__betrag_m_sn"]
        - df["sozialversicherung__beiträge_versicherter_m"]
        + df["bürgergeld__betrag_m_bg"]
        + df["kindergeld__betrag_m"]
        + df["kinderzuschlag__betrag_m_bg"]
        + df["wohngeld__betrag_m_wthh"]
    )


budget = pd.DataFrame(
    {
        "gross earnings": before["einnahmen__bruttolohn_m"],
        "status quo": disposable_income(before),
        "reform": disposable_income(after),
    }
)
budget.head()
"""),
    md("""
## 5 · The budget constraint
"""),
    code("""
fig = go.Figure()
for name, colour in [("status quo", "#1f77b4"), ("reform", "#d62728")]:
    fig.add_scatter(
        x=budget["gross earnings"], y=budget[name], name=name,
        mode="lines", line={"color": colour, "width": 2},
    )
fig.add_scatter(
    x=budget["gross earnings"], y=budget["gross earnings"],
    name="45°", mode="lines", line={"dash": "dot", "color": "#999", "width": 1},
)
fig.update_layout(
    title="Budget constraint, single adult, 2023",
    xaxis_title="gross earnings, € per month",
    yaxis_title="disposable income, € per month",
    template="plotly_white", height=460,
)
fig
"""),
    md("""
### The kinks

A kink is where the slope changes — where one more euro earned is retained at a
different rate. Differencing the budget constraint shows them directly.
"""),
    code("""
step = budget["gross earnings"].diff()
marginal = pd.DataFrame(
    {
        "gross earnings": budget["gross earnings"],
        "status quo": budget["status quo"].diff() / step,
        "reform": budget["reform"].diff() / step,
    }
)

fig = go.Figure()
for name, colour in [("status quo", "#1f77b4"), ("reform", "#d62728")]:
    fig.add_scatter(
        x=marginal["gross earnings"], y=marginal[name], name=name,
        mode="lines", line={"color": colour, "width": 2, "shape": "hv"},
    )
fig.update_layout(
    title="Marginal retention rate",
    xaxis_title="gross earnings, € per month",
    yaxis_title="Δ disposable income / Δ gross earnings",
    template="plotly_white", height=420,
)
fig
"""),
    md("""
---

## TODO 1 — Choose your dimension

*Which dimension does your reform actually vary along? Earnings is the default;
rent, age, number of children or pension income may be the right one. Use
`LinspaceGrid` for `bruttolohn_m` and `upsert_input_data` for anything else.*
"""),
    code("""
# your code here
"""),
    md("""
## TODO 2 — Status quo against reform

*Run your grid under both environments and plot them on one axis.*
"""),
    code("""
# your code here
"""),
    md("""
## TODO 3 — Where are the kinks?

*Did your reform move them, create them, or remove them? Write the answer down — you
will want it in an hour.*
"""),
    code("""
# your answer here
"""),
]

write(Path(__file__).parent.parent / "notebooks" / "02_personas.ipynb", cells)
print("written")
