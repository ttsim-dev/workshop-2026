# GETTSIM Workshop 2026 — hands-on material

Bonn, 3–4 September 2026.

The workshop material (notebooks and briefs) lands here shortly before the workshop.
This branch carries the pinned environment so you can install everything ahead of time.

You do not need to know GETTSIM. We start from zero on Thursday afternoon.

## Setup

Please do this **before you travel**. It takes about half an hour, most of it waiting.

1. Install [pixi](https://pixi.sh/latest/#installation).

2. Clone this repository **with its submodules**:

   ```console
   $ git clone --recurse-submodules https://github.com/ttsim-dev/workshop-2026.git
   $ cd workshop-2026
   $ pixi install
   ```

   If you already cloned without `--recurse-submodules`:

   ```console
   $ git submodule update --init --recursive
   ```

3. Add your SOEP data. Friday morning uses **SOEP-Core v41**. Copy the raw `.dta` files
   into `soep-preparation/data/V41/`. The pipeline expects them flat in that one
   directory, so if your download splits them into subdirectories, flatten it.

4. Check that it worked:

   ```console
   $ pixi run verify
   ```

If anything fails, do not spend your evening on it — come to the setup desk during
registration and lunch on Thursday from 12:00.

## Running

Use your favorite IDE or run:

```console
$ pixi run jupyter
```

## What is pinned

`ttsim`, `gettsim`, `gettsim-personas` and `soep-preparation` are git submodules pinned
to the commits the notebooks were tested against, installed editable. The source is in
your working tree: read it, grep it, change it.


## Layout

```
notebooks/     the three sessions
slides/        the four presentations (Slidev; see slides/README.md)
src/           workshop_soep.py — assembles SOEP into GETTSIM inputs
scripts/       setup verification
```
