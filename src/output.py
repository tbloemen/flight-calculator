import json
import subprocess
from dataclasses import asdict
from pathlib import Path

import markdown
import pendulum
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from .analysis import Advice
from .util import get_template_dir


def convert_md_to_pdf(input_file: str, output_file: str = "output.pdf") -> str:
    with open(input_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert markdown to HTML and wrap in full HTML doc
    html_body = markdown.markdown(md_text, extensions=["tables"])

    html_text = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: "DejaVu Sans", "Noto Sans", sans-serif;
            margin: 2em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            word-wrap: normal;
        }}
        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em 0;
        }}
        @page {{
            size: Letter;
            margin: 0in 0.44in 0.2in 0.44in;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""

    HTML(string=html_text, base_url=Path(input_file).parent).write_pdf(output_file)
    return output_file


def convert_advices_to_md(advices: list[Advice]) -> str:
    template_dir = get_template_dir()
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.md")
    filename = "test.md"

    content = template.render(
        advices=advices,
        date=pendulum.now().to_formatted_date_string(),
    )

    with open(filename, mode="w", encoding="utf-8") as output:
        output.write(content)
    return filename


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
        ["typst", "compile", template_dir + "/report.typ", "output.pdf"], check=True
    )

    # delete temp files
    Path(template_dir).joinpath("advices.json").unlink()
    for advice in advices:
        Path(template_dir).joinpath(advice.pareto_path).unlink()


def remove_build_files(md_file: str, plot_paths: list[str]) -> None:
    # remove md file
    Path.cwd().joinpath(md_file).unlink()
    # remove plot paths
    for path in plot_paths:
        Path.cwd().joinpath(path).unlink()


def create_pdf(advices: list[Advice]) -> None:
    md_file = convert_advices_to_md(advices)
    pdf_file = convert_md_to_pdf(md_file)
    print("Deleting build files...")
    plot_paths = [advice.pareto_path for advice in advices]
    remove_build_files(md_file, plot_paths)
    print("The report has been generated:", pdf_file)
