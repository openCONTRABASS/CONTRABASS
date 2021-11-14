import os
import pytest
import logging
import subprocess
import xlrd
import math
import sys

sys.path.append("src")

from contrabass.core.CobraMetabolicModel import CobraMetabolicModel
from errorHandler import CellsNotEqualException


LOGGER = logging.getLogger(__name__)
LOGGER_MSG = "Executing cli file: {} {}"

# NOTE: these directories are relative the 'src' package
TEST_MODEL = "../test/test_cli/data/MODEL1108160000_url.xml"
INCORRECTLY_FORMATED = "../test/test_cli/data/incorrectly_formatted.xml"
DATA_SPREADSHEET = "../test/test_cli/data/MODEL1108160000_url.xls"
DATA_SPREADSHEET_GROWTH_DEP = "../test/test_cli/data/MODEL1108160000_url_cp.xls"

# directory with the package of the 'contrabass' module
# this directory will be opened with the 'cd' command
CONTRABASS_PACKAGE = os.path.abspath("src")
# this is the whole module of the CLI script
CONTRABASS_MODULE = "contrabass.cli.main"

OUTPUT_MODEL = "/tmp/output.xml"
OUTPUT_MODEL_YML = "/tmp/output.yml"
OUTPUT_SPREADSHEET_TEST = "/tmp/test_spreadsheet.xls"
OUTPUT_SPREADSHEET_TEST_CP = "/tmp/test_spreadsheet_cp.xls"


def __equal_cell(val1, val2):
    if isinstance(val1, float):
        if math.isnan(val1) and math.isnan(val2):
            return True
        else:
            return math.isclose(val1, val2, rel_tol=1e-5)
    else:
        return val1 == val2


def __compare_two_spreadsheets_content(file1, file2):
    xls1 = xlrd.open_workbook(file1, on_demand=True)
    xls2 = xlrd.open_workbook(file1, on_demand=True)

    for name in xls1.sheet_names():
        sheet1 = xls1.sheet_by_name(name)
        sheet2 = xls2.sheet_by_name(name)
        LOGGER.info(
            "Checking sheet : (col:{},row:{}) {} ".format(
                sheet1.ncols, sheet1.nrows, name
            )
        )

        for col in range(sheet1.ncols):
            for row in range(sheet1.nrows):
                val1 = sheet1.cell_value(row, col)
                val2 = sheet2.cell_value(row, col)
                if not __equal_cell(val1, val2):
                    raise CellsNotEqualException(
                        name, row, col, file1, val1, file2, val2
                    )


"""
    Assure correct output and no errors running correct model
"""
@pytest.mark.skip(reason="skipped as it takes to much to run on github action. Running it locally is suggested")
def test_verbose_output_on_model():
    params = [
        "report",
        "critical-reactions",
        TEST_MODEL,
        "--output-spreadsheet",
        OUTPUT_SPREADSHEET_TEST,
    ]

    LOGGER.info(LOGGER_MSG.format(CONTRABASS_PACKAGE, params))

    result = subprocess.check_output(
        ["python", "-m", CONTRABASS_MODULE] + params,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=CONTRABASS_PACKAGE,
    )

    LOGGER.info(
        "Comparing spreadsheets: '{}' : '{}'".format(
            OUTPUT_SPREADSHEET_TEST, DATA_SPREADSHEET
        )
    )

    __compare_two_spreadsheets_content(OUTPUT_SPREADSHEET_TEST, DATA_SPREADSHEET)


"""
    Assure correct output and no errors running correct model
"""
@pytest.mark.skip(reason="skipped as it takes to much to run on github action. Running it locally is suggested")
def test_verbose_chokepoint_computation_on_model():
    params = [
        "report",
        "growth-dependent-reactions",
        TEST_MODEL,
        "--output-spreadsheet",
        OUTPUT_SPREADSHEET_TEST_CP,
    ]

    LOGGER.info(LOGGER_MSG.format(CONTRABASS_PACKAGE, params))

    result = subprocess.check_output(
        ["python", "-m", CONTRABASS_MODULE] + params,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=CONTRABASS_PACKAGE,
    )

    LOGGER.info(
        "Comparing spreadsheets: '{}' : '{}'".format(
            OUTPUT_SPREADSHEET_TEST_CP, DATA_SPREADSHEET_GROWTH_DEP
        )
    )

    __compare_two_spreadsheets_content(
        OUTPUT_SPREADSHEET_TEST_CP, DATA_SPREADSHEET_GROWTH_DEP
    )


"""
    Assure correct output and no errors generating new models
"""
@pytest.mark.skip(reason="")
def test_verbose_generate_new_models():
    params = [
        "new-model",
        "fva-constrained-without-dem",
        TEST_MODEL,
        "--output-model",
        OUTPUT_MODEL_YML,
    ]

    LOGGER.info(LOGGER_MSG.format(CONTRABASS_PACKAGE, params))

    result = subprocess.check_output(
        ["python", "-m", CONTRABASS_MODULE] + params,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=CONTRABASS_PACKAGE,
    )

    model2 = CobraMetabolicModel(OUTPUT_MODEL_YML)
    model2.find_dem()
    for compartment in model2.dem():
        assert len(model2.dem()[compartment]) == 0
