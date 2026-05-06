# Solidity to EFSM

A research prototype for converting Solidity smart contracts into Extended Finite State Machine (EFSM) models for formal analysis.

This repository contains the core implementation used to parse Solidity smart contracts, extract contract behavior from the Solidity Abstract Syntax Tree (AST), and generate EFSM-based models compatible with Supremica `.wmod` files. The repository also contains example smart contracts, generated models, and experimental support for automatically converting smart contracts to EFSMs.

---

## Overview

Smart contracts are programs deployed on blockchain platforms such as Ethereum. Since they may control digital assets and execute autonomously after deployment, it is important to formally analyze their behavior before or after deployment.

This project converts Solidity smart contracts into Extended Finite State Machine (EFSM) models. The generated EFSM models can then be used for formal analysis, including reachability analysis, nonblocking verification, transfer-failure analysis, and supervisory-control-based reasoning.

The main workflow is:

1. Compile a Solidity contract into a compact JSON AST.
2. Parse the AST.
3. Extract contract variables, functions, modifiers, guards, assignments, and transfer behavior.
4. Convert the extracted behavior into EFSM components.
5. Generate a `.wmod` model.

---

## Core Branch

The main working branch of this repository is:

```bash
automatic_spec
```

This branch contains the core implementation, including:

- Solidity contract examples.
- AST extraction and parsing scripts.
- EFSM construction logic.
- Event and node generation.
- XML/WATERS model generation.
- Generated `.wmod` models.

To use the core branch:

```bash
git clone https://github.com/nishantparekh01/Solidity_to_EFSM.git
cd Solidity_to_EFSM
git checkout automatic_spec
```

---

## Repository Structure

```text
Solidity_to_EFSM/
│
├── smart_contracts/
│   ├── auction_contract.sol
│   ├── casino_blocking.sol
│   ├── casino_nonblocking.sol
│   ├── escrow_blocking.sol
│   ├── escrow_v2_blocking.sol
│   ├── escrow_v2_nonblocking.sol
│   ├── game_21.sol
│   ├── game_21_updated.sol
│   ├── game_9.sol
│   ├── game_9_3_players.sol
│   ├── game_9_3_players_version2.sol
│   └── test_game_9_v1.sol
│
├── models/
│   ├── NineGameAbstract.wmod
│   ├── NineGameAbstractP2win.wmod
│   ├── game9_conversion_output.wmod
│   └── game9_conversion_output.2_addresses.wmod
│
├── json_contract.py
├── solidity_ast_parser.py
├── ast_restructure.py
├── efsm_framework.py
├── add_events_nodes.py
├── add_events_nodes_v2.py
├── xml_generator.py
├── wmodify.py
├── test_supremica_generator.py
├── about_test_supremica_generator.txt
└── README.md
```

---

## Main Components

### `json_contract.py`

Compiles a Solidity smart contract using `solc` and extracts the compact JSON AST.

The Solidity input file is selected in this script using the `contract_file` variable.

Example:

```python
contract_file = r"smart_contracts/game_9_3_players.sol"
```

Update this path before running the conversion.

The script also contains the path to the Solidity compiler. If `solc` is installed somewhere else on your machine, update the compiler path accordingly.

---


## Requirements

The project requires:

- Python 3
- Solidity compiler `solc`
- Supremica/WATERS, for opening and analyzing generated `.wmod` models

The Python scripts mainly use standard libraries such as:

```python
json
subprocess
xml.etree.ElementTree
datetime
os
copy
dataclasses
typing
```

No `requirements.txt` is currently provided.

---

## Setup

Clone the repository:

```bash
git clone https://github.com/nishantparekh01/Solidity_to_EFSM.git
cd Solidity_to_EFSM
```

Switch to the core branch:

```bash
git checkout automatic_spec
```

Check that the Solidity compiler is available:

```bash
solc --version
```

If `solc` is not available globally, update the compiler path inside `json_contract.py`.

---

## Usage

### Step 1: Select the Solidity contract

Open `json_contract.py` and set the Solidity file to be converted.

Example:

```python
contract_file = r"smart_contracts/game_9_3_players.sol"
```

You can replace this with any contract in the `smart_contracts/` directory.

---

### Step 2: Set the Solidity compiler path

In `json_contract.py`, update the `solc` path if required.

For example, the script may contain a command similar to:

```python
command = ["C:/Windows/solcfolder/solc", "--ast-compact-json", contract_file]
```

Change this path according to your local installation of `solc`.

---

### Step 3: Set the output directory

Open `xml_generator.py` and update the output folder.

Look for the `base_folder` variable and replace it with a valid path on your machine.

Example:

```python
base_folder = r"C:\Users\your_name\Documents\conversion_output_models"
```

---

### Step 4: Generate the `.wmod` model

Run:

```bash
python xml_generator.py
```

The script creates a timestamped output folder and writes the generated `.wmod` model there.

The output file has a name similar to:

```text
output_YYYY_MM_DD_HH_MM.wmod
```

---

## Output

The main output of the tool is a WATERS/Supremica-compatible `.wmod` file. The generated `.wmod` file can be opened in Supremica/WATERS for further verification and analysis.

---

## Generated Models

The `models/` directory contains example generated models, including:

```text
NineGameAbstract.wmod
NineGameAbstractP2win.wmod
game9_conversion_output.wmod
game9_conversion_output.2_addresses.wmod
```

These models can be used as reference outputs or opened directly in Supremica/WATERS.

---

## Modeling Approach

The conversion is based on representing Solidity smart contract behavior as an Extended Finite State Machine.

At a high level:

1. A Solidity contract is compiled into a compact JSON AST.
2. The AST is parsed to extract relevant Solidity constructs.
3. Contract-level variables are represented as EFSM variables.
4. Address variables are mapped to finite symbolic domains.
5. Public functions are represented as EFSM components.
6. Function statements are translated into transitions.
7. `require` statements are translated into guarded transitions.
8. Assignments are translated into EFSM actions.
9. Conditional statements are translated into branching control flow.
10. Transfer behavior is modeled using success and failure transitions.
11. The generated EFSM components are exported as a `.wmod` model.

---


## Research Context

This repository was developed as part of research on formal modeling and verification of smart contracts.

The tool is intended to support analysis of questions such as:

- Can a smart contract reach a desired state?
- Can execution become blocking?
- Can failed transfers prevent progress?
- Can a malicious or non-cooperative participant affect contract behavior?
- Can supervisory control theory be used to reason about smart contract behavior?
- Can generated EFSM models support bias or strategy analysis?

---

## Suggested Workflow for New Contracts

To analyze a new Solidity smart contract:

1. Add the Solidity file to the `smart_contracts/` directory.
2. Update `contract_file` in `json_contract.py`.
3. Make sure the Solidity compiler path is correct.
4. Update the output folder path in `xml_generator.py`.
5. Run:

```bash
python xml_generator.py
```

6. Open the generated `.wmod` file in Supremica/WATERS.
7. Inspect the generated variables, events, components, and transitions.
8. Add or enable specifications if required.
9. Run formal analysis using the generated model.

---
