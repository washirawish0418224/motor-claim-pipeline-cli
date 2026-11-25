# Motor Claim Data Pipeline CLI
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](test/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A CLI data pipeline that ingests raw insurance claim CSV records, validates them against schema and regex specifications, isolates malformed rows, and generates financial analytics including loss ratios grouped by coverage type.

---

## How Does It Work?

The pipeline operates in 4 sequential stages using memory-efficient streaming generators:

```
                  ┌──────────────────────┐
                  │    Raw Input CSV     │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Schema Verification  │  ◄── config/format.csv
                  │  & Regex Validation  │
                  └──────────┬───────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
   ┌────────────────────┐        ┌────────────────────┐
   │   Valid Records    │        │ Malformed Records  │
   │ (cleaned_data.csv) │        │   (errors.csv +    │
   └──────────┬─────────┘        │   error_cause)     │
              │                  └────────────────────┘
              ▼
   ┌────────────────────┐
   │ Financial Metrics  │
   │   (summary.txt)    │
   └────────────────────┘
```

1. **Header & Structure Ingestion**: Streams rows using Python's `csv.reader` generator. The pipeline checks that all required headers match the schema in `config/format.csv`.
2. **Schema & Regex Validation**: Evaluates each field against strict validation patterns (policy number format, chronological dates, categorical values, and positive currency amounts).
3. **Data Segregation & Error Attribution**:
   * Valid rows are written to `cleaned_data.csv`.
   * Invalid rows are isolated into `errors.csv` with an appended `error_cause` column indicating exactly which field failed validation.
4. **Financial Summary Computation**: Aggregates total claim amounts, total premium collected, and computes the loss ratio ($\frac{\text{Claims}}{\text{Premiums}}$) for each coverage type (`comprehensive`, `third_party`), outputting a consolidated `summary.txt`.

---

## Project Structure

```text
├── config/
│   └── format.csv          # Schema definitions & regex patterns
├── sample_data/
│   ├── sample.csv          # Sample dataset with valid & invalid rows
│   └── sample2.csv         # Edge-case dataset
├── src/
│   └── mcd.py              # Core CLI pipeline and business logic
├── test/
│   └── test_mcd.py         # End-to-end integration and unit tests
├── result/                 # Generated output directory (gitignored)
├── pyproject.toml          # Project configuration, CLI entrypoint & dependencies
└── README.md
```

---

## Prerequisite

* **Python 3.10+**: Requires Python 3.10 or newer.
* **Git**: To clone the repository.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/washirawish0418224/Python_Project2_MCD.git
   cd Python_Project2_MCD
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the CLI package in editable mode**:
   ```bash
   # Install the CLI tool
   pip install -e .

   # Or install with testing tools (pytest)
   pip install -e ".[dev]"
   ```

4. **Verify the installation**:
   ```bash
   mcd -h
   ```

---

## CLI Options

| Flag | Name | Description | Default |
| :--- | :--- | :--- | :--- |
| `-i` | `--input` | **(Required)** File path of the raw claim CSV file | — |
| `-o` | `--output` | Designated folder name for the generated output | `MCD_<filename>_<timestamp>` |
| `-s` | `--separator` | Delimiter used in the input CSV (`,`, `-`, `/`, ` `, `_`) | `,` |
| `-c` | `--clear` | Clear and reset the output directory before proceeding | `False` |

---

## Configuration

The validation rules and required fields are defined in [`config/format.csv`](config/format.csv).

| Field Name | Pattern / Type | Description / Validation Rule |
| :--- | :--- | :--- |
| `policy_number` | `^MT-\d{6}$` | Must start with `MT-` followed by exactly 6 digits |
| `claim_date` | `DATE` | Valid calendar date formatted as `YYYY-MM-DD` |
| `claimant_name` | `^[a-zA-Z]+ [a-zA-Z]+$` | First name and last name separated by a space |
| `vehicle_type` | `^(sedan\|pickup\|suv\|motorcycle)$` | Allowed vehicle categories |
| `coverage_type` | `^(comprehensive\|third_party)$` | Type of insurance policy |
| `claim_amount` | `^(0\|[1-9]\d*)\.\d{2}$` | Monetary amount with exactly 2 decimal places |
| `premium_collected` | `^(0\|[1-9]\d*)\.\d{2}$` | Monetary amount with exactly 2 decimal places |
| `claim_status` | `^(PENDING\|OPEN\|CLOSED\|REJECTED)$` | Current status of the claim |

**Custom Schemas**: You can modify or add new regex patterns in `config/format.csv` without modifying the core Python code.

**Python Official Regular Expression Guide**: ['re — Regular expression operations — Python 3.15.2 documentation'](https://docs.python.org/3/library/re.html)

---

## How to Use?

### 1. Basic Execution
Run the pipeline against sample insurance claim data:
```bash
mcd -i sample_data/sample.csv
```

### 2. Custom Output Directory
Specify a custom directory name for your reports:
```bash
mcd -i sample_data/sample.csv -o my_custom_report
```

### 3. Custom Separator
Process files that use delimiters other than commas (e.g. whitespace, slashes):
```bash
mcd -i sample_data/sample.csv -s "_"
```

### 4. Clearing Output Folder
Reset and remove existing files inside the result folder before running:
```bash
mcd -c
```

### Output Results
Each run generates three organized files inside the output folder:

* **`cleaned_data.csv`**: Contains all valid rows that passed schema checks.
* **`errors.csv`**: Contains all malformed records with an added `error_cause` column:
  ```csv
  policy_number,claim_date,claimant_name,vehicle_type,coverage_type,claim_amount,premium_collected,claim_status,error_cause
  MT-02934071,2024-03-01,Somchai Jaidee,sedan,comprehensive,45000.00,52000.00,CLOSED,policy_number
  MT-999999,invalid-date,Jane Doe,sedan,third_party,500.00,1000.00,OPEN,claim_date
  ```
* **`summary.txt`**: Consolidated financial analysis:
  ```text
  Summary report for: sample.csv
  2024-11-25 10:30:00
  --------------------
  Number of malformed rows: 3

  Summary grouped by coverage_type:
  Claim type 'comprehensive':
  	- Claim amount: 163300.00
  	- Total premium collected: 167000.00
  	- Loss Ratio: 0.98
  Claim type 'third_party':
  	- Claim amount: 12500.00
  	- Total premium collected: 18000.00
  	- Loss Ratio: 0.69
  ```

---

## Running Tests

This project includes a comprehensive test suite in [`test/test_mcd.py`](test/test_mcd.py) using `pytest`. Tests cover CLI argument parsing, file error handling, custom output directories, invalid file formats, and directory cleanup.

To run the full test suite:

```bash
pytest test/ -v
```

All 8 parameterized integration tests should pass:
```text
test/test_mcd.py::test_end2end[normal] PASSED
test/test_mcd.py::test_end2end[missing_field_file] PASSED
test/test_mcd.py::test_end2end[no_argument] PASSED
test/test_mcd.py::test_end2end[file_not_found] PASSED
test/test_mcd.py::test_end2end[wrong_file_type] PASSED
test/test_mcd.py::test_end2end[custom_result_folder_name] PASSED
test/test_mcd.py::test_end2end[existed_folder_name] PASSED
test/test_mcd.py::test_end2end[clear_directory] PASSED
```

---

## License

This project is licensed under the MIT License.

<p align="center">
  <sub>Made by <a href="https://github.com/washirawish0418224">Washirawish</a> · Released under the <a href="LICENSE">MIT License</a></sub>
</p>

