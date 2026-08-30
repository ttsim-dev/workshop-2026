"""Check that the workshop environment is ready.

Run with `pixi run verify`. Prints one line per check and exits non-zero on failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBMODULES = ("ttsim", "gettsim", "gettsim-personas", "soep-preparation")


def main() -> int:
    problems: list[str] = []

    for name in SUBMODULES:
        if not (ROOT / name / "pyproject.toml").exists():
            problems.append(
                f"Submodule '{name}' is empty. Run:\n"
                f"    git submodule update --init --recursive"
            )
    if problems:
        for problem in problems:
            print(f"FAIL  {problem}")
        return 1

    import gettsim
    import gettsim_personas  # noqa: F401
    import soep_preparation  # noqa: F401

    print(f"OK    gettsim {gettsim.__version__}")

    from gettsim import MainTarget, main

    main(main_target=MainTarget.policy_environment, policy_date_str="2023-07-01")
    print("OK    policy environment for 2023-07-01 builds")

    from gettsim_personas import grundsicherung_für_erwerbsfähige

    grundsicherung_für_erwerbsfähige.Couple1Child(policy_date_str="2023-07-01")
    print("OK    personas available")

    from soep_preparation.config import DATA_ROOT, SOEP_VERSION, SRC
    from soep_preparation.utilities.general import get_script_names

    # soep-preparation reads one raw .dta per cleaning module, named after it.
    # Whatever else the directory holds is not used, so do not look at it.
    soep_data = DATA_ROOT / SOEP_VERSION
    location = soep_data.relative_to(ROOT)
    modules = sorted(get_script_names(SRC / "clean_modules"))
    missing = [name for name in modules if not (soep_data / f"{name}.dta").exists()]
    if not missing:
        print(
            f"OK    SOEP-Core {SOEP_VERSION} raw files found for every cleaning module"
        )
    elif len(missing) == len(modules):
        print(
            f"NOTE  no SOEP-Core {SOEP_VERSION} raw files in {location}/ yet.\n"
            "      Needed for Friday's session only."
        )
    else:
        listed = "\n".join(f"        {name}.dta" for name in missing)
        print(
            f"NOTE  {location}/ has no raw file for these cleaning "
            f"modules:\n{listed}\n"
            "      Needed for Friday's session only."
        )

    print("\nYou are set up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
