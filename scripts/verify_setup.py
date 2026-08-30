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

    soep_data = ROOT / "soep-preparation" / "data" / "V41"
    n_dta = len(list(soep_data.glob("*.dta"))) if soep_data.is_dir() else 0
    if n_dta:
        print(f"OK    SOEP-Core v41 raw files found ({n_dta} .dta)")
    else:
        print(
            f"NOTE  no SOEP-Core v41 files in {soep_data.relative_to(ROOT)}/ yet.\n"
            "      Needed for Friday's session only."
        )

    print("\nYou are set up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
