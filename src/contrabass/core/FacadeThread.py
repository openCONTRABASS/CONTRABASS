import threading
import inspect
import ctypes
import time
import os

from contrabass.core.FacadeUtils import FacadeUtils

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


class ThreadInterrupt(Exception):
    def __str__(self):
        return "Exception: Thread stopped"

    def _async_raise(tid, exctype, syserr=True):
        """Raises an exception in the threads with id tid"""
        if not inspect.isclass(exctype):
            raise TypeError("Only types can be raised (not instances)")
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(tid), ctypes.py_object(exctype)
        )
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # "if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        if syserr:
            raise SystemError("PyThreadState_SetAsyncExc failed")


class FacadeThread(threading.Thread):
    def get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL : this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        raise AssertionError("could not determine the thread's id")

    def raiseExc(self, exctype, tid=None):
        """Raises the given exception type in the context of this thread.

        If the thread is busy in a system call (time.sleep(),
        socket.accept(), ...), the exception is simply ignored.

        If you are sure that your exception should terminate the thread,
        one way to ensure that it works is:

                t = ThreadWithExc( ... )
                ...
                t.raiseExc( SomeException )
                while t.isAlive():
                        time.sleep( 0.1 )
                        t.raiseExc( SomeException )

        If the exception is to be caught by the thread, you need a way to
        check that your thread has caught it.

        CAREFUL : this function is executed in the context of the
        caller thread, to raise an excpetion in the context of the
        thread represented by this instance.
        """
        if tid is None:
            _async_raise(self.get_my_tid(), exctype)
        else:
            _async_raise(tid, exctype)

    def __init__(self, model_path):
        self.model_path = model_path
        super(FacadeThread, self).__init__()

    def set_task(
        self,
        task,
        notify_function=None,
        args1=None,
        args2=None,
        output_path=None,
        objective=None,
        fraction=1.0,
    ):
        self.task = task
        self.notify_function = notify_function
        self.args1 = args1
        self.args2 = args2
        self.output_path = output_path
        self.objective = objective
        self.fraction = fraction

    def run(self):
        try:
            if self.task == TASK_READ_MODEL:
                f = FacadeUtils()
                (
                    result,
                    error,
                    model,
                    model_id,
                    reactions,
                    metabolites,
                    genes,
                    reactions_list,
                ) = f.read_model(self.model_path)
                self.notify_function(
                    result,
                    error,
                    model_id,
                    reactions,
                    metabolites,
                    genes,
                    reactions_list,
                    self.args1,
                    self.args2,
                )

            elif self.task == TASK_FIND_AND_REMOVE_DEM:
                f = FacadeUtils()
                self.model = f.find_and_remove_dem(self.model_path)
                if self.output_path is not None and self.model is not None:
                    f.save_model(self.output_path, self.model)
                self.notify_function(
                    "text", self.args1, self.args2, ended=True, result=True, error=None
                )

            elif self.task == TASK_SAVE_FVA:
                f = FacadeUtils()
                (self.model, error) = f.run_fva(
                    self.model_path, objective=self.objective, fraction=self.fraction
                )
                result_ok = error == ""
                if result_ok:
                    if self.output_path is not None and self.model is not None:
                        f.save_model(self.output_path, self.model)
                    self.notify_function(
                        "text",
                        self.args1,
                        self.args2,
                        ended=True,
                        result=True,
                        error=None,
                    )
                else:
                    self.notify_function(
                        "text",
                        self.args1,
                        self.args2,
                        ended=True,
                        result=False,
                        error=error,
                    )

            elif self.task == TASK_SAVE_FVA_DEM:
                f = FacadeUtils()
                (self.model, error) = f.run_fva_remove_dem(
                    self.model_path, objective=self.objective, fraction=self.fraction
                )
                result_ok = error == ""
                if result_ok:
                    if self.output_path is not None and self.model is not None:
                        f.save_model(self.output_path, self.model)
                    self.notify_function(
                        "text",
                        self.args1,
                        self.args2,
                        ended=True,
                        result=True,
                        error=None,
                    )
                else:
                    self.notify_function(
                        "text",
                        self.args1,
                        self.args2,
                        ended=True,
                        result=False,
                        error=error,
                    )

            elif self.task == TASK_SPREADSHEET:
                f = FacadeUtils()
                s = f.run_summary_model(
                    self.model_path,
                    self.notify_function,
                    self.args1,
                    None,
                    objective=self.objective,
                    fraction=self.fraction,
                )
                self.spreadsheet = s
                if self.output_path is not None:
                    (result_ok, error) = f.save_spreadsheet(self.output_path, s)
                self.notify_function(
                    "text", self.args1, self.args2, ended=True, result=True, error=None
                )

            elif self.task == TASK_SENSIBILITY:
                f = FacadeUtils()
                s = f.run_sensibility_analysis(
                    self.model_path,
                    self.notify_function,
                    self.args1,
                    None,
                    objective=self.objective,
                )
                self.spreadsheet = s
                if self.output_path is not None:
                    (result_ok, error) = f.save_spreadsheet(self.output_path, s)
                self.notify_function(
                    "text", self.args1, self.args2, ended=True, result=True, error=None
                )

            elif self.task == TASK_SAVE_SPREADSHEET:
                f = FacadeUtils()
                s = self.spreadsheet
                if self.output_path is not None and s is not None:
                    (result_ok, error) = f.save_spreadsheet(self.output_path, s)
                    self.notify_function(
                        "text",
                        self.args1,
                        self.args2,
                        ended=True,
                        result=result_ok,
                        error=error,
                    )

            elif self.task == TASK_SAVE_MODEL:
                f = FacadeUtils()
                (result, text) = f.save_model(self.output_path, self.model)
                self.notify_function(
                    "text",
                    self.args1,
                    self.args2,
                    ended=True,
                    result=result,
                    error=text,
                )
        except Exception as error:
            # Thread stopped
            # This raise is just for debugging purposes
            # print("DEBUG: please remove in FacadeThread.py:", str(error))
            # raise error
            # print("Error:", str(error))
            pass
