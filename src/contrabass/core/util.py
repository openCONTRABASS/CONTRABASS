import os, json
from jinja2 import Environment, FileSystemLoader, Template

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

# imports on release
from contrabass.core.CobraMetabolicModel import CobraMetabolicModel
from contrabass.core.templates import html


def read_model(model_path, objective=None, processes=None):
    model = CobraMetabolicModel(model_path)
    if objective is not None:
        model.set_objective(objective)
    if processes is not None:
        model.processes = processes
    return model


def write_file(path, string):
    text_file = open(path, "w")
    n = text_file.write(string)
    text_file.close()


def read_file(path):
    with open(path, "r") as file:
        data = file.read()
        return data


def generate_html_template(data, template_name, default=None):
    # file_loader = FileSystemLoader(searchpath="./")
    # env = Environment(loader=file_loader)
    # template = env.get_template('template.html')

    html_template = pkg_resources.read_text(html, template_name)

    """
    jinja2 is giving error:
        jinja2.exceptions.TemplateSyntaxError: unexpected char '\\' at 280624
    on angular produced template in the script section
    The following quickfix is implemented as solution: 
        scripts are replaced and then restored after template is parsed.
    """
    START_SCRIPT_HTML = "<script"
    END_SCRIPT_HTML = "</script>"
    script_sections = []
    for i in range(0, 3):
        script_start = html_template.find(START_SCRIPT_HTML)
        script_end = html_template.find(END_SCRIPT_HTML)
        script_section = html_template[script_start : script_end + len(END_SCRIPT_HTML)]
        script_sections.append(script_section)
        no_script_template = (
            html_template[:script_start]
            + "{{ script_"
            + str(i)
            + " }}"
            + html_template[script_end + len(END_SCRIPT_HTML) :]
        )
        html_template = no_script_template

    # include vars placeholder
    script_start = no_script_template.find("{{ script_0 }}")
    no_script_template = (
        no_script_template[:script_start]
        + "<script>window.data = {{ results }};</script>"
        + no_script_template[script_start:]
    )

    # Uncomment me to get test data json string
    # print(json.dumps(data, default=default).replace("NaN", "\"NaN\""))

    template = Template(no_script_template)
    output = template.render(
        results=json.dumps(data, default=default).replace("NaN", '"NaN"'),
        script_0=script_sections[0],
        script_1=script_sections[1],
        script_2=script_sections[2],
    )

    return output
