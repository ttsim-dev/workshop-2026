# Slides

Five Slidev decks, one per presentation slot.

| file | slot |
|---|---|
| `hmg.md` | Thu · Two years of GETTSIM, and what `main` is |
| `00_format.md` | Thu 13:30 · Workshop format and group formation |
| `01_policy_environment.md` | Thu 13:45 · Introduction to Stage 1 |
| `02_personas.md` | Fri 09:00 · Introduction to Stage 2 |
| `03_micro_data.md` | Fri 10:35 · Introduction to Stage 3 |

## Running

```console
$ pixi run view-pres 01     # present; the argument is a filename prefix
$ pixi run build-pres 01    # export to slides/01_policy_environment-export.pdf
```

Both depend on `slides-install`, which runs `npm install` in this directory the first
time and is a no-op afterwards. `hmg.md` is a prefix like any other:

```console
$ pixi run view-pres hmg
```

## The interface DAG

`hmg.md` embeds `public/interface_dag.html`, an interactive plotly figure — hover a node
during the talk to see its name and description. It is generated from the pinned GETTSIM
and committed, so the deck runs without a Python environment. Regenerate it with

```console
$ pixi run slides-dag
```

Because it is an iframe, it is live in `view-pres` but blank in the PDF that
`build-pres` produces.
