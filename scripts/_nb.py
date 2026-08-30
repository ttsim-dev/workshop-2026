"""Tiny helper: build an .ipynb from a list of (kind, source) pairs."""

from __future__ import annotations

import json
from pathlib import Path


def md(text: str) -> tuple[str, str]:
    return ("markdown", text.strip("\n"))


def code(text: str) -> tuple[str, str]:
    return ("code", text.strip("\n"))


def write(path: str | Path, cells: list[tuple[str, str]]) -> None:
    nb = {
        "cells": [
            {
                "cell_type": kind,
                "id": f"c{i:03d}",
                "metadata": {},
                "source": src.splitlines(keepends=True),
                **({"outputs": [], "execution_count": None} if kind == "code" else {}),
            }
            for i, (kind, src) in enumerate(cells)
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.14"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    Path(path).write_text(
        json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
