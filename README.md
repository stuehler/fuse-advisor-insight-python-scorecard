# fuse-advisor-insight-python-scorecard

Generates personalized PDF scorecards for Advisor Insight survey participants and emails them with a link to take the next survey.

## Surveys

| Survey ID | Topic                                |
| --------- | ------------------------------------ |
| 62        | AI                                   |
| 66        | Private Markets                      |
| 67        | Crypto                               |
| 13        | Time Management                      |
| 63        | UHNW Investors                       |
| 64        | Convergence of Wealth and Retirement |

## Prerequisites

- Python 3.13+
- ODBC Driver 17 for SQL Server
- Access to the FUSE RDS SQL Server instance

### Mac setup

```bash
# Install ODBC driver (one-time)
brew tap microsoft/mssql-release https://github.com/microsoft/homebrew-mssql-release
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql17
```

### Server setup (Ubuntu/EC2)

Python is provided via Miniconda at `/home/ubuntu/miniconda3/bin/python`.

## Getting started

### 1. Create and activate a virtual environment (Mac only — not needed on EC2)

```bash
python3 -m venv venv
source venv/bin/activate
```

**Important:** You must activate the virtual environment every time you open a new terminal to work on this project:

```bash
source venv/bin/activate
```

Your prompt will show `(venv)` when it's active. Run `deactivate` when you're done.

### 2. Install dependencies

```bash
pip install pandas sqlalchemy pyodbc python-dotenv playwright
playwright install chromium
```

### 3. Create a `.env` file

Create a `.env` file in the project root with the following variables:

```
SQL_SERVER=<rds-hostname>
SQL_DATABASE=<database-name>
SQL_USERNAME=<username>
SQL_PASSWORD=<password>
SQL_DRIVER=ODBC Driver 17 for SQL Server

SMTP_HOST=<ses-smtp-host>
SMTP_PORT=587
SMTP_USERNAME=<ses-username>
SMTP_PASSWORD=<ses-password>
EMAIL_FROM=<sender-email>
```

The `.env` file is in `.gitignore` and must never be committed.

## Usage

### From the command line

```bash
python scorecard_control.py \
  --userid 215 \
  --name "Rick Ledbury" \
  --email "rledbury@fuse-research.com" \
  --surveyid 62
```

### From Node/Express (on EC2)

```javascript
const { exec } = require("child_process");

const cmd = `/home/ubuntu/miniconda3/bin/python /home/ubuntu/python/scorecard_control.py \
  --userid ${userId} \
  --name "${userName}" \
  --email "${userEmail}" \
  --surveyid ${surveyId}`;

exec(cmd, { cwd: "/home/ubuntu/python" }, (error, stdout, stderr) => {
  if (error) {
    console.error(`Scorecard generation failed: ${error.message}`);
    return;
  }
  console.log("Scorecard generated and emailed successfully");
});
```

## Project structure

```
scorecard_control.py          # Main entry point — accepts CLI arguments, orchestrates the flow
scorecard_control_manual.py   # Manual/testing version with hardcoded participant
get_survey_data.py            # Database queries (SQL Server via SQLAlchemy)
scorecard_email.py            # Email composition and sending (AWS SES)
ai_scoring_algorithm.py       # Scoring + PDF generation for AI survey
pm_scoring_algorithm.py       # Scoring + PDF generation for Private Markets survey
crypto_scoring_algorithm.py   # Scoring + PDF generation for Crypto survey
time_mgmnt_scoring_algorithm.py  # Scoring + PDF generation for Time Management survey
uhnw_scoring_algorithm.py     # Scoring + PDF generation for UHNW survey
retire_scoring_algorithm.py   # Scoring + PDF generation for Wealth/Retirement survey
email1_html.html              # Email template — scorecard + next survey invite
email1_text.txt               # Plain-text fallback for email1
email2_html.html              # Email template — scorecard, all surveys complete
email2_text.txt               # Plain-text fallback for email2
scorecards/                   # Generated PDF output (gitignored)
.env                          # Credentials (gitignored)
```
