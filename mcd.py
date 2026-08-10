import mypy
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
            breakpoint()
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
        default=new_folder(),
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
    input_inspect(args.input, args.separator)
        # raise FileNotFoundError("The file path provided could not be found.") 

    if not output_check():
        raise ValueError("There is already a folder with the same name in this location.")

def input_inspect(input, separator):
    input_valid(input, separator) #check whether the file path provided from the user is valid

    for row in csvfile(input, separator, True): #row = {'policy_number': 'MT...', ...}
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

def output_check():
    return True
    #check whether there is a folder that has the same name as the designated folder.
 
def new_folder():
    pass
    #create a unique folder name for the output ({input_filename}_mcd_output_YYYY-MM-DD_HH:MM:SS)

if __name__ == "__main__":
    main()