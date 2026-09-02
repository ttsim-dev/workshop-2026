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

The toolchain is deliberately **outside pixi**: adding `nodejs` would re-solve
`pixi.lock`, which participants have already installed against.

```console
$ cd slides
$ npm install
$ npm run 00      # or 01, 02, 03 — each on its own port
```

Export a PDF:

```console
$ npx slidev export 00_format.md --output 00_format.pdf
```
