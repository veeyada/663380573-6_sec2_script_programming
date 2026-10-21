# src/sms_tasks.py
from utils import setup_logging
from email_tasks import EmailTasks  # Reuse EmailTasks for sending the actual email

logger = setup_logging(__name__)


class SMSTasks:
    """
    Provides a simplified interface to send SMS via email-to-SMS gateways.
    Relies on EmailTasks for the actual email transmission.
    """

    def __init__(self, email_tasks_instance):
        if not isinstance(email_tasks_instance, EmailTasks):
            raise TypeError("SMSTasks requires an instance of EmailTasks.")
        self.email_tasks = email_tasks_instance

        # Common US carrier email-to-SMS gateways (add more as needed)
        self.carrier_gateways = {
            "att": "@txt.att.net",
            "verizon": "@vtext.com",
            "tmobile": "@tmomail.net",
            "sprint": "@messaging.sprintpcs.com",
            "boost": "@sms.boostmobile.com",
            "cricket": "@mms.cricketwireless.net",
            "us_cellular": "@email.uscc.net",
        }
        logger.info("SMSTasks initialized.")

    def _gateway_address(self, phone_number, carrier_name):
        if '@' in phone_number and '.' in phone_number:
            return phone_number  # Already a full gateway (or plain email) address
        if carrier_name and carrier_name.lower() in self.carrier_gateways:
            digits = "".join(ch for ch in phone_number if ch.isdigit())
            return f"{digits}{self.carrier_gateways[carrier_name.lower()]}"
        return None

    def send_sms(self, phone_numbers, message, carrier_name=None, subject=""):
        """
        Sends SMS messages via email-to-SMS gateway for multiple recipients.
        :param phone_numbers: List of numbers (e.g. ['1234567890']) or full gateway addresses.
        :param carrier_name: Carrier key (e.g. 'att'); not needed when a full address is given.
        :return: (all_succeeded, list of gateway addresses that were sent to)
        """
        sent_to = []
        for phone_number in phone_numbers:
            gateway = self._gateway_address(phone_number, carrier_name)
            if not gateway:
                logger.warning(f"No known carrier for {phone_number} (carrier='{carrier_name}') and it's not a gateway address. Cannot send SMS.")
                continue
            logger.info(f"Attempting to send SMS to {phone_number} via gateway: {gateway}")
            ok, _ = self.email_tasks.send_email(recipients={'to': [gateway]}, subject=subject, body=message)
            if ok:
                sent_to.append(gateway)

        logger.info(f"Attempted {len(phone_numbers)} SMS message(s), {len(sent_to)} succeeded (email-wise).")
        return bool(phone_numbers) and len(sent_to) == len(phone_numbers), sent_to
