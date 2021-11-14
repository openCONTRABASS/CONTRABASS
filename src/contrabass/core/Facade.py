import os
import warnings
import os
from pathlib import Path

from contrabass.core.FacadeUtils import FacadeUtils
from contrabass.core.FacadeThread import FacadeThread, ThreadInterrupt
from contrabass.core.utils.GrowthDependentCPConfig import *
from contrabass.core.utils.CustomLogger import *
from contrabass.core.util import *

import threading
import inspect
import ctypes
import time

TASK_READ_MODEL = "READ_MODEL"
TASK_SAVE_DEM = "SAVE_DEM"
TASK_SAVE_FVA = "SAVE_FVA"
TASK_SAVE_FVA_DEM = "SAVE_FVA_DEM"
TASK_SPREADSHEET = "SPREADSHEET"
TASK_SENSIBILITY = "TASK_SENSIBILITY"
TASK_SAVE_SPREADSHEET = "SAVE_SPREADSHEET"
TASK_FIND_AND_REMOVE_DEM = "TASK_FIND_AND_REMOVE_DEM"
TASK_SAVE_MODEL = "TASK_SAVE_MODEL"
TASK_FVA = "TASK_FVA"


class Facade:
    model_path = None
    model = None
    spreadsheet = None

    model_id = None
    reactions = None
    metabolites = None
    genes = None

    thread1 = None
    tid = None

    __processes = None

    @property
    def processes(self):
        return self.__processes

    @processes.setter
    def processes(self, processes):
        self.__processes = processes

    def isAlive_tid(self, tid_input):
        for tid, tobj in threading._active.items():
            if tid == tid_input:
                return True
        return False

    def stop_tid(self, tid):
        try:
            ThreadInterrupt._async_raise(tid, ThreadInterrupt, syserr=False)
            print("STOPPING")
            while self.isAlive_tid(tid):
                time.sleep(0.1)
                print("STOPPING")
                ThreadInterrupt._async_raise(tid, ThreadInterrupt, syserr=False)
        except Exception as errr:
            # Thread stopped - catch some derivated errors
            # print("DEBUG: PLEASE REMOVE THIS RAISE IN Facade.py")
            # raise errr
            pass

    def get_tid(self):
        return self.thread1.get_my_tid()

    def stop(self):
        try:
            tid = self.get_tid()
            self.stop_tid(tid)
        except Exception as exc:
            # Thread is already stopped
            # print("DEBUG: PLEASE REMOVE THIS RAISE IN Facade.py")
            # raise exc
            pass

    def set_model_path(self, model_path):
        self.model_path = model_path

    def read_model(
        self, stoppable, model_path, notify_function, args1=None, args2=None
    ):
        self.model_path = model_path
        if not stoppable:
            (
                result,
                error,
                model,
                model_id,
                reactions,
                metabolites,
                genes,
            ) = FacadeUtils.read_model(model_path)
            self.model = model
            self.model_id = model_id
            self.reactions = reactions
            self.metabolites = metabolites
            self.genes = genes
            return (result, error)
        else:
            self.thread1 = FacadeThread(self.model_path)
            self.thread1.set_task(TASK_READ_MODEL, notify_function, args1, args2)
            self.thread1.start()
            self.tid = self.thread1.get_my_tid()
        return (None, None)

    def get_model_info(self):
        return (self.model_id, self.reactions, self.metabolites, self.genes)

    def generate_critical_cp_report(self, config):
        logger = CustomLogger(config.print_f, config.args1, config.args2)

        f = FacadeUtils()
        f.processes = config.processes

        results = f.compute_critical_points(
            config.model_path,
            config.print_f,
            config.args1,
            config.args2,
            config.objective,
            config.fraction,
        )
        self.spreadsheet = f.generate_critical_cp_spreadsheet(results)
        if self.spreadsheet is not None and config.output_path_spreadsheet is not None:
            logger.print("Generating spreadsheet report...")
            self.save_spreadsheet(False, config.output_path_spreadsheet, config.print_f)
            logger.print("File saved at: " + config.output_path_spreadsheet)

        if config.output_path_html is not None:
            logger.print("Generating html report...")
            html = f.generate_critical_cp_html_report(results)
            write_file(config.output_path_html, html)
            logger.print("File saved at: " + config.output_path_html)

    def generate_spreadsheet(
        self,
        stoppable,
        model_path,
        print_f,
        args1=None,
        args2=None,
        output_path=None,
        objective=None,
        fraction=1.0,
    ):
        warnings.warn(
            "generate_spreadsheet() is deprecated, use generate_critical_cp_report(findCPcore.CriticalCPConfig) instead",
            DeprecationWarning,
        )
        if not stoppable:
            f = FacadeUtils()
            f.processes = self.__processes
            self.spreadsheet = f.run_summary_model(
                model_path, print_f, args1, args2, objective, fraction
            )
            if self.spreadsheet is not None and output_path is not None:
                self.save_spreadsheet(stoppable, output_path, print_f)
            return ""
        else:
            self.thread1 = FacadeThread(self.model_path)
            self.thread1.set_task(
                TASK_SPREADSHEET,
                print_f,
                args1,
                args2,
                output_path,
                objective=objective,
                fraction=fraction,
            )
            self.thread1.start()
            self.tid = self.thread1.get_my_tid()

    def generate_growth_dependent_report(self, config):

        logger = CustomLogger(config.print_f, config.args1, config.args2)

        f = FacadeUtils()
        f.processes = config.processes

        results = f.compute_growth_dependent_chokepoints(
            config.model_path,
            config.print_f,
            config.args1,
            config.args2,
            config.objective,
        )
        self.spreadsheet = f.generate_growth_dependent_spreadsheet(results)
        if self.spreadsheet is not None and config.output_path_spreadsheet is not None:
            logger.print("Generating spreadsheet report...")
            self.save_spreadsheet(False, config.output_path_spreadsheet, config.print_f)
            logger.print("File saved at: " + config.output_path_spreadsheet)

        if config.output_path_html is not None:
            logger.print("Generating html report...")
            html = f.generate_growth_dependent_html_report(results)
            write_file(config.output_path_html, html)
            logger.print("File saved at: " + config.output_path_html)

    def generate_sensibility_spreadsheet(
        self,
        stoppable,
        model_path,
        print_f,
        args1=None,
        args2=None,
        output_path=None,
        objective=None,
    ):
        warnings.warn(
            "generate_sensibility_spreadsheet() is deprecated, use generate_growth_dependent_report(findCPcore.GrowthDependentCPConfig) instead",
            DeprecationWarning,
        )
        if not stoppable:
            f = FacadeUtils()
            f.processes = self.__processes
            self.spreadsheet = f.run_sensibility_analysis(
                model_path, print_f, args1, args2, objective
            )
            if self.spreadsheet is not None and output_path is not None:
                self.save_spreadsheet(stoppable, output_path, print_f)
            return ""
        else:
            self.thread1 = FacadeThread(self.model_path)
            self.thread1.set_task(
                TASK_SENSIBILITY,
                print_f,
                args1,
                args2,
                output_path,
                objective=objective,
            )
            self.thread1.start()
            self.tid = self.thread1.get_my_tid()

    def save_spreadsheet(self, stoppable, output_path, print_f):
        if not stoppable:
            f = FacadeUtils()
            f.processes = self.__processes
            (result_ok, text) = f.save_spreadsheet(output_path, self.spreadsheet)
            return (result_ok, text)
        else:
            self.thread1.set_task(
                TASK_SAVE_SPREADSHEET,
                notify_function=print_f,
                args1=None,
                args2=None,
                output_path=output_path,
            )
            self.thread1.run()
        return (None, None)

    # print_f (arg1, ended=True, str)
    def find_and_remove_dem(
        self, stoppable, output_path, print_f, model_path, args1=None, args2=None
    ):
        if not stoppable:
            f = FacadeUtils()
            f.processes = self.__processes
            self.model = f.find_and_remove_dem(model_path)
        else:
            self.thread1 = FacadeThread(self.model_path)
            self.thread1.set_task(
                TASK_FIND_AND_REMOVE_DEM,
                notify_function=print_f,
                args1=args1,
                args2=None,
                output_path=output_path,
            )
            self.thread1.start()
            self.tid = self.thread1.get_my_tid()

    def run_fva(
        self,
        stoppable,
        output_path,
        print_f,
        model_path,
        args1=None,
        args2=None,
        objective=None,
        fraction=1.0,
    ):
        if not stoppable:
            f = FacadeUtils()
            f.processes = self.__processes
            (self.model, errors) = f.run_fva(model_path, objective, fraction)
            return errors
        else:
            self.thread1 = FacadeThread(self.model_path)
            self.thread1.set_task(
                TASK_SAVE_FVA,
                notify_function=print_f,
                args1=args1,
                args2=None,
                output_path=output_path,
                objective=objective,
                fraction=fraction,
            )
            self.thread1.start()
            self.tid = self.thread1.get_my_tid()

    def run_fva_remove_dem(
        self,
        stoppable,
        output_path,
        print_f,
        model_path,
        args1=None,
        args2=None,
        objective=None,
        fraction=1.0,
    ):
        if not stoppable:
            f = FacadeUtils()
            f.processes = self.__processes
            (self.model, errors) = f.run_fva_remove_dem(model_path, objective, fraction)
            return errors
        else:
            self.thread1 = FacadeThread(self.model_path)
            self.thread1.set_task(
                TASK_SAVE_FVA_DEM,
                notify_function=print_f,
                args1=args1,
                args2=None,
                output_path=output_path,
                objective=objective,
                fraction=fraction,
            )
            self.thread1.start()
            self.tid = self.thread1.get_my_tid()

    # guarda el modelo calculado que se almacena en self
    # print_f (arg, result_ok=True/False, error text)
    def save_model(self, output_path, stoppable, print_f):
        if stoppable:
            self.thread1.set_task(
                TASK_SAVE_MODEL,
                notify_function=print_f,
                args1=None,
                args2=None,
                output_path=output_path,
            )
            self.thread1.run()
        else:
            f = FacadeUtils()
            f.processes = self.__processes
            (result, text) = f.save_model(output_path, self.model)
            return (result, text)
