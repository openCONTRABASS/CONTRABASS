from __future__ import absolute_import

import os
import click

from contrabass.cli.utils import (
    validate_input_model,
    validate_output_model,
    validate_output_spread,
    save_final_spreadsheet,
    save_final_model,
    check_error_save_final_model,
    verbose_f,
    validate_number,
    validate_output_html_path,
)
from contrabass.core import Facade
from contrabass.core import FacadeUtils
from contrabass.core.utils.GrowthDependentCPConfig import GrowthDependentCPConfig
from contrabass.core.utils.CriticalCPConfig import CriticalCPConfig

TASK_CRITICAL_REACTIONS = "TASK_CRITICAL_REACTIONS"
TASK_SENSIBILITY = "TASK_SENSIBILITY"
TASK_SAVE_WITHOUT_DEM = "TASK_SAVE_WITHOUT_DEM"
TASK_SAVE_WITH_FVA = "TASK_SAVE_WITH_FVA"
TASK_SAVE_WITH_FVA_DEM = "TASK_SAVE_WITH_FVA_DEM"

DEFAULT_SPREADSHEET_FILE = "output.xls"
DEFAULT_HTML_FILE = "output.html"
DEFAULT_MODEL_FILE = "output.xml"

DEFAULT_SPREADSHEET_EXTENSION = ".xls"
HTML_EXTENSION = ".html"

LICENSE = """
    contrabass Copyright (C) 2020-2021  Alex Oarga  <718123 at unizar dot es> (University of Zaragoza)
    This program comes with ABSOLUTELY NO WARRANTY;
    This is free software, and you are welcome to redistribute it
    under certain conditions;
    For details see <https://github.com/openCONTRABASS/CONTRABASS/blob/master/LICENSE>
    If not available, see <https://www.gnu.org/licenses/>
"""


@click.group()
@click.help_option("--help", "-h")
def report():
    """
    Compute vulnerabilities on constrained-based models.
    """
    pass


@click.group()
@click.help_option("--help", "-h")
def new_model():
    """
    Export refined constrained-based model.
    """
    pass


@report.command()
@click.help_option("--help", "-h")
@click.argument(
    "model",
    type=click.Path(exists=True, dir_okay=False),
    # help="Input constrained.based model. Allowed file formats: .xml .json .yml"
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Do not print outputs while running.",
)
@click.option(
    "--objective",
    type=str,
    metavar="OBJECTIVE",
    help="Reaction id to be used as objective function with Flux Balance Analysis",
)
@click.option(
    "--output-spreadsheet",
    "-o",
    type=str,
    metavar="OUTPUT_SPREADSHEET",
    help="Output spreadsheet file with results. Allowed file formats: '.xls' '.xlsx' '.ods'. Default value: "
         "<INPUT-MODEL>.xls",
)
@click.option(
    "--output-html-report",
    "-r",
    type=str,
    metavar="OUTPUT_SPREADSHEET",
    help="Output spreadsheet file with results. Allowed file formats: '.html'. Default value: <INPUT-MODEL>.html",
)
@click.option(
    "--fraction",
    type=float,
    default=1.0,
    metavar="FRACTION",
    help="Fraction of optimum growth to be used in Flux Variability Analysis. Value must be between 0.0 and 1.0",
)
def critical_reactions(
        model, output_spreadsheet, output_html_report, silent, objective, fraction
):
    # Default values
    if fraction is None:
        fraction = 1.0
    fraction = validate_number(fraction)

    if output_spreadsheet is None:
        output_spreadsheet = os.path.splitext(model)[0] + DEFAULT_SPREADSHEET_EXTENSION

    if output_html_report is None:
        output_html_report = os.path.splitext(model)[0] + HTML_EXTENSION

    validate_input_model(model)
    validate_output_spread(output_spreadsheet)
    validate_output_html_path(output_html_report)

    task = TASK_CRITICAL_REACTIONS
    run(
        task,
        model,
        output_spreadsheet,
        output_html_report,
        not silent,
        objective,
        fraction,
    )


