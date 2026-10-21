# src/email_tasks.py
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import decode_header
from email.utils import parseaddr
import os
from utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


class EmailTasks:
    """
    Handles sending and receiving emails via SMTP and IMAP protocols.
    IMAP operations use UIDs so that results stay valid across reconnects.
    """

    def __init__(self, smtp_server, smtp_port, imap_server, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.sender_email = sender_email
        self.sender_password = sender_password
        self._smtp_server = None
        self._imap_mail = None
        logger.info(f"EmailTasks initialized for {sender_email}.")

    # --- SMTP (Sending) Methods ---
    def _connect_smtp(self):
        if self._smtp_server:
            return True
        try:
            self._smtp_server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            self._smtp_server.starttls()
            self._smtp_server.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into SMTP server.")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed. Check email and app password. Error: {e}")
        except Exception as e:
            logger.error(f"SMTP connection/login failed: {e}")
        self._smtp_server = None
        return False

    def _disconnect_smtp(self):
        if self._smtp_server:
            try:
                self._smtp_server.quit()
            except Exception as e:
                logger.warning(f"Error during SMTP disconnection: {e}")
            finally:
                self._smtp_server = None

    def send_email(self, recipients, subject, body, attachments=None, is_html=False, html_body=None):
        """
        Sends an email with dynamic content and multiple attachments.
        :param recipients: Dictionary with lists for 'to', 'cc', 'bcc'.
        :param body: Plain text (or HTML when is_html=True) body.
        :param html_body: Optional HTML alternative; sent together with the plain-text body.
        :return: (success, attached_files) tuple.
        """
        to_recipients = recipients.get('to', [])
        cc_recipients = recipients.get('cc', [])
        bcc_recipients = recipients.get('bcc', [])  # BCC goes in the envelope only, never in a header
        all_recipients = to_recipients + cc_recipients + bcc_recipients
        if not all_recipients:
            logger.error("No recipients specified for email.")
            return False, []

        msg = MIMEMultipart('mixed')
        msg['From'] = self.sender_email
        msg['Subject'] = subject
        msg['To'] = ", ".join(to_recipients)
        if cc_recipients:
            msg['Cc'] = ", ".join(cc_recipients)

        if html_body:
            alternative = MIMEMultipart('alternative')
            alternative.attach(MIMEText(body, 'plain', 'utf-8'))
            alternative.attach(MIMEText(html_body, 'html', 'utf-8'))
            msg.attach(alternative)
        else:
            msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))

        attached_files = []
        for attachment_path in attachments or []:
            if not os.path.exists(attachment_path):
                logger.warning(f"Attachment file not found: {attachment_path}. Skipping.")
                continue
            try:
                filename = os.path.basename(attachment_path)
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)
                attached_files.append(attachment_path)
                logger.info(f"Attached file: {attachment_path}")
            except Exception as e:
                logger.error(f"Error attaching file {attachment_path}: {e}")

        if not self._connect_smtp():
            return False, attached_files
        try:
            self._smtp_server.send_message(msg, from_addr=self.sender_email, to_addrs=all_recipients)
            cc_note = f" (CC: {', '.join(cc_recipients)})" if cc_recipients else ""
            logger.info(f"Email sent successfully to {', '.join(to_recipients)}{cc_note}. Subject: '{subject}'.")
            return True, attached_files
        except Exception as e:
            logger.error(f"Failed to send email. Error: {e}")
            return False, attached_files
        finally:
            self._disconnect_smtp()

    # --- IMAP (Receiving) Methods ---
    def _connect_imap(self, mailbox='INBOX'):
        if not self._imap_mail:
            try:
                self._imap_mail = imaplib.IMAP4_SSL(self.imap_server)
                self._imap_mail.login(self.sender_email, self.sender_password)
                logger.info("Successfully connected and logged into IMAP server.")
            except imaplib.IMAP4.error as e:
                logger.error(f"IMAP authentication failed. Check email and app password. Error: {e}")
                self._imap_mail = None
                return False
            except Exception as e:
                logger.error(f"IMAP connection/login failed: {e}")
                self._imap_mail = None
                return False
        status, _ = self._imap_mail.select(mailbox)
        if status != 'OK':
            logger.error(f"Could not select mailbox '{mailbox}'.")
            return False
        return True

    def _disconnect_imap(self):
        if self._imap_mail:
            try:
                self._imap_mail.logout()
            except Exception as e:
                logger.warning(f"Error during IMAP disconnection: {e}")
            finally:
                self._imap_mail = None

    @staticmethod
    def _quote(value):
        """IMAP search strings containing spaces must be quoted."""
        return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"') + '"'

    def search_emails(self, mailbox='INBOX', criteria='UNSEEN', from_sender=None, subject_contains=None):
        """
        Searches for emails based on criteria.
        :param subject_contains: A string or a list of strings that must all appear in the subject.
        :return: A list of email UIDs (bytes).
        """
        if not self._connect_imap(mailbox):
            return []
        try:
            search_query = [criteria]
            if from_sender:
                search_query.extend(['FROM', self._quote(from_sender)])
            if isinstance(subject_contains, str):
                subject_contains = [subject_contains]
            for text in subject_contains or []:
                search_query.extend(['SUBJECT', self._quote(text)])

            status, data = self._imap_mail.uid('SEARCH', None, *search_query)
            if status != 'OK':
                logger.error(f"IMAP search failed. Status: {status}")
                return []
            uids = data[0].split()
            logger.info(f"Found {len(uids)} emails matching {search_query} in '{mailbox}'.")
            return uids
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
        finally:
            self._disconnect_imap()

    def fetch_email_content(self, uid, mailbox='INBOX'):
        """
        Fetches and parses one email WITHOUT changing its \\Seen flag (BODY.PEEK).
        Marking as read and downloading attachments are separate, rule-driven actions.
        :return: (email_info dict, email.message.Message) or (None, None).
        """
        if not self._connect_imap(mailbox):
            return None, None
        uid_str = uid.decode('utf-8') if isinstance(uid, bytes) else str(uid)
        try:
            status, msg_data = self._imap_mail.uid('FETCH', uid_str, '(BODY.PEEK[])')
            if status != 'OK' or not msg_data or msg_data[0] is None:
                logger.error(f"Failed to fetch email UID {uid_str}. Status: {status}")
                return None, None

            msg = email.message_from_bytes(msg_data[0][1])
            sender = self._decode_header_part(msg['From'])
            subject = self._decode_header_part(msg['Subject'])

            text_body, html_body, attachments_meta = "", "", []
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition") or "")
                filename = part.get_filename()

                if filename or "attachment" in content_disposition:
                    attachments_meta.append({
                        'filename': self._decode_header_part(filename) if filename else "unnamed",
                        'content_type': content_type,
                        'filepath': None,  # Filled in when a rule downloads it
                    })
                elif content_type in ("text/plain", "text/html"):
                    try:
                        payload = part.get_payload(decode=True) or b""
                        decoded = payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
                    except Exception as e:
                        logger.warning(f"Could not decode {content_type} part of UID {uid_str}: {e}")
                        continue
                    if content_type == "text/plain":
                        text_body += decoded
                    else:
                        html_body += decoded

            email_info = {
                "uid": uid_str,
                "sender": sender,
                "sender_address": parseaddr(sender)[1].lower(),
                "subject": subject,
                "date": msg.get('Date', ''),
                "text_body": text_body,
                "html_body": html_body,
                "has_attachments": bool(attachments_meta),
                "attachments_meta": attachments_meta,
            }
            logger.info(f"Fetched UID {uid_str}: '{subject}' from {sender} ({len(attachments_meta)} attachment(s)).")
            return email_info, msg
        except Exception as e:
            logger.error(f"Error fetching/parsing email UID {uid_str}: {e}")
            return None, None
        finally:
            self._disconnect_imap()

    def save_attachments(self, msg, email_info, target_dir, allowed_extensions=None, filename_builder=None):
        """
        Saves attachments of an already-fetched message to disk.
        :param allowed_extensions: e.g. [".pdf"]; None means every attachment.
        :param filename_builder: Optional callable(original_filename) -> new filename (renaming).
        :return: List of saved file paths. Also fills 'filepath' in email_info['attachments_meta'].
        """
        ensure_directory_exists(target_dir)
        allowed = [ext.lower() for ext in allowed_extensions] if allowed_extensions else None
        saved = []
        meta_by_name = {m['filename']: m for m in email_info['attachments_meta']}

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart' or not part.get_filename():
                continue
            original = self._decode_header_part(part.get_filename())
            if allowed and os.path.splitext(original)[1].lower() not in allowed:
                logger.info(f"Skipping attachment '{original}' (extension not in {allowed}).")
                continue
            new_name = os.path.basename(filename_builder(original) if filename_builder else original)
            filepath = os.path.join(target_dir, new_name)
            try:
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True) or b"")
                saved.append(filepath)
                if original in meta_by_name:
                    meta_by_name[original]['filepath'] = filepath
                logger.info(f"Downloaded attachment: {filepath}")
            except Exception as e:
                logger.error(f"Error saving attachment {original}: {e}")
        return saved

    def mark_as_read(self, uid, mailbox='INBOX'):
        """Adds the \\Seen flag to an email."""
        if not self._connect_imap(mailbox):
            return False
        uid_str = uid.decode('utf-8') if isinstance(uid, bytes) else str(uid)
        try:
            status, _ = self._imap_mail.uid('STORE', uid_str, '+FLAGS', '(\\Seen)')
            if status == 'OK':
                logger.info(f"Marked email UID {uid_str} as read.")
                return True
            logger.error(f"Failed to mark UID {uid_str} as read. Status: {status}")
            return False
        except Exception as e:
            logger.error(f"Error marking UID {uid_str} as read: {e}")
            return False
        finally:
            self._disconnect_imap()

    def _decode_header_part(self, header_value):
        """Decodes header parts that might be encoded (e.g., '=?UTF-8?B?U3ViamVjdA==?=')."""
        if header_value is None:
            return ""
        decoded_string = ""
        for part, charset in decode_header(header_value):
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(charset if charset else 'utf-8')
                except (LookupError, UnicodeDecodeError):
                    decoded_string += part.decode('latin-1', errors='replace')
            else:
                decoded_string += part
        return decoded_string.strip()
