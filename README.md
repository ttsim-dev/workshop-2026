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

## What is pinned

`ttsim`, `gettsim`, `gettsim-personas` and `soep-preparation` are git submodules pinned
to the commits the material was tested against, installed editable. The source is in
your working tree: read it, grep it, change it.

The workshop works on **1 July 2023 law**, the date the Bürgergeld-Gesetz's new
Freibetrag schedule took effect. Keeping one policy date across all three sessions means
the same reform travels from the policy environment to the personas to the micro data
unchanged.

SOEP surveys wealth only in 2002, 2007, 2012 and 2017, so Friday's Vermögensprüfung
cannot run on observed wealth. It runs on `soep-preparation`'s wealth imputation, which
projects household net wealth to 2022. That has to be built once, and it takes a while:

```console
$ cd soep-preparation
$ SOEP_WEALTH_IMPUTATION=1 pixi run --manifest-path ../pyproject.toml python -m pytask
```

Friday morning only. Skip it if you are not bringing SOEP data.
