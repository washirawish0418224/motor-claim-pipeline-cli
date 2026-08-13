# import mypy
import shutil
from datetime import datetime
import argparse
from pathlib import Path
import re
import csv
def field_extract(input): 
    field_list = [] #expect [("policy_number", str, "regex_pattern"),...]
    for row in csvfile(input):
        field_list.append(tuple(row.values()))
    return field_list

def csvfile(input: str, sep: str, header: bool) -> dict:
    """Turn .csv file into dictionary
    
    A generator that generate the dictionary 
    from each row from the specified .csv file.

    Parameters
    ----------
    input : str
        Path to the CSV file.
    sep : str
        Delimiter character used in the file.
    header : bool
        If True, uses the first line as keys for dictionaries.
        If False, reads rows as plain lists.

    Yields
    ------
    dict or list
        A single row parsed from the CSV file.
    """
    with open(input) as file:
        if header == True:
            reader = csv.DictReader(file, delimiter = sep) # {'policy_number': 'MT', 'claim_date':}
        elif header == False:
            reader = csv.reader(file, delimiter = sep) # ['policy_number', 'claim_date']
        for row in reader:
            yield row #expect {'policy_number': 'MT',...} or {'field_name': 'policy_number',...}

class Const:
    FIELD_FILE_NAME = "format.csv"
    CLEAN_FILE_NAME = "cleaned_data.csv"
    ERROR_FILE_NAME = "errors.csv"
        
class Record: #contains a row of record
    def __init__(self, record): #record = {'policy_number': 'MT...', ...}
        self.status = [True, []] # [False, [policy_number]] => mismatch pattern at policy_number 
        self.record = record

    @property
    def record(self):
        return self.__record

    @record.setter
    def record(self, record): #check whether it's missing or pattern mismatch
        #check pattern mismatch, if mismatch => set the self.status to false

        for field in csvfile(Const.FIELD_FILE_NAME, ",", True):
            field_value = record.get(field['field_name']) #value of each field
            regex_pattern = field['regex_pattern']
            if not re.search(regex_pattern, field_value):
                self.status[0] = False
                self.status[1].append(field['field_name'])

        self.__record = record

def main():
    parser = argparse.ArgumentParser(
        description="A program that cleans, export errors into a file, and summarize into a report."
    )
    
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="The file path of the raw claim data file.",
    )
    
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="The designated folder path for the output.",
    )

    parser.add_argument(
        "-s",
        "--separator",
        type=str,
        default=",",
        choices=[",", "-", "/", " ", "_"],
        help="Separators format in the input csv file."
    )

    args = parser.parse_args()
    if args.output is None and args.input:
        args.output = new_folder_name(args.input)

    input_valid(args.input, args.separator) #check whether the file path provided from the user is valid
    result_dir = create_folder(args.output) #create a new folder and return the path
    result_data_file = Path(Path(shutil.copy2(Path(args.input), result_dir)).rename(Const.CLEAN_FILE_NAME)) # a path for duplicated (clean) file
    input_inspect(result_data_file, args.separator, result_dir)

def input_inspect(input, separator, result_dir):
    row_index = 0
    clean_file_path = result_dir / Const.CLEAN_FILE_NAME
    error_file_path = result_dir / Const.ERROR_FILE_NAME
    for row in csvfile(input, separator, True): #row = {'policy_number': 'MT...', ...}
        row_index += 1
        the_record = Record(row) #turn the record row into an object

def input_valid(input, sep):
    try:
        open(input)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file \"{input}\" could not be found.")
    else:
        pass

    file_path = Path(input)
    extension = file_path.suffix
    
    if extension != ".csv":
        raise TypeError(f"Expected .csv file type but got {extension} file type instead.")

    #check whether the dataset contains specific fields
    raw_data_field = next(csvfile(input, sep, False))
    field_list = next(csvfile(Const.FIELD_FILE_NAME,",", False))
    if set(field_list) <= set(raw_data_field):
        raise ValueError(f"The given .csv file does not include the same set of fields as provided in the \"{Const.FORMAT_FILE_NAME}\"")

def create_folder(folder_name):
    result_parent_dir = Path(__file__).parent.parent / "Result"
    if not result_parent_dir.is_dir():
        new_f = new_folder_name()
        folder_create = input(f"Unable to create a new folder named {folder_name}. There is already a folder with this name.\nUse the default name for the result folder?\nName:{new_f}\n-Y for Yes.")

        if not folder_create.strip.lower == "y":
            raise ValueError(f"Please use other name for output folder.")

    new_f = folder_name
    result_dir = result_parent_dir / new_f
    result_dir.mkdir(parents=True, exist_ok=True)
    
    clean_file = result_dir / Const.CLEAN_FILE_NAME
    error_file = result_dir / Const.ERROR_FILE_NAME
    clean_file.touch()
    error_file.touch()

    #add a header for both files
    the_reader = csvfile(Const.FIELD_FILE_NAME, ",", False)
    next(the_reader)
    header_row = [row[0] for row in the_reader if row]

    
    with open(clean_file, mode = "w", newline = '', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header_row)

    with open(error_file, mode = "w", newline = '', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header_row + ['cause of error'])

    return result_dir
    #new folder is created
 
def new_folder_name(input_filename):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folder_name = f"MCD_{input_filename}_{time_now}"
    return folder_name
    #create a unique folder name for the output ({input_filename}_mcd_output_YYYY-MM-DD_HH:MM:SS)

if __name__ == "__main__":
    main()