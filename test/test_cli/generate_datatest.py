import os
import pytest
import logging
import subprocess
import xlrd
import math
import sys
from dotenv import load_dotenv

load_dotenv()

ENV_ENVIRONMENT = "ENVIRONMENT"
ENV_DEV = "DEV"
ENV_PRO = "PRO"

if os.environ.get(ENV_ENVIRONMENT) == ENV_DEV:
    # import relative path of core for development purposes
    print("*** DEVELOPMENT ENVIRONMENT ***")
    sys.path.append("../../findCPcore_pkg/core/")
    from CobraMetabolicModel import CobraMetabolicModel
else:
    from findCPcore import CobraMetabolicModel

from errorHandler import CellsNotEqualException


LOGGER = logging.getLogger(__name__)
LOGGER_MSG = "Executing cli file: {} {}"

TEST_MODEL = "data/MODEL1108160000_url.xml"
INCORRECTLY_FORMATED = "data/incorrectly_formatted.xml"
FINDCPCLI_PATH = os.path.abspath("../../scripts/contrabass")

OUTPUT_SPREADSHEET_TEST = "data/test_spreadsheet.xls"
OUTPUT_SPREADSHEET_TEST_CP = "data/test_spreadsheet_cp.xls"


def generate_test_no_args():

    LOGGER.info("Executing cli file: {}".format(FINDCPCLI_PATH))

    try:
        subprocess.check_output(
            ["python", FINDCPCLI_PATH], stderr=subprocess.STDOUT, text=True
        )
        raise RuntimeError(
            "This point should not be reached. Return code must not be 0."
        )
    except subprocess.CalledProcessError as err:
        f = open("data/no_args_err.txt", "w")
        f.write(str(err.stdout))
        f.close()


def generate_test_incorrect_input_model():

    try:
        params = ["-i", INCORRECTLY_FORMATED, "-o", OUTPUT_SPREADSHEET_TEST]

        LOGGER.info(LOGGER_MSG.format(FINDCPCLI_PATH, params))

        result = subprocess.check_output(
            ["python", FINDCPCLI_PATH] + params, stderr=subprocess.STDOUT, text=True
        )

    except subprocess.CalledProcessError as err:
        f = open("data/test_incorrect_input_model.txt", "w")
        f.write(str(err.stdout))
        f.close()


def generate_test_verbose_output_on_model():
    params = ["-i", TEST_MODEL, "-o", OUTPUT_SPREADSHEET_TEST, "-v"]

    LOGGER.info(LOGGER_MSG.format(FINDCPCLI_PATH, params))

    result = ""
    try:
        result = subprocess.check_output(
            ["python", FINDCPCLI_PATH] + params, stderr=subprocess.STDOUT, text=True
        )
    except subprocess.CalledProcessError as err:
        print(err.stdout)

    f = open("data/test_verbose_output_on_model.txt", "w")
    f.write(str(result))
    f.close()


def generate_test_verbose_chokepoint_computation_on_model():
    params = ["-i", TEST_MODEL, "-cp", OUTPUT_SPREADSHEET_TEST_CP, "-v"]

    LOGGER.info(LOGGER_MSG.format(FINDCPCLI_PATH, params))

    result = subprocess.check_output(
        ["python", FINDCPCLI_PATH] + params, stderr=subprocess.STDOUT, text=True
    )

    f = open("data/test_verbose_chokepoint_computation_on_model.txt", "w")
    f.write(str(result))
    f.close()


def generate_test_verbose_generate_new_models():
    params = [
        "-i",
        TEST_MODEL,
        "-swD",
        "data/model_without_dem.xml",
        "-sF",
        "data/model_fva_flux.json",
        "-swDF",
        "data/model_fva_dem.yml",
    ]

    LOGGER.info(LOGGER_MSG.format(FINDCPCLI_PATH, params))

    result = subprocess.check_output(
        ["python", FINDCPCLI_PATH] + params, stderr=subprocess.STDOUT, text=True
    )


generate_test_no_args()
generate_test_incorrect_input_model()
generate_test_verbose_output_on_model()
generate_test_verbose_chokepoint_computation_on_model()
generate_test_verbose_generate_new_models()
