# Slides

Four Slidev decks, one per presentation slot.

| file | slot |
|---|---|
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
time and is a no-op afterwards.
