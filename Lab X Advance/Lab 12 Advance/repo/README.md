# Week 12 LabX ADV: Agentic Communication Workflows (Advanced Email & SMS)

video : https://drive.google.com/file/d/1IQG5n4ZtnCZXstkHJfyGHwmwLuJx7XBq/view?usp=sharing

A configurable **CommunicationAgent** that runs email and SMS workflows defined in a JSON file
([configs/comm_pipeline_config.json](configs/comm_pipeline_config.json)). Features:
- Templated content filled in from the agent's shared context.
- Rule-based inbox processing.
- Attachment handling.
- Automated replies.
- SMS alerts.
- A JSON audit log.

## Key Concepts Demonstrated

| Concept | Where |
|---|---|
| **Agent + task dispatcher**: config `type` is mapped to a handler (`send_email`, `send_sms`, `process_inbox`) | `src/communication_agent.py` |
| **Declarative configuration**: tasks, rules and recipients are all in JSON. `${ENV_VAR}` placeholders are filled from `.env`, so no secrets go in the config | `configs/`, `src/config_parser.py` |
| **Context / state**: `self.context` holds report data plus each task's output (`output_context_key`), and later tasks can use it, e.g. `{daily_report_email.recipients.to.0}` | `src/communication_agent.py` |
| **Dynamic templating**: `{report_date}`, `{sales_figure:,.2f}`, dotted paths like `{attachments_meta.0.filename}` | `src/template_renderer.py` |
| **Advanced sending**: To / CC / BCC, multiple attachments (missing files are skipped), HTML + plain-text alternative | `src/email_tasks.py` |
| **Rule-based inbox**: IMAP search with retries. **IF** `from_sender` / `subject_contains` / `body_contains` / `has_attachments` **THEN** `download_attachments_to` (filter by extension, rename), `mark_as_read`, `send_sms_alert`, `reply_with_template` | `src/communication_agent.py`, `src/email_tasks.py` |
| **SMS**: email-to-SMS gateways, multiple numbers, templated message | `src/sms_tasks.py` |
| **Audit + error handling**: every task, rule match and action goes into `reports/audit_report_comm_*.json`. If anything fails, an `[Agent Error]` alert email is sent | `src/utils.py`, `src/communication_agent.py` |

## Workflow (`python main.py`)

1. **Send Daily Sales Report Email**: an HTML and plain-text report to `TEST_RECIPIENT_EMAIL` (CC yourself), with `sales_report.pdf` and `summary_data.xlsx` attached.
2. **Send Sales Alert SMS**: a templated message that reuses the output of task 1.
3. **Simulate Incoming Request Email**: sends `Data Request for <date> - Urgent [run <id>]` to yourself, with attachments.
4. **Process Incoming Data Requests**: searches INBOX (`UNSEEN`, falling back to `ALL`) for that email and then applies these rules:
   - `save_request_attachments`: IF the sender is me AND the subject contains "Request", THEN save **only PDFs**, renamed, to `data/incoming_attachments/<date>/` and mark the email as read.
   - `urgent_sms_alert`: IF the body contains "urgent" AND the email has attachments, THEN send an SMS alert.
   - `auto_reply`: IF the body contains "new data processing", THEN send the reply `Re: ... - Received & Processing`.
5. **Audit**: writes `reports/audit_report_comm_YYYYMMDD_HHMMSS.json`.

## Setup & How to Run

```bash
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python create_sample_data.py     # (re)creates data/reports/sales_report.pdf + summary_data.xlsx
copy .env.example .env           # macOS/Linux: cp .env.example .env  -> then edit .env
python main.py
```

**Gmail:** `SENDER_APP_PASSWORD` must be an **App password**, not your normal password. Turn on 2-Step Verification, then go to Google Account → Security → App passwords. IMAP access must also be enabled.

**SMS:** US carrier gateways need `TEST_SMS_PHONE_NUMBER` plus `TEST_SMS_CARRIER` (`att`, `verizon`, `tmobile`, ...). If your carrier has no gateway (for example in Thailand), put an email address in `TEST_SMS_PHONE_NUMBER` and leave `TEST_SMS_CARRIER` empty. The SMS then arrives as a short `[SMS] ...` email.

## Project Structure

```
├── src/
│   ├── communication_agent.py  # Agent: dispatcher, context, rules, error alert, audit report
│   ├── email_tasks.py          # SMTP send (To/CC/BCC, HTML, attachments) + IMAP search/fetch/save/mark-read
│   ├── sms_tasks.py            # Email-to-SMS gateways
│   ├── config_parser.py        # Load + validate config, resolve ${ENV_VAR}
│   ├── template_renderer.py    # {placeholder} rendering with dotted paths
│   └── utils.py                # Logging, env loading, audit entries
├── configs/comm_pipeline_config.json
├── data/
│   ├── reports/                # sales_report.pdf, summary_data.xlsx (sample attachments)
│   ├── attachments/
│   └── incoming_attachments/   # Saved by inbox rules (git-ignored)
├── create_sample_data.py
├── main.py
├── .env.example                # Copy to .env (git-ignored)
└── requirements.txt
```

## Debugging

- `Environment variable '...' not set`: check that `.env` exists and has every key listed in `.env.example`.
- `SMTPAuthenticationError` / `IMAP4.error`: you must use a Gmail **App password**, and IMAP must be enabled in Gmail settings.
- `No emails matched the inbox search criteria`: Gmail can be slow. Raise `wait_seconds` or `max_attempts` in the config.
- `Missing context key`: a `{placeholder}` in the config isn't in the context. The audit report lists which template failed.
