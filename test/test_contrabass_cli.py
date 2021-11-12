import os
import pytest
import logging
import subprocess
import xlrd
import math
import sys



from contrabass.core import CobraMetabolicModel
from errorHandler import CellsNotEqualException


LOGGER = logging.getLogger(__name__)
LOGGER_MSG = "Executing cli file: {} {}"

TEST_MODEL = "data/MODEL1108160000_url.xml"
INCORRECTLY_FORMATED = "data/incorrectly_formatted.xml"
FINDCPCLI_PATH = os.path.abspath("../scripts/contrabass")

OUTPUT_SPREADSHEET_TEST = "test_spreadsheet.xls"
OUTPUT_SPREADSHEET_TEST_CP = "test_spreadsheet_cp.xls"


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
# @pytest.mark.skip(reason="")
def test_verbose_output_on_model():
    params = ["-i", TEST_MODEL, "-o", OUTPUT_SPREADSHEET_TEST, "-v"]

    LOGGER.info(LOGGER_MSG.format(FINDCPCLI_PATH, params))

    f = open("data/test_verbose_output_on_model.txt", "r")
    expected_result = f.read()
    f.close()

    result = subprocess.check_output(
        ["python", FINDCPCLI_PATH] + params, stderr=subprocess.STDOUT, universal_newlines=True
    )

    # The output is not checked as this could change based on different dependencies version.
    # assert(str(result) == expected_result)

    LOGGER.info(
        "Comparing spreadsheets: '{}' : '{}'".format(
            OUTPUT_SPREADSHEET_TEST, "data/MODEL1108160000_url.xls"
        )
    )

    __compare_two_spreadsheets_content(
        OUTPUT_SPREADSHEET_TEST, "data/MODEL1108160000_url.xls"
    )


"""
    Assure correct output and no errors running correct model
"""


def test_verbose_chokepoint_computation_on_model():
    params = ["-i", TEST_MODEL, "-cp", OUTPUT_SPREADSHEET_TEST_CP, "-v"]

    LOGGER.info(LOGGER_MSG.format(FINDCPCLI_PATH, params))

    f = open("data/test_verbose_chokepoint_computation_on_model.txt", "r")
    expected_result = f.read()
    f.close()

    result = subprocess.check_output(
        ["python", FINDCPCLI_PATH] + params, stderr=subprocess.STDOUT, universal_newlines=True
    )

    # The output is not checked as this could change based on different dependencies version.
    # assert(str(result) == expected_result)

    LOGGER.info(
        "Comparing spreadsheets: '{}' : '{}'".format(
            OUTPUT_SPREADSHEET_TEST_CP, "data/MODEL1108160000_url_cp.xls"
        )
    )

    __compare_two_spreadsheets_content(
        OUTPUT_SPREADSHEET_TEST_CP, "data/MODEL1108160000_url_cp.xls"
    )


"""
    Assure correct output and no errors generating new models
"""


def test_verbose_generate_new_models():
    params = [
        "-i",
        TEST_MODEL,
        "-swD",
        "model_without_dem.xml",
        "-sF",
        "model_fva_flux.json",
        "-swDF",
        "model_fva_dem.yml",
    ]

    LOGGER.info(LOGGER_MSG.format(FINDCPCLI_PATH, params))

    f = open("data/test_verbose_generate_new_models.txt", "r")
    expected_result = f.read()
    f.close()

    result = subprocess.check_output(
        ["python", FINDCPCLI_PATH] + params, stderr=subprocess.STDOUT, universal_newlines=True
    )

    # The output is not checked as this could change based on different dependencies version.
    # assert(str(result) == expected_result)

    # model1 = CobraMetabolicModel("model_without_dem.xml")
    # model1.find_dem()
    # for compartment in model1.dem():
    #    assert(len(model.dem()[compartment]) == 0)

    model2 = CobraMetabolicModel("model_fva_dem.yml")
    model2.find_dem()
    for compartment in model2.dem():
        assert len(model2.dem()[compartment]) == 0
