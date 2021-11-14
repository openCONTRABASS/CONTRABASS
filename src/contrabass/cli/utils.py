MSG_SUCCESFULLY_SAVE = "File successfully saved at: {}"
MSG_UNKNOWN_ERROR = "Error, something went wrong: {}"
MSG_FURTHER_INFO = "run contrabass -h for further information."
MSG_ERROR_DECIMAL = (
    "Error: parameter 'fraction' must be a decimal number between 0.0 and 1.0"
)


def __check_model_file(path):
    if len(path) <= 4:  # Error: file has no name
        return False

    if path[-4:] != ".xml" and path[-5:] != ".json" and path[-4:] != ".yml":
        return False
    else:
        return True


def __check_spread_file(path):
    if len(path) <= 4:  # Error: file has no name
        return False

    if path[-4:] != ".xls" and path[-4:] != ".ods" and path[-5:] != ".xlsx":
        return False
    else:
        return True


def __check_html_file(path):
    if len(path) <= 5:  # Error: file has no name
        return False

    if path[-5:] != ".html":
        return False
    else:
        return True


def validate_input_model(input_file):
    if not __check_model_file(input_file):
        print("Model file must be either .xml .json .yml")
        print(MSG_FURTHER_INFO)
        exit(1)


# Method for validating the output file path for operation that generate a new model
def validate_output_model(output_path):
    if not __check_model_file(output_path):
        print("Output model file must be either .xml .json .yml")
        print(MSG_FURTHER_INFO)
        exit(1)


def validate_number(parameter):
    try:
        parameter = float(parameter)
        if parameter < 0.0 or parameter > 1.0:
            print(MSG_ERROR_DECIMAL)
            exit(1)
    except:
        print(MSG_ERROR_DECIMAL)
        exit(1)
    return parameter


# Method for validating the output file path for operation that generate a new spreadsheet file
def validate_output_spread(output_path):
    if not __check_spread_file(output_path):
        print("Output file must be .xls .xlsx or .ods")
        print(MSG_FURTHER_INFO)
        exit(1)


def validate_output_html_path(output_path):
    if not __check_html_file(output_path):
        print("Output html report file format must be .html")
        print(MSG_FURTHER_INFO)
        exit(1)


def save_final_spreadsheet(facade, output_path, verbose_f, error):
    if error == "":
        (result_ok, text) = facade.save_spreadsheet(False, output_path, verbose_f)
        if result_ok:
            print(MSG_SUCCESFULLY_SAVE.format(text))
        else:
            print(MSG_UNKNOWN_ERROR.format(text))
    else:
        print(MSG_UNKNOWN_ERROR.format(error))


def save_final_model(facade, output_path, verbose_f):
    (result_ok, text) = facade.save_model(output_path, False, verbose_f)
    if result_ok:
        print(MSG_SUCCESFULLY_SAVE.format(text))
    else:
        print(MSG_UNKNOWN_ERROR.format(text))


def check_error_save_final_model(error, facade, output_path, verbose_f):
    if error != "":
        print(MSG_UNKNOWN_ERROR.format(error))
    else:
        save_final_model(facade, output_path, verbose_f)


def verbose_f(text, args1=False, args2=False):
    if args1:
        print(text)
