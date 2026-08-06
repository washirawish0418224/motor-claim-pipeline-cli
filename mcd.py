import mypy
import argparse
from pathlib import Path
import re
FIELD_FILE = "format.csv"

class Record: #contains a row of record
    def __init__(self, record): #record = {'policy_number': 'MT...', ...}
        self.record = record
        self.status = [True, []] 

    @property
    def record(self):
        return self.__record

    @record.setter
    def record(self, record): #check whether it's missing or pattern mismatch
        #check pattern mismatch


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
    field_list = [row for row in csvfile(FIELD_FILE)] #[{'field_name': '...', 'data_type': str, ...}]
    input_inspect(args.input, args.separator)
        # raise FileNotFoundError("The file path provided could not be found.") 

    if not output_check():
        raise ValueError("There is already a folder with the same name in this location.")
    
def input_inspect(input, separator):
    input_valid(input) #check whether the file path provided from the user is valid

    for row in csvfile(input, seperator): #row = {'policy_number': 'MT...', ...}
        Record(row) #turn the record row into an object


def row_inspect(row): #inspect the pattern of each element in the row using "re"
    # b_policy_number = re.search("pattern", row[''])
    pass

def csvfile(input: str, sep: str, header: bool) -> dict:
    with open(input) as file:
        if header == True:
            reader = csv.DictReader(file, separator = sep)
        elif header == False:
            reader = csv.Reader(file, separator = sep)
        for row in reader:
            yield row #expect {'policy_number': 'MT',...} or {'field_name': 'policy_number',...}

def input_valid(input):
    try:
        open(input)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file \"{input}\" could not be found.")
    else:
        pass

    file_path = Path(input)
    extension = file_path.suffix()

    if extension != ".csv":
        raise TypeError(f"Expected .csv file type but got {extension} file type instead.")

    raw_data = 
def output_check():
    pass
    #check whether there is a folder that has the same name as the designated folder.
 
def new_folder():
    pass
    #create a unique folder name for the output (mcd_output_YYYY-MM-DD_HH:MM:SS)

def field_extract(): 
    field_list = [] #expect [("policy_number", str, "regex_pattern"),...]
    for row in csvfile(FIELD_FILE):
        field_list.append(tuple(row.values()))
    return field_list
if __name__ == "__main__":
    main()