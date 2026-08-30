"""Assemble a GETTSIM-ready SOEP dataset for the workshop.

GETTSIM needs ~50 inputs to compute Bürgergeld. The `soep-preparation` pipeline maps 13
of them to SOEP variables. This module closes the gap with two explicit, inspectable
trees:

- `from_data(df)` — inputs that come from SOEP, either mapped straight through by the
  pipeline or derived here from a SOEP variable.
- `ASSUMED` — inputs SOEP does not observe, each a constant with a stated justification.

Both are keyed by GETTSIM qname and merged before being handed to `main`. Nothing is
hidden: `assumptions_table()` prints every assumed input and why.

The derivations here are candidates for upstreaming into `soep-preparation`'s
`gettsim_inputs` mapping, which is where they belong long term.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from soep_preparation.config import BLD, MODULES
from soep_preparation.final_dataset import create_final_dataset

# SOEP variables we pull in addition to what the pipeline already maps to qnames.
_EXTRA_SOEP_VARIABLES = [
    "age",
    "birth_month",
    "federal_state_of_residence",
    "gesetzliche_rente_y",
    "arbeitslosengeld_y",
    "marital_status",
    "in_education",
    "rented_or_owned",
    "number_of_children_living_in_hh",
    "hh_weighting_factor",
]

# GETTSIM nodes we supply directly rather than building their inputs from scratch.
# Every one of these would otherwise pull in a long tail of biographical inputs (pension
# histories, Elterngeld eligibility) that SOEP either does not carry or that would cost
# more assumptions than the node itself is worth.
OVERRIDDEN_NODES = (
    "sozialversicherung__rente__altersrente__betrag_m",
    "sozialversicherung__rente__erwerbsminderung__betrag_m",
    "sozialversicherung__arbeitslosen__betrag_m",
    "elterngeld__betrag_m",
    "unterhaltsvorschuss__betrag_m",
)

# Inputs SOEP does not observe. Value, then why that value is defensible.
ASSUMED: dict[str, tuple[object, str]] = {
    "bürgergeld__bezug_im_vorjahr": (
        True,
        "Decides which Vermögensfreibetrag applies. SOEP does not identify the start "
        "of a Leistungsbezug, and most of the 2023 caseload was already receiving "
        "benefits, so we put everyone past the Karenzzeit: 15 000 € per person rather "
        "than 40 000 € for the first. This is the assumption the Vermögensprüfung is "
        "most sensitive to — flip it and rerun.",
    ),
    "einkommensteuer__abzüge__beitrag_private_rentenversicherung_m": (
        0.0,
        "Riester/Rürup contributions not separable in SOEP.",
    ),
    "einkommensteuer__abzüge__kinderbetreuungskosten_m": (
        0.0,
        "Childcare costs are surveyed irregularly; zero understates deductions.",
    ),
    "einkommensteuer__abzüge__p_id_kinderbetreuungskostenträger": (
        -1,
        "Follows from childcare costs being zero.",
    ),
    "einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y": (
        0.0,
        "Negligible for the working-age population Bürgergeld concerns.",
    ),
    "einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y": (
        0.0,
        "SOEP self-employment income is not split by Einkunftsart; booked as "
        "selbstständige Arbeit instead.",
    ),
    "einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__tatsächliche_werbungskosten_y": (  # noqa: E501
        0.0,
        "Not surveyed; GETTSIM applies the Arbeitnehmerpauschbetrag.",
    ),
    "einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y": (
        0.0,
        "Rental income is surveyed at household level only.",
    ),
    "einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig": (
        False,
        "Affects health-insurance treatment only; rare in the target population.",
    ),
    "einkommensteuer__einkünfte__sonstige__alle_weiteren_y": (
        0.0,
        "Residual category.",
    ),
    "einkommensteuer__einkünfte__sonstige__rente__alter_beginn_leistungsbezug_sonstige_private_vorsorge": (  # noqa: E501
        67,
        "Only binds when private pension income is non-zero, which it is not here.",
    ),
    "einnahmen__kapitalerträge_y": (
        0.0,
        "SOEP capital income is household-level and top-coded; below the "
        "Sparerpauschbetrag for most Bürgergeld households anyway.",
    ),
    "einnahmen__renten__aus_berufsständischen_versicherungen_m": (0.0, "Rare."),
    "einnahmen__renten__basisrente_m": (0.0, "Not separable in SOEP."),
    "einnahmen__renten__betriebliche_altersvorsorge_m": (0.0, "Not separable in SOEP."),
    "einnahmen__renten__geförderte_private_vorsorge_m": (0.0, "Not separable in SOEP."),
    "einnahmen__renten__sonstige_private_vorsorge_m": (0.0, "Not separable in SOEP."),
    "elterngeld__betrag_m": (
        0.0,
        "Overridden node. Elterngeld eligibility needs a birth history and prior net "
        "income; out of scope for a Bürgergeld reform.",
    ),
    "unterhalt__tatsächlich_erhaltener_betrag_m": (
        0.0,
        "Maintenance received is not reliably measured in SOEP.",
    ),
    "unterhaltsvorschuss__betrag_m": (
        0.0,
        "Overridden node. Take-up is not observed.",
    ),
    "kindergeld__in_ausbildung": (
        False,
        "Set from `in_education` for adults; children under 18 do not need it.",
    ),
    "schwerbehindert_grad_g": (
        False,
        "Merkzeichen G is not surveyed; only the Grad der Behinderung is.",
    ),
    "sozialversicherung__kranken__beitrag__privat_versichert": (
        False,
        "Private insurance is rare among Bürgergeld-eligible households.",
    ),
    "sozialversicherung__pflege__beitrag__hat_kinder": (
        True,
        "Avoids the childless surcharge; refine if your reform is sensitive to it.",
    ),
    "sozialversicherung__rente__bezieht_rente": (
        False,
        "Set together with the overridden pension amount.",
    ),
    "sozialversicherung__rente__erwerbsminderung__betrag_m": (
        0.0,
        "Overridden node. Disability pension receipt is not cleanly identified.",
    ),
    "sozialversicherung__rente__grundrente__grundrentenzeiten_monate": (
        0,
        "Grundrente needs a full contribution history.",
    ),
    "sozialversicherung__rente__jahr_renteneintritt": (
        2080,
        "Far future, so no one is treated as retired; consistent with the overridden "
        "pension amount.",
    ),
    "wohngeld__mietstufe_hh": (
        3,
        "SOEP has no Gemeindekennziffer, so the statutory Mietstufe cannot be assigned. "
        "3 is the modal stufe. This one matters — see the Wohnkosten talk.",
    ),
}


def _f(s: pd.Series) -> np.ndarray:
    """Float column, missing values as 0.0."""
    return pd.to_numeric(s, errors="coerce").fillna(0.0).to_numpy(dtype="float64")


def _i(s: pd.Series, fill: int = -1) -> np.ndarray:
    """Integer column, missing values as `fill`."""
    return pd.to_numeric(s, errors="coerce").fillna(fill).to_numpy(dtype="int64")


def _b(s: pd.Series, fill: bool = False) -> np.ndarray:
    """Boolean column, missing values as `fill`."""
    return s.astype("boolean").fillna(fill).to_numpy(dtype="bool")


def _valid_pointer(pointer: np.ndarray, present: np.ndarray) -> np.ndarray:
    """Set pointers to -1 when the person they point at is not in the sample.

    SOEP records a spouse or parent even when that person did not take part in the
    survey year. GETTSIM requires every pointer to resolve to a `p_id` that is present,
    so a dangling pointer becomes "no spouse" / "no parent". This shrinks measured
    Bedarfsgemeinschaften and is one of the places where sample restriction quietly
    changes the answer.
    """
    known = set(present.tolist())
    return np.where(np.isin(pointer, list(known)), pointer, -1).astype("int64")


def _hh_const(values: np.ndarray, hh_id: np.ndarray) -> np.ndarray:
    """Broadcast the first value observed in each household to all its members.

    GETTSIM requires `*_hh` inputs to be constant within `hh_id`. SOEP household
    variables are attached per person and can disagree across members after missing
    values are filled, so we take the first non-missing value each household reports.
    """
    frame = pd.DataFrame({"hh_id": hh_id, "value": values})
    filled = frame.groupby("hh_id")["value"].transform("first")
    return filled.to_numpy(dtype=values.dtype)


def _hh_size(hh_id: np.ndarray) -> np.ndarray:
    """Number of sample members per household, aligned to the person rows."""
    return pd.Series(hh_id).groupby(hh_id).transform("size").to_numpy(dtype="float64")


def _unflatten(flat: dict[str, object]) -> dict:
    """Turn `{'a__b': x}` into `{'a': {'b': x}}`."""
    tree: dict = {}
    for qname, value in flat.items():
        node = tree
        *path, leaf = qname.split("__")
        for part in path:
            node = node.setdefault(part, {})
        node[leaf] = value
    return tree


#: SOEP surveys wealth only in these years. Everything after 2017 has to be imputed,
#: which is what `soep_preparation.wealth_imputation` does.
WEALTH_YEARS = (2002, 2007, 2012, 2017)

SURVEY_YEAR = 2023

#: 1 July 2023, the date the Bürgergeld-Gesetz's new Freibetrag schedule took effect.
#: On 1 January 2023 the `bürgergeld` namespace already exists but still carries the
#: pre-reform schedule inherited from Arbeitslosengeld II, so the July date is the one
#: that shows Bürgergeld as it was actually legislated.
POLICY_DATE = "2023-07-01"

#: Wealth source: the projection replicates rather than
#: `household_wealth_2022_component_only.arrow`. That file reports a per-household
#: median across draws, which is a point estimate for covariate use and mechanically
#: erases the zero and negative mass — exactly the mass a Vermögensprüfung turns on.
#: Each replicate here is one complete predictive draw and keeps it.
_WEALTH_FILE = (
    BLD
    / "wealth_imputation"
    / "household_wealth_2022_component_only_projection_replicates.arrow"
)

#: Component-only, i.e. the six-component net-wealth total without the reconciliation
#: residual. The residual-inclusive file is the more complete total but the pipeline
#: cannot validate it.
_WEALTH_REPLICATE = "component_only_net_wealth_2022_a"

#: The imputation projects 2022 household wealth; the sample is the 2023 interview.
#: Carrying last year's wealth into this year's means test is the standard compromise
#: and is stated rather than hidden.
_WEALTH_YEAR = 2022


def _household_wealth() -> pd.Series:
    """2022 household net wealth from the imputation, indexed by `hh_id`.

    Five projection replicates `a`–`e` are released. We use `a` throughout. Doing this
    properly means running the analysis five times and combining across replicates —
    worth saying out loud if your reform is sensitive to the Vermögensfreibetrag. The
    release is explicitly not Rubin-valid, so the combination rule is not Rubin's.
    """
    frame = pd.read_feather(_WEALTH_FILE)
    return (
        frame.set_index("hh_id")[_WEALTH_REPLICATE]
        .astype("float64")
        .groupby(level=0)
        .first()
    )


def load_soep(survey_year: int = SURVEY_YEAR) -> pd.DataFrame:
    """Load one survey year of pipeline output plus the extra SOEP variables.

    Keeps only people with a valid interview in `survey_year`. Without this the frame
    carries every person ever observed, whose inputs are then silently filled with
    zeros — which makes them look poor rather than absent.
    """
    gettsim_inputs = pd.read_feather(BLD / "gettsim_inputs" / "gettsim_inputs.arrow")
    gettsim_inputs = gettsim_inputs[gettsim_inputs["survey_year"] == survey_year]
    extra = create_final_dataset(
        modules={name: MODULES[name].load() for name in MODULES._entries},  # noqa: SLF001
        variables=_EXTRA_SOEP_VARIABLES,
        survey_years=[survey_year],
    )
    # A few SOEP source modules carry more than one row per person-year, so the merge
    # would multiply rows. Keep the first.
    extra = extra[extra["survey_year"] == survey_year].drop_duplicates(
        subset=["p_id"], keep="first"
    )
    merged = gettsim_inputs.merge(
        extra.drop(columns=["hh_id", "hh_id_original"], errors="ignore"),
        on=["p_id", "survey_year"],
        how="inner",
    )
    merged = merged[merged["age"].notna()]
    # A handful of exact duplicate person-rows survive the merge; GETTSIM requires
    # unique `p_id`s.
    merged = merged.drop_duplicates(subset=["p_id"], keep="first").reset_index(
        drop=True
    )
    # Imputed household wealth, attached per household. The imputation covers about
    # seven in ten of the households in this sample; the rest get 0.0, which passes the
    # Vermögensprüfung. That is the optimistic direction, so say so rather than let it
    # look like measured poverty. `wealth_coverage(df)` reports the actual rate.
    merged["haushaltsvermögen"] = (
        merged["hh_id"].map(_household_wealth()).astype("float64").fillna(0.0)
    )
    return merged


def wealth_coverage(df: pd.DataFrame) -> pd.Series:
    """Share of sample households the wealth imputation actually covers."""
    covered = df.drop_duplicates("hh_id")["hh_id"].isin(_household_wealth().index)
    return pd.Series(
        {
            "households": int(covered.size),
            "with imputed wealth": int(covered.sum()),
            "share": float(covered.mean()),
        }
    )


def from_data(df: pd.DataFrame) -> dict[str, object]:
    """Inputs that come from SOEP: mapped by the pipeline, or derived here."""
    age = pd.to_numeric(df["age"], errors="coerce")
    is_adult = (age >= 18).fillna(False)
    second_parent = _second_parent(df)
    hh_id = _i(df["hh_id"])
    tree: dict[str, object] = {
        # --- Straight from soep-preparation's own GETTSIM mapping -----------------
        "p_id": _i(df["p_id"]),
        "hh_id": _i(df["hh_id"]),
        "geburtsjahr": _i(df["geburtsjahr"], fill=1970),
        "arbeitsstunden_w": _f(df["arbeitsstunden_w"]),
        "behinderungsgrad": _i(df["behinderungsgrad"], fill=0),
        "einnahmen__bruttolohn_m": _f(df["einnahmen__bruttolohn_m"]),
        "einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y": _f(
            df["einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y"]
        ),
        "familie__p_id_ehepartner": _i(df["familie__p_id_ehepartner"]),
        "familie__p_id_elternteil_1": _i(df["familie__p_id_elternteil_1"]),
        "bürgergeld__p_id_einstandspartner": _i(
            df["bürgergeld__p_id_einstandspartner"]
        ),
        "wohnen__bruttokaltmiete_m_hh": _f(df["wohnen__bruttokaltmiete_m_hh"]),
        "wohnen__heizkosten_m_hh": _f(df["wohnen__heizkosten_m_hh"]),
        "wohnen__wohnfläche_hh": _f(df["wohnen__wohnfläche_hh"]),
        # --- Derived here from SOEP variables the pipeline cleans but does not map -
        "alter": _i(age, fill=0),
        # Age in months. SOEP gives the birth month but not the interview date, so the
        # within-year position is approximated by half a year.
        "alter_monate": _i(age * 12 + 6, fill=0),
        # The imputation delivers a household total; GETTSIM's `vermögen` is an
        # individual input that it sums over the Bedarfsgemeinschaft. We split the
        # household total equally across its members, so it adds back up to the
        # household total whenever the household is one Bedarfsgemeinschaft, and
        # splits proportionally when it is more than one. Giving every member the
        # full household amount would multiply the household's wealth by its size.
        "vermögen": _f(df["haushaltsvermögen"]).clip(min=0.0)
        / _hh_size(_i(df["hh_id"])),
        "wohnen__bewohnt_eigentum_hh": _b(
            df["rented_or_owned"].astype("string").str.contains("own", case=False)
        ),
        "wohnort_ost_hh": _b(_is_east(df["federal_state_of_residence"])),
        "einkommensteuer__gemeinsam_veranlagt": _b(
            df["familie__p_id_ehepartner"].notna()
            & (pd.to_numeric(df["familie__p_id_ehepartner"], errors="coerce") >= 0)
        ),
        "familie__alleinerziehend": _b(_is_single_parent(df, second_parent)),
        "familie__p_id_elternteil_2": _i(second_parent),
        "kindergeld__p_id_empfänger": _i(df["familie__p_id_elternteil_1"]),
        "sozialversicherung__rente__altersrente__betrag_m": _f(
            df["gesetzliche_rente_y"]
        )
        / 12,
        "sozialversicherung__arbeitslosen__betrag_m": _f(df["arbeitslosengeld_y"]) / 12,
        "kindergeld__in_ausbildung": _b(
            df["in_education"].astype("boolean").fillna(False) & is_adult
        ),
    }
    present = tree["p_id"]
    for qname in (
        "familie__p_id_ehepartner",
        "familie__p_id_elternteil_1",
        "familie__p_id_elternteil_2",
        "bürgergeld__p_id_einstandspartner",
        "kindergeld__p_id_empfänger",
    ):
        tree[qname] = _valid_pointer(tree[qname], present)
    for qname in (
        "wohnen__bruttokaltmiete_m_hh",
        "wohnen__heizkosten_m_hh",
        "wohnen__wohnfläche_hh",
        "wohnen__bewohnt_eigentum_hh",
        "wohnort_ost_hh",
    ):
        tree[qname] = _hh_const(tree[qname], hh_id)
    return tree


def _is_east(federal_state: pd.Series) -> pd.Series:
    east = {
        "Brandenburg",
        "Mecklenburg-Vorpommern",
        "Sachsen",
        "Sachsen-Anhalt",
        "Thüringen",
        "Berlin",
    }
    return federal_state.astype("string").isin(east).fillna(False)


def _is_single_parent(df: pd.DataFrame, second_parent: pd.Series) -> pd.Series:
    """A parent of a child in the household, with no spouse present."""
    has_child = df["p_id"].isin(
        pd.concat([df["familie__p_id_elternteil_1"], second_parent]).dropna()
    )
    no_spouse = (
        pd.to_numeric(df["familie__p_id_ehepartner"], errors="coerce").fillna(-1) < 0
    )
    return has_child & no_spouse


def _kindergeld_recipient(df: pd.DataFrame) -> pd.Series:
    """Kindergeld goes to the first parent on record; -1 for everyone else."""
    return df["familie__p_id_elternteil_1"].fillna(-1).astype(int)


def assumptions_table() -> pd.DataFrame:
    """Every assumed input, its value, and why."""
    return pd.DataFrame(
        [
            {"gettsim input": q, "assumed value": v, "why": why}
            for q, (v, why) in sorted(ASSUMED.items())
        ]
    )


def input_data_tree(df: pd.DataFrame) -> dict:
    """Merge the data tree and the assumed tree into one GETTSIM input tree."""
    n = len(df)
    flat: dict[str, object] = dict(from_data(df))
    for qname, (value, _why) in ASSUMED.items():
        if qname in flat:
            continue
        flat[qname] = pd.Series(np.repeat(value, n), index=df.index)
    return _unflatten(flat)


def _second_parent(df: pd.DataFrame) -> pd.Series:
    """SOEP gives one parent pointer; take that parent's spouse as the second parent.

    Defensible for married couples, which is the case the Bedarfsgemeinschaft
    logic cares about. Unmarried co-resident parents are missed, so their households
    look like single-parent households to GETTSIM.
    """
    spouse_of = dict(
        zip(df["p_id"], df["familie__p_id_ehepartner"].fillna(-1), strict=True)
    )
    first = df["familie__p_id_elternteil_1"].fillna(-1).astype(int)
    return first.map(lambda pid: spouse_of.get(pid, -1) if pid >= 0 else -1).astype(int)
