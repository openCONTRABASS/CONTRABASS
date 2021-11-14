import warnings
from collections import defaultdict

import xlwt
import os
import json

from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
from depinfo import get_pkg_info
from dotenv import load_dotenv

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

envars = os.path.dirname(os.path.realpath(__file__)) + "/.env"

from contrabass.core.CobraMetabolicModel import CobraMetabolicModel
from contrabass.core.Spreadsheet import Spreadsheet
from contrabass.core.State import StateEncoder
from contrabass.core.utils.CustomLogger import CustomLogger
from contrabass.core.util import *

# import contrabass.core
# VERSION=contrabass.__version__
VERSION = "0.0.0"


class ErrorGeneratingModel(Exception):
    pass


class FacadeUtils:

    __processes = None

    @property
    def processes(self):
        return self.__processes

    @processes.setter
    def processes(self, processes):
        self.__processes = processes

    def __init__(self, processes=None):
        self.__processes = processes

    def __generate_sheet_sensibility_analysis(
        self, xlwt_worbook, results_growth_dependent
    ):

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = xlwt_worbook.add_sheet("main")

        model = results_growth_dependent["model"]

        sheet.write(0, 0, "Model", style=style)
        sheet.write(2, 0, "Reactions", style=style)
        sheet.write(4, 0, "Metabolites", style=style)
        sheet.write(1, 0, model.id())
        sheet.write(3, 0, len(model.reactions()))
        sheet.write(5, 0, len(model.metabolites()))

        y = 1
        sheet.write(y + 0, 2, "Reversible Reactions (RR)", style=style)
        sheet.write(y + 1, 2, "Non-reversible Reactions (NR)", style=style)
        sheet.write(y + 2, 2, "Dead Reactions (DR)", style=style)
        sheet.write(y + 3, 2, "Chokepoints (CP)", style=style)

        y = 1
        X_OFFSET = 4
        for i in range(0, len(results_growth_dependent["index"])):
            if i == 0:
                sheet.write(
                    0, i + X_OFFSET, results_growth_dependent["index"][i], style=style
                )
            else:
                sheet.write(
                    0,
                    i + X_OFFSET,
                    "gamma = " + results_growth_dependent["index"][i],
                    style=style,
                )
            if (
                type(results_growth_dependent["reversible"][i]) == list
                or type(results_growth_dependent["reversible"][i]) == set
            ):
                sheet.write(
                    y + 0, i + X_OFFSET, len(results_growth_dependent["reversible"][i])
                )
                sheet.write(
                    y + 1,
                    i + X_OFFSET,
                    len(results_growth_dependent["non_reversible"][i]),
                )
                sheet.write(
                    y + 2, i + X_OFFSET, len(results_growth_dependent["dead"][i])
                )
                sheet.write(
                    y + 3, i + X_OFFSET, len(results_growth_dependent["chokepoints"][i])
                )
            else:
                sheet.write(
                    y + 0, i + X_OFFSET, results_growth_dependent["reversible"][i]
                )
                sheet.write(
                    y + 1, i + X_OFFSET, results_growth_dependent["non_reversible"][i]
                )
                sheet.write(y + 2, i + X_OFFSET, results_growth_dependent["dead"][i])
                sheet.write(
                    y + 3, i + X_OFFSET, results_growth_dependent["chokepoints"][i]
                )

        return xlwt_worbook

    def __generate_model_info_dict(self, model):
        # Save metadata
        results = {}
        results["solver"] = str(type(model.model().solver))
        results["findCPcore_version"] = VERSION
        results["date"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # save model data
        results["model_identifier"] = model.id()
        results["growth"] = model.get_growth()
        results["objective"] = model.objective()
        return results

    def compute_growth_dependent_chokepoints(
        self, model_path, print_f, arg1, arg2, objective=None
    ):

        FRAC = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 1.0]
        results_growth_dependent = defaultdict(list)
        logger = CustomLogger(print_f, arg1, arg2)

        logger.print("Reading model...")
        model = read_model(model_path, objective=objective, processes=self.__processes)

        logger.print("Computing essential reactions...")
        model.knockout_reactions_growth()
        model.compute_essential_reactions()
        logger.print("Computing optimal growth essential reactions")
        model.find_optimal_growth_essential_reactions()

        reversible_initial = set([r.id for r in model.reversible_reactions()])
        dead_reactions_initial = set([r.id for r in model.dead_reactions()])
        non_reversible_initial = (
            set([r.id for r in model.reactions()])
            .difference(dead_reactions_initial)
            .difference(reversible_initial)
        )
        model.find_chokepoints(exclude_dead_reactions=True)
        chokepoints_initial = set(model.chokepoint_reactions())

        essential_reactions_initial = set([r.id for r in model.essential_reactions()])

        # save model data
        results_growth_dependent["model"] = model
        results_growth_dependent["reactions"] = [r.id for r in model.reactions()]
        results_growth_dependent["metabolites"] = [m.id for m in model.metabolites()]
        results_growth_dependent["genes"] = [g.id for g in model.genes()]
        results_growth_dependent["compartments"] = list(model.compartments())
        results_growth_dependent["essential"] = [r.id for r in model.knockout_growth()]
        results_growth_dependent["optimal_essential"] = [
            r.id for r in model.optimal_growth_essential_reactions()
        ]
        # growth dependent values
        results_growth_dependent["index"].append("Initial")
        results_growth_dependent["reversible"].append(list(reversible_initial))
        results_growth_dependent["dead"].append(list(dead_reactions_initial))
        results_growth_dependent["non_reversible"].append(list(non_reversible_initial))
        results_growth_dependent["chokepoints"].append(list(chokepoints_initial))
        results_growth_dependent["essential_reactions"].append(
            list(essential_reactions_initial)
        )
        results_growth_dependent["fva_result"].append([])

        # growth essential reactions are computed on the initial model, as FVA is not mandatory for the computation
        # and one execution of the knock-out of each reaction (method) is enough.
        logger.print("Computing growth dependent essential reactions")
        for i in range(0, len(FRAC)):
            model.find_growth_essential_reactions(FRAC[i])
            growth_essential_reactions = set(
                [r.id for r in model.growth_essential_reactions()]
            )
            results_growth_dependent["essential_reactions"].append(
                list(growth_essential_reactions)
            )

        y = 1
        for i in range(0, len(FRAC)):

            model = read_model(
                model_path, objective=objective, processes=self.__processes
            )

            logger.print(
                "Running Flux Variability Analysis with fraction: " + str(FRAC[i])
            )
            errors_fva = model.fva(update_flux=True, threshold=FRAC[i])

            if errors_fva != []:
                logger.print(
                    "Could not run Flux Variability Analysis: " + str(errors_fva[0])
                )
                err_msg = "Error running FVA: " + str(errors_fva[0])
                results_growth_dependent["index"].append(str(FRAC[i]))
                results_growth_dependent["reversible"].append(err_msg)
                results_growth_dependent["dead"].append(err_msg)
                results_growth_dependent["non_reversible"].append(err_msg)
                results_growth_dependent["chokepoints"].append(err_msg)
                results_growth_dependent["fva_result"].append(err_msg)
                continue

            fva_dead_reactions = set([r.id for r in model.dead_reactions()])
            fva_reversible = set([r.id for r in model.reversible_reactions()])
            non_reversible = (
                set([r.id for r in model.reactions()])
                .difference(fva_reversible)
                .difference(fva_dead_reactions)
            )
            model.find_chokepoints(exclude_dead_reactions=True)
            chokepoints = set(model.chokepoint_reactions())

            results_growth_dependent["index"].append(str(FRAC[i]))
            results_growth_dependent["reversible"].append(list(fva_reversible))
            results_growth_dependent["dead"].append(list(fva_dead_reactions))
            results_growth_dependent["non_reversible"].append(list(non_reversible))
            results_growth_dependent["chokepoints"].append(list(chokepoints))
            results_growth_dependent["fva_result"].append(
                [(r.id, upper, lower) for (r, upper, lower) in model.get_fva()]
            )

        # Blocked reactions are equal to dead reactions with gamma = 0.0 (i.e. fraction of optimum = 0.0)
        results_growth_dependent["blocked"] = results_growth_dependent["dead"][1]

        # generate generic model data
        results_growth_dependent = {
            **results_growth_dependent,
            **self.__generate_model_info_dict(model),
        }

        return results_growth_dependent

    def generate_growth_dependent_spreadsheet(self, growth_dependent_results):
        s = xlwt.Workbook()
        s = self.__generate_sheet_sensibility_analysis(s, growth_dependent_results)
        sObject = Spreadsheet()
        sObject.set_workbook(s)

        return sObject

    def generate_growth_dependent_html_report(self, results_growth_dependent):
        # cobra model not json serializable
        del results_growth_dependent["model"]
        return generate_html_template(results_growth_dependent, "template.html")

    def generate_critical_cp_html_report(self, critical_cp_results):
        data = {}
        encoder = StateEncoder()
        data["initial"] = encoder.encode(critical_cp_results["initial"])
        data["fva"] = encoder.encode(critical_cp_results["fva"])
        data["dem"] = encoder.encode(critical_cp_results["dem"])
        data["fva_dem"] = encoder.encode(critical_cp_results["fva_dem"])
        return generate_html_template(
            critical_cp_results, "template_cp.html", default=encoder.default
        )

    def run_sensibility_analysis(self, model_path, print_f, arg1, arg2, objective=None):
        warnings.warn(
            "run_sensibility_analysis() is deprecated, use instead:\n"
            + "    results = facadeUtils.compute_growth_dependent_chokepoints(...) \n"
            + "    xlwt_workbook = facadeUtils.generate_growth_dependent_spreadsheet(result)",
            DeprecationWarning,
        )
        results_growth_dependent = self.compute_growth_dependent_chokepoints(
            model_path, print_f, arg1, arg2, objective
        )

        s = xlwt.Workbook()
        s = self.__generate_sheet_sensibility_analysis(s, results_growth_dependent)
        sObject = Spreadsheet()
        sObject.set_workbook(s)

        return sObject

    def compute_critical_points(
        self, model_path, print_f, arg1, arg2, objective=None, fraction=1.0
    ):
        print_f("Reading model...", arg1, arg2)
        model = CobraMetabolicModel(model_path)
        if objective is not None:
            model.set_objective(objective)
        if self.__processes is not None:
            model.processes = self.__processes

        model.save_state("initial")
        model.save_state("dem")
        model.save_state("fva")
        model.save_state("fva_dem")

        # save general model info
        general_info = self.__generate_model_info_dict(model)

        print_f("Generating models...", arg1, arg2)

        model.find_essential_genes_reactions()
        print_f("Searching Dead End Metabolites (D.E.M.)...", arg1, arg2)
        model.find_dem()
        print_f("Searching chokepoint reactions...", arg1, arg2)
        model.find_chokepoints(exclude_dead_reactions=True)
        print_f("Searching essential reactions...", arg1, arg2)
        model.knockout_reactions_growth()
        print_f("Searching essential genes...", arg1, arg2)
        errors_initial = model.find_essential_genes_1()
        if errors_initial != []:
            MSG = "Couldn't find essential genes: " + str(errors_initial[0])
            print_f(MSG)
        else:
            print_f("Searching essential genes reactions...", arg1, arg2)
            model.find_essential_genes_reactions()

        model.save_state("initial")

        print_f("Removing Dead End Metabolites (D.E.M.)...", arg1, arg2)
        model.remove_dem()
        print_f("Searching essential reactions...", arg1, arg2)
        model.knockout_reactions_growth()
        print_f("Searching new chokepoint reactions...", arg1, arg2)
        model.find_chokepoints(exclude_dead_reactions=True)

        if errors_initial == []:
            print_f("Searching essential genes...", arg1, arg2)
            errors_dem = model.find_essential_genes_1()
            if errors_dem == []:
                print_f("Searching essential genes reactions...", arg1, arg2)
                model.find_essential_genes_reactions()

        model.save_state("dem")

        print_f("Running Flux Variability Analysis...", arg1, arg2)
        model = CobraMetabolicModel(model_path)

        if objective is not None:
            model.set_objective(objective)
        if self.__processes is not None:
            model.processes = self.__processes

        errors_fva = model.fva(update_flux=True, threshold=fraction)

        if errors_fva != []:
            MSG = "Couldn't run Flux Variability Analysis: " + str(errors_fva[0])
            print_f(MSG, arg1, arg2)
        else:
            print_f("Searching Dead End Metabolites (D.E.M.)...", arg1, arg2)
            model.find_dem()
            print_f("Searching new chokepoint reactions...", arg1, arg2)
            model.find_chokepoints(exclude_dead_reactions=True)
            print_f("Searching essential genes...", arg1, arg2)
            errors_fva_genes = model.find_essential_genes_1()
            if errors_fva_genes != []:
                MSG = "Couldn't find essential genes: " + str(errors_fva_genes[0])
                print_f(MSG)
            else:
                print_f("Searching essential genes reactions...", arg1, arg2)
                model.find_essential_genes_reactions()
            print_f("Searching essential reactions...", arg1, arg2)
            model.knockout_reactions_growth()

            model.save_state("fva")

            print_f("Removing Dead End Metabolites (D.E.M.)...", arg1, arg2)
            model.remove_dem()
            print_f("Searching essential reactions...", arg1, arg2)
            model.knockout_reactions_growth()
            print_f("Searching new chokepoint reactions...", arg1, arg2)
            model.find_chokepoints(exclude_dead_reactions=True)
            if errors_fva_genes == []:
                print_f("Searching essential genes...", arg1, arg2)
                model.find_essential_genes_1()
                print_f("Searching essential genes reactions...", arg1, arg2)
                model.find_essential_genes_reactions()

            model.save_state("fva_dem")

        result = {}
        result["initial"] = model.get_state("initial")
        result["dem"] = model.get_state("dem")
        result["fva"] = model.get_state("fva")
        result["fva_dem"] = model.get_state("fva_dem")
        # include general model info computed previously
        result = {**result, **general_info}

        return result

    def generate_critical_cp_spreadsheet(self, critical_cp_results):

        initial = critical_cp_results["initial"]
        fva = critical_cp_results["fva"]
        dem = critical_cp_results["dem"]
        fva_dem = critical_cp_results["fva_dem"]

        s = Spreadsheet()
        s.spreadsheet_write_model_info(initial, "model_info")
        s.spreadsheet_write_summary(
            "summary",
            initial,
            dem,
            fva,
            fva_dem,
        )
        s.spreadsheet_write_reactions(initial, "reactions", ordered=True)
        s.spreadsheet_write_metabolites(
            initial,
            "metabolites",
            ordered=True,
            print_reactions=True,
        )
        s.spreadsheet_write_genes(initial, "genes", ordered=True, print_reactions=True)

        s.spreadsheet_write_reactions(fva, "reactions_FVA", ordered=True)
        s.spreadsheet_write_metabolites(
            fva,
            "metabolites_FVA",
            ordered=True,
            print_reactions=True,
        )

        s.spreadsheet_write_reversible_reactions(
            "reversible reactions",
            initial,
            fva,
            ordered=True,
        )
        s.spreadsheet_write_summary_reactions(
            "chokepoints",
            initial,
            dem,
            fva,
            fva_dem,
        )
        s.spreadsheet_write_summary_metabolites("dead-end", initial, fva)
        s.spreadsheet_write_chokepoints_genes(
            "comparison",
            initial,
            dem,
            fva,
            fva_dem,
        )
        s.spreadsheet_write_essential_genes_comparison(
            "essential genes",
            initial,
            dem,
            fva,
            fva_dem,
            ordered=True,
        )
        s.spreadsheet_write_essential_reactions(
            "essential reactions",
            initial,
            dem,
            fva,
            fva_dem,
            ordered=True,
        )

        return s

    def run_summary_model(
        self, model_path, print_f, arg1, arg2, objective=None, fraction=1.0
    ):
        warnings.warn(
            "run_summary_model() is deprecated, use instead:\n"
            + "    results = facadeUtils.compute_critical_points(...) \n"
            + "    xlwt_workbook = facadeUtils.generate_critical_cp_spreadsheet(result)",
            DeprecationWarning,
        )

        results = self.compute_critical_points(
            model_path, print_f, arg1, arg2, objective, fraction
        )
        return self.generate_critical_cp_spreadsheet(results)

    def find_and_remove_dem(self, model_path):
        model = CobraMetabolicModel(model_path)
        model.find_dem()
        model.remove_dem()
        return model

    def run_fva(self, model_path, objective=None, fraction=1.0):

        model = CobraMetabolicModel(model_path)

        if objective is not None:
            model.set_objective(objective)
        if self.__processes is not None:
            model.processes = self.__processes

        errors_fva = model.fva(update_flux=True)
        errors = model.fva(update_flux=True, threshold=fraction)
        if errors != []:
            return (model, errors[0])
        else:
            return (model, "")

    def run_fva_remove_dem(self, model_path, objective=None, fraction=1.0):

        model = CobraMetabolicModel(model_path)

        if objective is not None:
            model.set_objective(objective)
        if self.__processes is not None:
            model.processes = self.__processes

        errors = model.fva(update_flux=True, threshold=fraction)
        if errors != []:
            return (model, errors[0])
        else:
            model.find_dem()
            model.remove_dem()
            return (model, "")

    def save_model(self, output_path, model):
        if output_path != "":
            try:
                model.save_model(output_path)
                return (True, output_path)
            except Exception as error:
                if os.environ.get(ENV_ENVIRONMENT) == ENV_DEV:
                    raise error
                return (False, str(error))
        return (False, "")

    def save_spreadsheet(self, output_path, spreadsheet):
        if output_path != "":
            try:
                spreadsheet.spreadsheet_save_file(output_path)
                return (True, output_path)
            except Exception as error:
                if os.environ.get(ENV_ENVIRONMENT) == ENV_DEV:
                    raise error
                return (False, str(error))
        return (False, "")

    def read_model(self, model_path):
        try:
            model = CobraMetabolicModel(model_path)
            model_id = model.id()
            reactions = len(model.reactions())
            metabolites = len(model.metabolites())
            genes = len(model.genes())
            reactions_list = [x.id for x in model.reactions()]
            return (
                True,
                None,
                model,
                model_id,
                reactions,
                metabolites,
                genes,
                reactions_list,
            )
        except Exception as error:
            print(error)
            return (False, str(error), None, None, None, None, None, None)

    def print_something(self):
        pass
