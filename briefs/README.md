# Fallback topic briefs

For groups that have not settled on a topic of their own. Pointers, not recipes — the
scoping is part of the work. Each brief is one page; print four copies of each.

Every topic runs through the same three stages: implement it in the policy environment
(Thursday), look at it on a persona (Friday morning), take it to SOEP (Friday late
morning).

______________________________________________________________________

## A note on the policy date

The demo cells run on **1 July 2023 law**. Set `policy_date_str` to whatever your topic
needs — nothing stops you working on 2025.

Friday's wealth comes from `soep-preparation`'s imputation, which projects household net
wealth to 2022; the notebooks carry it into the 2023 means test unchanged. Move to a
later policy date and the wealth is older still. That matters for the means-tested
topics and not at all for the others.

______________________________________________________________________

## 1 · Grundsicherung im Alter after the Alterssicherungskommission

**The question.** The Alterssicherungskommission's recommendations to the BMAS (June
2026\) propose changes to basic old-age income support under SGB XII. What do they cost,
and who gains?

**The reform.** Pick one concrete recommendation from the report and implement it. Most
of them land in the Freibeträge and Mehrbedarfe, or in how income from a public pension
is counted against the Bedarf.

**Where to look.**

- `gettsim/src/gettsim/germany/grundsicherung/im_alter/freibeträge_und_mehrbedarfe.yaml`
  — the parameters
- `.../im_alter/einkommen.py` — how income is counted against the Bedarf
- `.../im_alter/im_alter.py` — the benefit itself
- `gettsim/docs/tt_explanations/childrens_income_grundsicherung_im_alter.md`

**Start from.** `gettsim_personas.grundsicherung_im_alter.SingleNoChild` or
`CoupleNoChild`.

**Stage 2.** Vary the public pension (`sozialversicherung.rente.altersrente.betrag_m`)
via `upsert_input_data` and watch where the reform bites.

**Stage 3.** Restrict to households above the Regelaltersgrenze. Fiscal cost and the
share lifted above the Bedarf are the two numbers worth having.

**The hard part.** Deciding which recommendation is actually a parameter change and
which needs a new node. Read the report first, choose second.

**Source.**
[Empfehlungen der Rentenkommission, BMAS, Juni 2026](https://www.bmas.de/SharedDocs/Downloads/DE/Soziales/empfehlungen-der-rentenkommission-bmas-juni-2026.pdf?__blob=publicationFile&v=4)

______________________________________________________________________

## 2 · A capital pension and the Nettoersatzrate

**The question.** If part of retirement income came from a funded capital pension rather
than from the public pension, what happens to the net replacement rate?

**The reform.** GETTSIM has no capital pension as such, but it does have the income
slots a funded pension would flow through — see `einnahmen.renten` in the input template
(`geförderte_private_vorsorge_m`, `betriebliche_altersvorsorge_m`, `basisrente_m`). The
work is deciding how a euro shifted out of the public pension arrives, and how it is
taxed and counted against means-tested benefits on the way.

**Where to look.**

- `gettsim/src/gettsim/germany/einnahmen/renten/` — the income slots
- `gettsim/src/gettsim/germany/sozialversicherung/rente/` — Entgeltpunkte and the
  Rentenformel
- `gettsim/docs/tt_explanations/taxation_of_pension_income.md` — the tax treatment,
  which is where the interesting part is

**Start from.** `gettsim_personas.gesetzliche_altersrente.SingleWithFixedPublicPension`.

**Stage 2.** Hold total gross retirement income fixed and shift its composition between
the public pension and the capital pension. The replacement rate you want is net
retirement income over net income while working, so you need both legs.

**Stage 3.** This is a lifecycle question and SOEP is a cross-section, so decide early
what you can actually compute. A cross-sectional distribution of net replacement rates
for recent retirees, status quo versus a counterfactual composition, is a defensible
answer. Say what you assumed.

**The hard part.** Defining the denominator. Agree on it in the first ten minutes.

______________________________________________________________________

## 3 · Familiensplitting instead of Ehegattensplitting

**The question.** Germany splits taxable income between spouses. What changes if it is
split across the family, children included?

**The reform.** Replace the Steuernummer-level splitting with a divisor that counts
children — the French *quotient familial* is the obvious reference point. Decide what
weight a child gets and whether the resulting relief is capped, then implement it.
Whether the Kinderfreibetrag survives alongside it is your call, but make it explicitly.

**Where to look.**

- `gettsim/src/gettsim/germany/einkommensteuer/einkommensteuer.py` — where splitting
  happens
- `.../einkommensteuer/einkommensteuertarif.yaml` — the tariff, a `RawParam`
- `.../einkommensteuer/kinderfreibetrag.py` and `.yaml` — the child allowance you may be
  replacing
- `.../familie/` — the family relationships the divisor has to read
- `gettsim/docs/how_to_guides/modifications_of_policy_environments.ipynb`, section
  "Modifying Column Objects" — the recipe for replacing a `PolicyFunction`

**Start from.** `gettsim_personas.einkommensteuer_sozialabgaben.Couple1Child`.

**Stage 2.** Vary the secondary earner's `bruttolohn_m` with `LinspaceGrid` and compare
the marginal rate schedule under both regimes. The distributional story is in how the
gain varies with the earnings split within the couple.

**Stage 3.** Fiscal cost and winners and losers by household type. Single parents and
couples without children are where the answer gets uncomfortable.

**The hard part.** This is the only fallback that certainly needs a new `PolicyFunction`
rather than a parameter change. It is also the most interesting.
