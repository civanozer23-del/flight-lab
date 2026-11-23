# AI Usage Disclosure

## Tools used

- ChatGPT (OpenAI, GPT-5.6)

## Conversation links

- Link 1: https://chatgpt.com/share/6b03ef69-15a4-83ed-a5a4-8c06e9ad5971

## What I used them for

- Understanding the assignment requirements and project structure.
- Implementing and debugging row validation.
- Implementing CSV parsing and duplicate detection.
- Implementing the command-line interface and error handling.
- Implementing basic and extended flight queries.
- Understanding public test failures and correcting the implementation.

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| validator.py | load_airports, validate_row, to_record and helper functions | AI-generated and explained |
| csv_loader.py | parse_files | AI-generated and explained |
| flight_parser.py | main, CLI handling, JSON and logging logic | AI-generated and explained |
| query.py | run_query, run_queries and query validation helpers | AI-generated and explained |

## Key prompts

1. Help me implement the flight query graded lab step by step according to the assignment requirements.
2. Help me understand the failing public tests and fix the relevant Python code.

## What I changed or verified myself

- I created and configured the GitHub repository and Codespace.
- I added my student information.
- I ran the public tests after each implementation stage.
- I checked the test results and applied the required changes.
- I verified that the final public test run passes all 29 tests.