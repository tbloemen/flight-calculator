import pendulum
import subprocess
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


def create_pdf(advices: list[Advice]) -> None:
    md_file = convert_advices_to_md(advices)
    pdf_file = convert_md_to_pdf(md_file)
    print("The report has been generated:", pdf_file)
