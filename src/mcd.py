# import mypy
import sys
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
    CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
    FIELD_FILE_NAME = CONFIG_DIR / "format.csv"
    CLEAN_FILE_NAME = "cleaned_data.csv"
    ERROR_FILE_NAME = "errors.csv"
    ERROR_CAUSE_FIELD = "error_cause"
    HEADER_ROW = [row[0] for row in csvfile(FIELD_FILE_NAME, ",", False) if row][1:]
    RESULT_DIR_PATH = Path(__file__).parent / "result"
    LOSS_FIELD_NAME = "claim_amount"
    PREMIUM_FIELD_NAME = "premium_collected"
    CLAIM_TYPE_FIELD_NAME = "coverage_type"
    SUMMARY_FILE_NAME = "summary.txt"
    TIME_NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Record: #contains a row of record
    def __init__(self, record): #record = {'policy_number': 'MT...', ...}
        self.status = [True, {Const.ERROR_CAUSE_FIELD:[]}] # [False, {'error_cause': [policy_number]}] => mismatch pattern at policy_number 
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
            matching = None
            if regex_pattern == 'DATE':
                try:
                    matching = datetime.strptime(field_value, "%Y-%m-%d") #ISO 8601 only
                except ValueError:
                    matching = None
            else:
                matching = re.search(regex_pattern, field_value)

            if matching == None:
                self.status[0] = False
                self.status[1][Const.ERROR_CAUSE_FIELD].append(field['field_name'])

        self.__record = record

def main():
    parser = argparse.ArgumentParser(
        description="A program that cleans, export errors into a file, and summarize into a report."
    )
    
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="the file path of the raw claim data file.",
    )
    
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="the designated folder path for the output.",
    )

    parser.add_argument(
        "-s",
        "--separator",
        type=str,
        default=",",
        choices=[",", "-", "/", " ", "_"],
        help="separators format in the input csv file."
    )

    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="clear all the files inside output folder before proceeding"
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.error("No argument provided.\nPlease specify any option.\nRun \"mcd.py -h\" for more information.")
    if args.clear:
        shutil.rmtree(Const.RESULT_DIR_PATH)
        Const.RESULT_DIR_PATH.mkdir(parents=True, exist_ok=True)
        print(f'The directory \"{Const.RESULT_DIR_PATH}\" is successfully cleared.')
    if args.input:
        if args.output is None:
            args.output = new_folder_name(args.input)

        input_valid(args.input, args.separator) #check whether the file path provided from the user is valid
        result_dir = create_folder(args.output, args.input) #create a new folder and return the path
        result_summary = input_inspect(args.input, args.separator, result_dir)
        #result_summary = [('third_party', [clm, prem, l_ratio]),..., error_row]
        write_summary(args.input, result_summary, result_dir)
        print(f"The result is successfully created in the folder \"{result_dir.name}\".\nFolder location: {result_dir}")
    elif not args.input and args.output:
        parser.error("Please specify the input data with the flag \"-i\"\nRun \"mcd.py -h\" for more information.")

