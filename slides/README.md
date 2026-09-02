# Slides

Four Slidev decks, one per presentation slot.

| file | slot |
|---|---|
| `00_format.md` | Thu 13:30 · Workshop format and group formation |
| `01_policy_environment.md` | Thu 13:45 · Introduction to Stage 1 |
| `02_personas.md` | Fri 09:00 · Introduction to Stage 2 |
| `03_micro_data.md` | Fri 10:35 · Introduction to Stage 3 |

`style.css` is shared by all four — Slidev picks it up automatically. The ecosystem
pipeline (`gettsim → gettsim-personas → soep-preparation`) is defined there and appears
on the second slide of each stage deck with the current stage lit.

## Running

```console
$ pixi run view-pres 01     # present; the argument is a filename prefix
$ pixi run build-pres 01    # export to slides/01_policy_environment-export.pdf
$ pixi run view-pres        # no argument: the format deck
```

Both depend on `slides-install`, which runs `npm install` in this directory the first
time and is a no-op afterwards.

Node lives in its own pixi feature (`[tool.pixi.feature.slides]`, environment `slides`)
rather than in the default dependencies. Adding it to the default environment would
re-solve `pixi.lock` for the environment participants already installed against; this
way their `pixi install` is untouched and the lock only gains an environment they never
build.
