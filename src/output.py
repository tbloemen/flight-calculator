import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pendulum

from .analysis import Advice
from .util import get_template_dir


def get_typst_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "bin", "typst.exe")
    return "typst"


def convert_advices_to_typst_pdf(advices: list[Advice]) -> None:
    template_dir = get_template_dir()
    advices_json = [asdict(advice) for advice in advices]
    with open(template_dir + "/advices.json", "w") as outfile:
        json.dump(
            advices_json,
            outfile,
            indent=4,
            default=lambda o: o.isoformat() if isinstance(o, pendulum.Date) else str(o),
        )
    subprocess.run(
        [get_typst_path(), "compile", template_dir + "/report.typ", "output.pdf"],
        check=True,
    )

    # delete temp files
    Path(template_dir).joinpath("advices.json").unlink()
    for advice in advices:
        Path(template_dir).joinpath(advice.pareto_path).unlink()