@report.command()
@click.help_option("--help", "-h")
@click.argument(
    "model",
    type=click.Path(exists=True, dir_okay=False),
    # help="Input constrained.based model. Allowed file formats: .xml .json .yml"
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Do not print outputs while running.",
)
@click.option(
    "--objective",
    type=str,
    metavar="OBJECTIVE",
    help="Reaction id to be used as objective function with Flux Balance Analysis",
)
@click.option(
    "--output-spreadsheet",
    "-o",
    type=str,
    metavar="OUTPUT_SPREADSHEET",
    help="Output spreadsheet file with results. Allowed file formats: '.xls' '.xlsx' '.ods'. Default value: <INPUT-MODEL>.xls",
)
@click.option(
    "--output-html-report",
    "-r",
    type=str,
    metavar="OUTPUT_HTML",
    help="Output spreadsheet file with results. Allowed file formats: '.html'. Default value: <INPUT-MODEL>.html",
)
def growth_dependent_reactions(
        model,
        output_spreadsheet,
        output_html_report,
        silent,
        objective,
):

    if output_spreadsheet is None:
        output_spreadsheet = os.path.splitext(model)[0] + DEFAULT_SPREADSHEET_EXTENSION

    if output_html_report is None:
        output_html_report = os.path.splitext(model)[0] + HTML_EXTENSION

    validate_input_model(model)
    validate_output_spread(output_spreadsheet)
    validate_output_html_path(output_html_report)

    task = TASK_SENSIBILITY
    run(task, model, output_spreadsheet, output_html_report, not silent, objective, None)


@new_model.command()
@click.help_option("--help", "-h")
@click.argument(
    "model",
    type=click.Path(exists=True, dir_okay=False),
    # help="Input constrained.based model. Allowed file formats: .xml .json .yml"
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Do not print outputs while running.",
)
@click.option(
    "--objective",
    type=str,
    metavar="OBJECTIVE",
    help="Reaction id to be used as objective function with Flux Balance Analysis",
)
@click.option(
    "--fraction",
    type=float,
    default=1.0,
    metavar="FRACTION",
    help="Fraction of optimum growth to be used in Flux Variability Analysis. Value must be between 0.0 and 1.0",
)
@click.option(
    "--output-model",
    "-o",
    type=str,
    metavar="OUTPUT-MODEL",
    help="Output model file. Allowed file formats: '.xml' '.json' '.yml'. Default value: "
         + "<INPUT-MODEL>-MFVA",
)
def fva_constrained(
        model,
        silent,
        objective,
        fraction,
        output_model,
):
    """
    Export a new model with its (maximum and minimum )flux bounds replaced with the
    constrained flux values obtained with Flux Variability Analysis.
    """

    if output_model is None:
        output_model = os.path.splitext(model)[0] + "-MFVA" + ".xml"

    validate_input_model(model)
    validate_output_model(output_model)

    task = TASK_SAVE_WITH_FVA
    run(task, model, output_model, None, not silent, objective, fraction)


@new_model.command()
@click.help_option("--help", "-h")
@click.argument(
    "model",
    type=click.Path(exists=True, dir_okay=False),
    # help="Input constrained.based model. Allowed file formats: .xml .json .yml"
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Do not print outputs while running.",
)
@click.option(
    "--objective",
    type=str,
    metavar="OBJECTIVE",
    help="Reaction id to be used as objective function with Flux Balance Analysis",
)
@click.option(
    "--fraction",
    type=float,
    default=1.0,
    metavar="FRACTION",
    help="Fraction of optimum growth to be used in Flux Variability Analysis. Value must be between 0.0 and 1.0",
)
@click.option(
    "--output-model",
    "-o",
    type=str,
    metavar="OUTPUT-MODEL",
    help="Output model file. Allowed file formats: '.xml' '.json' '.yml'. Default value: "
         + "<INPUT-MODEL>-MNODEM",
)
def without_dem(
        model,
        silent,
        objective,
        fraction,
        output_model,
):
    """
    Export a new model where Dead-End Metabolites have been removed.
    Dead-End Metabolites are removed iteratively, this is, if a reactions remains
    without metabolites it is also removed from the model.
    """

    if output_model is None:
        output_model = os.path.splitext(model)[0] + "-MNODEM" + ".xml"

    validate_input_model(model)
    validate_output_model(output_model)

    task = TASK_SAVE_WITHOUT_DEM
    run(task, model, output_model, None, not silent, objective, fraction)


