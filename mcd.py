import argparse
from pathlib import Path

FIELD_FILE = "format.csv"
breakpoint()
for row in csvfile(FIELD_FILE):
    print("OK")
    

class Record:
    pass
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
    
    input_inspect()
        # raise FileNotFoundError("The file path provided could not be found.") 

    if not output_check():
        raise ValueError("There is already a folder with the same name in this location.")
    
def input_inspect(input, separator):
    input_valid(input) #check whether the file path provided from the user is valid

    thedict = {}

def row_inspect(row): #inspect the pattern of each element in the row using "re"
    # b_policy_number = re.search("pattern", row[''])
    pass

def csvfile(input):
    with open(input) as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row

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

def output_check():
    pass
    #check whether there is a folder that has the same name as the designated folder.
 
def new_folder():
    pass
    #create a unique folder name for the output (mcd_output_YYYY-MM-DD_HH:MM:SS)
     
if __name__ == "__main__":
    main()