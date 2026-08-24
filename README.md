# Commit to Latex Report
This is a project where I was tasked with creating a professional document for summarising the progress of a team. It should be presentable to a client and show the progress a team has completed over a specified timeframe.

<img width="1856" height="898" alt="image" src="https://github.com/user-attachments/assets/0ffe6587-2a0d-460d-9268-362daf11eaea" />


## Installation
### Method 1:
Download the executable file from the releases tab.


### Method 2:
**Prerequisites:** [UV](https://docs.astral.sh/uv/getting-started/installation/) and a [Tex distribution e.g. MikTex](https://miktex.org/download).

To use the tool:
1. Download the source code from the `Releases` tab or clone the repository `git clone https://github.com/tactordev/commit-to-latex-report/`.
2. Enter the directory `cd commit-to-latex-report`.
3. Run `uv sync`.
4. Follow the usage as described below.

## Usage
To use the tool, you will need to run it using `uv run ctl` with specified parameters.
- `--url=https://github.com/author/repository` [REQUIRED]: this specifies a github repository to pull commit and information from.
- `--start=dd/mm/yyyy`: this specifies a start date for the commits and is defaulted to the creation of the repository.
- `--end=dd/mm/yyyy`: this specifies an end date for the commits and is defaulted to the date the tool was run.
- `--count=int`: this specifies the number of commits to fetch in total.

### Contribution
To contribute please create a Pull Request with the following information specified:
- Idea/Bug fixed.
- Description of changes and where they link to.


Made with 💕 by tactordev.
