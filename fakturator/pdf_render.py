import jinja2
from pathlib import Path

try:
    from weasyprint import HTML, CSS
except ImportError as error1:
    print(error1.__class__.__name__ + ": " + error1)
except OSError as error2:
    print(f"{error2}. \nImport of module weasyprint FAILED")

def get_template(templates_dir, template_file):
    """
    Make enviroment for loading html template by Jinja2 library.
    Then load a html template by this env and return it.
    """
    # basepath = Path(__file__).resolve(strict=True).parent
    # template_path = basepath.joinpath('templates', template_file)
    # create jinja2 enviroment object
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
    # with jinja2 env load a template file
    template = env.get_template(template_file)

    return template


def compile_pdf_from_template(template_file, in_variables):
    """Render a template file and compile it to pdf"""

    basedir = Path(__file__).resolve(strict=True).parents[1]

    build_dir = basedir.joinpath('.build')
    build_dir.mkdir(parents=True, exist_ok=True)

    invoices_dir = basedir.joinpath('invoices')
    invoices_dir.mkdir(parents=True, exist_ok=True)

    templates_dir = basedir / 'templates'

    template = get_template(templates_dir, template_file)
    rendered_template = template.render(**in_variables)

    html_file = in_variables["invoice_number"] + ".html"
    pdf_file = in_variables["invoice_number"] + ".pdf"
    build_out = build_dir.joinpath(html_file)
    pdf_out = invoices_dir.joinpath(pdf_file)
    # html out_file
    with open(build_out, mode="w", encoding="utf-8") as f:
        f.write(rendered_template)
    # WeasyPrint
    try:
        HTML(string=rendered_template).write_pdf(
            pdf_out, stylesheets=[CSS(templates_dir / 'style.css')]
        )
    except OSError as err:
        print(f"{err}: format pdf was not created.")
    except NameError as error:
        print(
            f"{error}: module weasyprint was not imported, format pdf was not created.."
        )