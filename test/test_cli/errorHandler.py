CELLS_NOT_EQUAL_ERROR = """
Not equal values found on sheet '{}' (row:{}, col:{})

Value found on '{}':
    {}
Value found on '{}':
    {}
"""


class CellsNotEqualException(Exception):
    """Exception raised when two cells on two spreadsheets files have different values.

    Attributes:
        sheet -- sheet name
        row   -- row of the sheet
        col   -- column of the sheet
        file1 -- speadsheet file 1
        val1  -- value on speadsheet file 1 on row, col
        file2 -- speadsheet file 2
        val2  -- value on speadsheet file 2 on row, col
    """

    def __init__(self, sheet, row, col, file1, val1, file2, val2):
        self.sheet = sheet
        self.row = row
        self.col = col
        self.file1 = file1
        self.val1 = val1
        self.file2 = file2
        self.val2 = val2

    def __str__(self):
        return CELLS_NOT_EQUAL_ERROR.format(
            self.sheet, self.row, self.col, self.file1, self.val1, self.file2, self.val2
        )
