import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _nb import code, md, write

cells = [
    md("""
# Stage 3 — Micro data

**Friday, 10:50–11:55.**

The same reform, now on SOEP. This notebook is about the pipeline: how prepared survey
data becomes GETTSIM input, what is missing, and how you close the gap.
"""),
    code("""
import sys

sys.path.insert(0, "../src")

import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from gettsim import InputData, MainTarget, TTTargets, copy_environment, main
from gettsim.tt import PiecewisePolynomialParam, TTSIMUnit, get_piecewise_parameters
from soep_preparation.config import BLD

import workshop_soep as ws

POLICY_DATE = ws.POLICY_DATE
"""),
    md("""
## 1 · What the pipeline produces

`soep-preparation` reads raw SOEP `.dta` files, casts every variable to a sensible
dtype, turns SOEP missing codes into `pd.NA`, combines variables across modules, and
exposes a metadata catalogue. On top of that sits `gettsim_inputs`, which renames the
variables it can to GETTSIM qnames.
"""),
    code("""
gettsim_inputs = pd.read_feather(BLD / "gettsim_inputs" / "gettsim_inputs.arrow")
gettsim_inputs.shape
"""),
    code("""
list(gettsim_inputs.columns)
"""),
    md("""
### The mapping report

The interesting list is the second one: GETTSIM inputs with no SOEP source.
"""),
    code("""
report = json.loads(
    (BLD / "gettsim_inputs" / "mapping_report.json").read_text(encoding="utf-8")
)["union"]

print(f"GETTSIM inputs in the mapping: {report['n_inputs_total']}")
print(f"  with a SOEP source:          {report['n_inputs_mapped']}")
print(f"  without:                     {report['n_inputs_unmapped']}")
"""),
    code("""
report["unmapped"][:20]
"""),
    md("""
## 2 · Closing the gap: two trees

Everything GETTSIM needs is assembled from two explicit trees, both keyed by qname:

- **`from_data`** — inputs that come from SOEP. Some are mapped straight through by the
  pipeline; the rest are derived in `src/workshop_soep.py` from SOEP variables the
  pipeline cleans but does not map.
- **`ASSUMED`** — inputs SOEP does not observe, each a constant with its justification.

They are merged just before the call to `main`. Nothing is hidden.
"""),
    code("""
ws.assumptions_table()
"""),
    md("""
The derivations in `from_data` are the other half. Open `src/workshop_soep.py` to see
them — they are ordinary pandas, and they are candidates for upstreaming into
`soep-preparation`'s own mapping, which is where they belong long term.
"""),
    md("""
---

## TODO 1 — Your reform's inputs

*Which inputs does your reform touch? Are they in the mapped list, derived in
`workshop_soep`, or in `ASSUMED`? For any that are assumed, decide what you want to
assume instead.*
"""),
    code("""
# your code here
"""),
    md("""
---

## 3 · The sample

We work on the **2023** interview under **1 July 2023** law.

SOEP surveys wealth only in 2002, 2007, 2012 and 2017, so the Vermögensprüfung cannot
run on observed data for 2023. It runs instead on `soep-preparation`'s wealth
imputation, which projects household net wealth to 2022 and releases five projection
replicates; `workshop_soep` uses the first. The household total is split equally across
household members, because GETTSIM's `vermögen` is an individual input that it sums over
the Bedarfsgemeinschaft.

`load_soep` keeps people with a valid interview in that year. Without that restriction
the frame carries everyone ever observed, whose inputs then get filled with zeros.
"""),
    code("""
soep = ws.load_soep()
print(f"{len(soep):,} people in {soep['hh_id'].nunique():,} households")
soep[["p_id", "hh_id", "age", "einnahmen__bruttolohn_m", "haushaltsvermögen"]].head()
"""),
    md("""
The imputation does not reach every household in the sample. The ones it misses get a
wealth of zero, which passes the Vermögensprüfung — so the gap runs in the direction of
too much entitlement, not too little.
"""),
    code("""
ws.wealth_coverage(soep)
"""),
    code("""
input_tree = ws.input_data_tree(soep)
sorted(input_tree)[:12]
"""),
    md("""
## 4 · Running the reform

Same two environments as yesterday.
"""),
    code("""
status_quo = main(main_target=MainTarget.policy_environment, policy_date_str=POLICY_DATE)

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
    code("""
TARGETS = {
    "bürgergeld": {"betrag_m_bg": None},
    "einkommensteuer": {"betrag_m_sn": None},
    "sozialversicherung": {"beiträge_versicherter_m": None},
    "kindergeld": {"betrag_m": None},
    "wohngeld": {"betrag_m_wthh": None},
}


def run(policy_environment):
    result = main(
        main_target=MainTarget.results.df_with_nested_columns,
        policy_date_str=POLICY_DATE,
        policy_environment=policy_environment,
        input_data=InputData.tree(input_tree),
        tt_targets=TTTargets.tree(TARGETS),
        include_warn_nodes=False,
    )
    result.columns = ["__".join(c).strip("_") for c in result.columns]
    return result.reset_index(drop=True)


before = run(status_quo)
after = run(reform)
before.head()
"""),
    md("""
## 5 · Aggregating at the right level

Yesterday the persona was one person, so every aggregation level coincided and we could
add the components directly. On SOEP they do not: a household can hold more than one
Bedarfsgemeinschaft, more than one Steuernummer.

Group-level values are repeated on every member of the group, so summing across people
double-counts. Take one value per group, then sum the groups within the household.
"""),
    code("""
group_ids = main(
    main_target=MainTarget.results.df_with_nested_columns,
    policy_date_str=POLICY_DATE,
    input_data=InputData.tree(input_tree),
    tt_targets=TTTargets.tree({"bg_id": None, "hh_id": None}),
    include_warn_nodes=False,
).reset_index(drop=True)
group_ids.columns = ["__".join(c).strip("_") if isinstance(c, tuple) else c
                     for c in group_ids.columns]
group_ids.head()
"""),
    code("""
def bürgergeld_per_household(result):
    \"\"\"One Bürgergeld amount per Bedarfsgemeinschaft, summed to household level.\"\"\"
    frame = pd.DataFrame(
        {
            "hh_id": group_ids["hh_id"],
            "bg_id": group_ids["bg_id"],
            "bürgergeld_m": result["bürgergeld__betrag_m_bg"],
        }
    )
    per_bg = frame.drop_duplicates(subset=["bg_id"])
    return per_bg.groupby("hh_id")["bürgergeld_m"].sum()


bürgergeld_before = bürgergeld_per_household(before)
bürgergeld_after = bürgergeld_per_household(after)
"""),
    md("""
## 6 · Weighting

SOEP is a sample. Without the household weight, sums describe the sample, not Germany.
"""),
    code("""
weights = (
    soep.drop_duplicates("hh_id")
    .set_index("hh_id")["hh_weighting_factor"]
    .astype("float64")
)

print(f"households represented: {weights.sum():,.0f}")
"""),
    code("""
change = (bürgergeld_after - bürgergeld_before).reindex(weights.index).fillna(0.0)

annual_cost = (change * weights).sum() * 12
print(f"fiscal effect: {annual_cost / 1e9:,.2f} bn € per year")
"""),
    md("""
## 7 · Winners and losers
"""),
    code("""
buckets = pd.cut(
    change,
    bins=[-np.inf, -0.01, 0.01, np.inf],
    labels=["loses", "unchanged", "gains"],
)
shares = weights.groupby(buckets, observed=False).sum() / weights.sum()
shares.map("{:.1%}".format)
"""),
    md("""
## 8 · By income decile
"""),
    code("""
income = pd.DataFrame(
    {
        "hh_id": group_ids["hh_id"],
        "gross_m": input_tree["einnahmen"]["bruttolohn_m"],
    }
).groupby("hh_id")["gross_m"].sum().reindex(weights.index).fillna(0.0)

decile = pd.qcut(income.rank(method="first"), 10, labels=range(1, 11))
by_decile = (
    pd.DataFrame({"change": change, "weight": weights, "decile": decile})
    .groupby("decile", observed=False)
    .apply(lambda g: (g["change"] * g["weight"]).sum() / g["weight"].sum(),
           include_groups=False)
)

fig = go.Figure(
    go.Bar(x=by_decile.index.astype(str), y=by_decile.to_numpy(), marker_color="#d62728")
)
fig.update_layout(
    title="Mean change in Bürgergeld by gross-earnings decile",
    xaxis_title="decile of household gross earnings",
    yaxis_title="€ per month",
    template="plotly_white", height=420,
)
fig
"""),
    md("""
---

## TODO 2 — The same three numbers for your reform

*Fiscal effect, winners and losers, and the distribution across deciles.*
"""),
    code("""
# your code here
"""),
    md("""
## TODO 3 — Revisit your assumptions

*Which entries in `ASSUMED` does your answer actually depend on? Change one and rerun.*
"""),
    code("""
# your code here
"""),
]

write(Path(__file__).parent.parent / "notebooks" / "03_micro_data.ipynb", cells)
print("written")