def input_inspect(input, separator, result_dir):
    row_index = 0
    clean_file_path = result_dir / Const.CLEAN_FILE_NAME
    error_file_path = result_dir / Const.ERROR_FILE_NAME

    with open(clean_file_path, "w") as cf, open(error_file_path, "w") as ef:
        cf_writer = csv.DictWriter(cf, fieldnames= Const.HEADER_ROW)
        ef_writer = csv.DictWriter(ef, fieldnames= Const.HEADER_ROW + [Const.ERROR_CAUSE_FIELD])
        cf_writer.writeheader()
        ef_writer.writeheader() 
        result_dict = {}
        error_row = 0
        for row in csvfile(input, separator, True): #row = {'policy_number': 'MT...', ...}
            the_record = Record(row) #turn the record row into an object
            # the_record.status => [False, [policy_number]] 
            #the_record.record = {'policy_number': 'MT...', ...}
            if the_record.status[0] == True:
                cf_writer.writerow(the_record.record)
                clm_type = the_record.record[Const.CLAIM_TYPE_FIELD_NAME]
                clm_amount = float(the_record.record[Const.LOSS_FIELD_NAME])
                prem_amount = float(the_record.record[Const.PREMIUM_FIELD_NAME])
                result_dict.setdefault(clm_type, [0, 0])
                result_dict[clm_type][0] += clm_amount
                result_dict[clm_type][1] += prem_amount

            elif the_record.status[0] == False:
                ef_writer.writerow(the_record.record | the_record.status[1])
                error_row += 1
    result_dict = list(result_dict.items())
    for type in result_dict:
        #type = ('type', [clm, prem])
        loss_ratio = float(type[1][0]) / float(type[1][1])
        type[1].append(loss_ratio)
    result_dict.append(error_row)
    return result_dict

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
        raise TypeError(f"Expecting .csv file type but got {extension} file type instead.")

    #check whether the dataset contains specific fields
    raw_data_field = next(csvfile(input, sep, False))
    field_list = Const.HEADER_ROW
    if not set(field_list) <= set(raw_data_field):
        raise ValueError(f"The given .csv file does not include the same set of fields as provided in the \"{Const.FIELD_FILE_NAME}\"")

def create_folder(folder_name, input_filename):
    result_parent_dir = Const.RESULT_DIR_PATH
    new_f = folder_name
    default_name = new_folder_name(input_filename)
    result_dir = result_parent_dir / new_f
    while result_dir.is_dir():
        folder_create = input(f"Unable to create a new folder named \"{folder_name}\".\nThere is already a folder with this name.\n----------\nUse the default name for the result folder?\nName:{default_name}\n\"Y\" - Yes\n\"N\" - No, I want to change the name for output folder.\n\"C\" - Cancel\n----------\n")
        folder_create = folder_create.strip().lower()
        if folder_create == "y":
            new_f = default_name
        elif folder_create == "n":
            new_f = input("Enter a new folder name:\n")
        elif folder_create == "c":
            SystemExit()

        result_dir = result_parent_dir / new_f

    new_f = folder_name
    result_dir = result_parent_dir / new_f
    result_dir.mkdir(parents=True, exist_ok=True)
    
    clean_file = result_dir / Const.CLEAN_FILE_NAME
    error_file = result_dir / Const.ERROR_FILE_NAME
    summary_file = result_dir / Const.SUMMARY_FILE_NAME
    clean_file.touch()
    error_file.touch()
    summary_file.touch()
    
    #add a header for both files
    the_reader = csvfile(Const.FIELD_FILE_NAME, ",", False)
    next(the_reader)
    
    with open(clean_file, mode = "w", newline = '', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(Const.HEADER_ROW)

    with open(error_file, mode = "w", newline = '', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(Const.HEADER_ROW + [Const.ERROR_CAUSE_FIELD])

    return result_dir
    #new folder is created
 
def new_folder_name(input_filename):
    folder_name = f"MCD_{input_filename}_{Const.TIME_NOW}"
    return folder_name
    #create a unique folder name for the output ({input_filename}_mcd_output_YYYY-MM-DD_HH:MM:SS)

def write_summary(data_flie_name, result_summary, result_dir):
    #result_summary = [('third_party', [clm, prem, l_ratio]),..., error_row]
    summary_path = result_dir / Const.SUMMARY_FILE_NAME
    errow_row = result_summary[-1]
    with open(summary_path, mode = 'w') as file:
        file.write(f"Summary report for: {data_flie_name}\n")
        file.write(Const.TIME_NOW)
        file.write('\n--------------------\n')
        file.write(f'Number of malformed rows: {errow_row}\n\n')
        file.write(f'Summary grouped by {Const.CLAIM_TYPE_FIELD_NAME}:\n')
        for type in result_summary[0:-1]:
            type_name = type[0]
            clm_amount = type[1][0]
            prem_amount = type[1][1]
            loss_ratio = type[1][2]
            file.write(f'Claim type \'{type_name}\':\n\t- Claim amount: {clm_amount}\n\t- Total premium collected: {prem_amount}\n\t- Loss Ratio: {loss_ratio}\n')
if __name__ == "__main__":
    main()