video : https://drive.google.com/file/d/1IQG5n4ZtnCZXstkHJfyGHwmwLuJx7XBq/view?usp=sharing

# Week 12 LabX ADV: Agentic Communication Workflows (Advanced Email & SMS)

A config-driven **CommunicationAgent** that runs the email/SMS workflow defined in
`configs/comm_pipeline_config.json`. It sends templated emails and SMS, processes the inbox with
if/then rules (download attachments, mark as read, SMS alert, auto-reply), keeps a shared `context`
between tasks, and writes a JSON audit report.

## Prototype goals → implementation

| # | Goal | Where |
| :-: | :-- | :-- |
| 1 | Load credentials securely from `.env` | `utils.load_dotenv()`, `CommunicationAgent.__init__` |
| 2 | Dynamic email with multiple attachments | task **Send Daily Sales Report Email**: subject/body filled from context (`{report_date}`, `{sales_figure:,.2f}`, …), To + CC, attaches `sales_report.pdf` and `summary_data.xlsx` (only files that exist) |
| 3 | Dynamic SMS | task **Send Daily Sales SMS** (email-to-SMS gateway) |
| 4 | Process inbox | task **Simulate Incoming Request Email** sends a "Data Request" with an attachment to yourself; task **Process Incoming Data Requests** waits/polls for it, downloads attachments to `data/incoming_attachments/`, marks it read, then applies the rules: *from self + subject contains "Request"* → auto-reply; *body contains "urgent"* → SMS alert |
| 5 | Audit log | `reports/audit_report_comm_<timestamp>.json` (every send, rule match, alert, reply, and a success/failure summary) |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
```
Edit `.env`:
```ini
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=abcdefghijklmnop   # 16-char Gmail App Password, no spaces
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_SERVER=imap.gmail.com
TEST_RECIPIENT_EMAIL=your_email@gmail.com
SMS_GATEWAY_ADDRESS=
STUDENT_NAME=Your Name
STUDENT_ID=6xxxxxxxx-x
```
The App Password comes from https://myaccount.google.com/apppasswords (2-Step Verification must be on).
No email addresses need to be typed into the config: it uses `{sender_email}`, `{test_recipient}` and
`{sms_gateway}` from `.env`.

**About SMS:** email-to-SMS gateways exist only for some (mostly US) carriers; Thai carriers have no free
gateway. If `SMS_GATEWAY_ADDRESS` is empty, the "SMS" messages are delivered to your own inbox (empty
subject) so you can still see the SMS step working.

## Run

```bash
python main.py
```
The run takes about 15–40 seconds because it waits for Gmail to deliver the request email before searching.

Expected console highlights:
```text
... Email sent successfully to ... Subject: 'Daily Sales Report - YYYY-MM-DD'.
... Email sent successfully to ... Subject: 'Data Request for YYYY-MM-DD'.
... Downloaded attachment: .../data/incoming_attachments/sales_report.pdf
... Rule 'Request from self -> download & mark read' matched ...
... Rule 'Urgent body -> SMS alert' matched ...
... AUDIT LOG - INFO: Summary: 6 action(s) succeeded, 0 failed.
```
In your Gmail inbox you will see: the sales report (2 attachments), the sales SMS, the Data Request
(now marked read), the auto-reply "Re: Data Request … - Received & Processing", and the URGENT SMS alert.

## Config reference

| Task `type` | Main parameters |
| :-- | :-- |
| `send_email` | `recipients` {`to`, `cc`, `bcc`}, `subject_template`, `body_template`, `attachments`, `is_html` |
| `send_sms` | `phone_numbers` (gateway addresses), `message_template`, optional `carrier_name` |
| `process_inbox` | `search_criteria` {`status`, `from_sender`, `subject_contains`, `ignore_subject_prefixes`}, `wait_before_search_seconds`, `poll_attempts`, `download_attachments_base_dir`, `rules` |

Rules: `if` supports `from_sender`, `subject_contains`, `body_contains` (case-insensitive) and
`has_attachments`; `then` supports `send_sms_alert` (+ `alert_phone_numbers`, `alert_message_template`)
and `reply_with_template` (+ `reply_subject_template`). Rule templates can use the email's
`{subject}`, `{sender}`, `{sender_address}`, `{attachment_names}` as well as everything in the context.
Any task can store its result in the context with `output_context_key`.

## Fixes made to the original code

* IMAP search sent `SUBJECT Data Request` unquoted, which the server rejects for values with spaces; values are now quoted.
* The inbox was searched immediately after sending to self; it now waits and polls (`wait_before_search_seconds`, `poll_attempts`).
* Rules are case-insensitive and match the lab goals (request from self → download/mark read/reply; body contains "urgent" → SMS alert).
* The auto-reply (subject "Re: Data Request …") is ignored on the next run instead of being processed as a new request.
* Added the missing standalone SMS task, the sample attachments (`data/reports/`), `.env.example` and `requirements.txt`; duplicate log lines removed.

## Project structure

```text
├── src/
│   ├── communication_agent.py   # dispatcher, context, rules, audit log
│   ├── email_tasks.py           # SMTP send (To/CC/BCC, attachments, HTML) + IMAP search/fetch
│   ├── sms_tasks.py             # SMS via email gateway
│   ├── template_renderer.py     # "{key}" / "{value:.2f}" templating
│   ├── config_parser.py
│   └── utils.py                 # logging, .env, audit entries
├── configs/comm_pipeline_config.json
├── data/
│   ├── reports/                 # sales_report.pdf, summary_data.xlsx (attachments to send)
│   ├── attachments/
│   └── incoming_attachments/    # attachments downloaded from processed emails
├── create_sample_attachments.py # re-creates the two sample attachments
├── .env.example
├── main.py
├── requirements.txt
└── README.md
```