@new_model.command()
@click.help_option("--help", "-h")
@click.argument(
    "model",
    type=click.Path(exists=True, dir_okay=False),
    # help="Input constrained.based model. Allowed file formats: .xml .json .yml"
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Do not print outputs while running.",
)
@click.option(
    "--objective",
    type=str,
    metavar="OBJECTIVE",
    help="Reaction id to be used as objective function with Flux Balance Analysis",
)
@click.option(
    "--fraction",
    type=float,
    default=1.0,
    metavar="FRACTION",
    help="Fraction of optimum growth to be used in Flux Variability Analysis. Value must be between 0.0 and 1.0",
)
@click.option(
    "--output-model",
    "-o",
    type=str,
    metavar="OUTPUT-MODEL",
    help="Output model file. Allowed file formats: '.xml' '.json' '.yml'. Default value: "
         + "<INPUT-MODEL>-MFVANODEM",
)
def fva_constrained_without_dem(
        model,
        silent,
        objective,
        fraction,
        output_model,
):
    """
    Export a new model with its (maximum and minimum) flux bounds replaced with the
    constrained flux values obtained with Flux Variability Analysis.
    In addition, Dead-End Metabolites are removed iteratively after the flux update.
    """

    if output_model is None:
        output_model = os.path.splitext(model)[0] + "-MFVANODEM" + ".xml"

    validate_input_model(model)
    validate_output_model(output_model)

    task = TASK_SAVE_WITH_FVA_DEM
    run(task, model, output_model, None, not silent, objective, fraction)


@click.command()
@click.help_option("--help", "-h")
def license():
    """
    Print license info.
    """
    click.echo(LICENSE)


def run(
        task,
        model_path,
        output_path,  # output spreadsheet report file or in case of new model, the output model path
        output_path_html,
        verbose,
        objective=None,
        fraction=1.0,
):
    try:
        if task == TASK_CRITICAL_REACTIONS:

            if verbose:
                print("Task: Critical reactions report generation")
            config = CriticalCPConfig()
            config.model_path = model_path
            config.print_f = verbose_f
            config.args1 = verbose
            config.args2 = None
            config.output_path_spreadsheet = output_path
            config.output_path_html = output_path_html
            config.objective = objective
            config.fraction = fraction

            facade = Facade()
            facade.generate_critical_cp_report(config)

        elif task == TASK_SENSIBILITY:

            if verbose:
                print("Task: Growth dependent reactions report generation")
            config = GrowthDependentCPConfig()
            config.model_path = model_path
            config.print_f = verbose_f
            config.args1 = verbose
            config.args2 = None
            config.output_path_spreadsheet = output_path
            config.output_path_html = output_path_html
            config.objective = objective

            facade = Facade()
            facade.generate_growth_dependent_report(config)

        elif task == TASK_SAVE_WITHOUT_DEM:
            if verbose:
                print("Task: save model without dead end metabolites")
            facade = Facade()
            facade.find_and_remove_dem(
                False, output_path, verbose_f, model_path, args1=verbose, args2=None
            )
            save_final_model(facade, output_path, verbose_f)

        elif task == TASK_SAVE_WITH_FVA:
            if verbose:
                print("Task: save model refined with Flux Variability Analysis")
            facade = Facade()
            error = facade.run_fva(
                False,
                output_path,
                verbose_f,
                model_path,
                args1=verbose,
                args2=None,
                objective=objective,
                fraction=fraction,
            )
            check_error_save_final_model(error, facade, output_path, verbose_f)

        elif task == TASK_SAVE_WITH_FVA_DEM:
            print(
                "Task: save model refined with Flux Variability Analysis without dead end metabolites"
            )
            facade = Facade()
            error = facade.run_fva_remove_dem(
                False,
                output_path,
                verbose_f,
                model_path,
                args1=verbose,
                args2=None,
                objective=objective,
                fraction=fraction,
            )
            check_error_save_final_model(error, facade, output_path, verbose_f)

        # Leave final blank line
        print("")

    except Exception as error:
        print("Error: Something went wrong:")
        # Important: the error is not raised but instead it is printed.
        print(str(error))
        raise error
