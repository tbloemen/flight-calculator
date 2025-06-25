import subprocess
from pathlib import Path

import pendulum
from jinja2 import Environment, FileSystemLoader

from .analysis import Advice


def convert_md_to_pdf(input_file: str, output_file: str = "output.pdf") -> str:
    try:
        subprocess.run(
            [
                "pandoc",
                input_file,
                "-o",
                output_file,
                "--pdf-engine=tectonic",
                "-V",
                "geometry:margin=2cm",
            ]
        )
    except subprocess.CalledProcessError as e:
        print("Error during pdf creation:", e)
    finally:
        return output_file


def convert_advices_to_md(advices: list[Advice]) -> str:
    env = Environment(loader=FileSystemLoader("src/templates/"))
    template = env.get_template("report.md")
    filename = "test.md"

    content = template.render(
        advices=advices,
        date=pendulum.now().to_formatted_date_string(),
    )

    with open(filename, mode="w", encoding="utf-8") as output:
        output.write(content)
    return filename


def remove_build_files(md_file: str, plot_paths: list[Path]) -> None:
    # remove md file
    Path.cwd().joinpath(md_file).unlink()
    # remove plot paths
    for path in plot_paths:
        path.unlink()


def create_pdf(advices: list[Advice]) -> None:
    md_file = convert_advices_to_md(advices)
    pdf_file = convert_md_to_pdf(md_file)
    print("Deleting build files...")
    plot_paths = [advice.pareto_path for advice in advices]
    remove_build_files(md_file, plot_paths)
    print("The report has been generated:", pdf_file)
