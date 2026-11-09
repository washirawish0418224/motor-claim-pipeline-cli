# Motor Claim Data Pipeline CLI

A CLI tool that validates raw insurance claim data against schema specifications, isolates malformed rows, and generates financial summaries including loss ratios by coverage type.

## Features

* **Schema & Pattern Validation**: Checks CSV rows against field regex rules and standard `YYYY-MM-DD` date formats defined in `format.csv`.
* **Data Segregation**: Separates valid rows from invalid ones, appending targeted field error causes to malformed records.
* **Financial Metric Summaries**: Automatically computes total claims, premium collected, and loss ratio per coverage type.
* **Flexible CLI Flags**: Offers customizable delimiters, designated output folders, and result directory reset options.

---

## File Requirements

To run the pipeline smoothly, make sure `format.csv` resides in the same root directory as the script. This file sets the required header fields and regex validation patterns.

---

## Usage

Run the script via your terminal:

```bash
python mcd.py -i <path_to_input.csv> -o <result_folder_name> -s <separator>