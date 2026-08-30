# GETTSIM Workshop 2026 — hands-on material

Bonn, 3–4 September 2026.

## Setup

If possible, do the following **before** the workshop. It will save us a lot of time.

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
   into `soep-preparation/data/V41/`.

4. Check that it worked:

   ```console
   $ pixi run verify
   ```

If anything fails, do not spend your evening on it, we will help you at the workshop.
