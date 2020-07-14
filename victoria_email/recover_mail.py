"""recover_mail

The functionality of the recover MailToil script is ported here.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
import email
import logging
import logging.config
import os
from os.path import join
from typing import List
import smtplib

from .core import config, service_bus, blob_storage, mail_reconstruction


def recover(cfg: config.MailToilConfig, cluster: str, input_file: str,
            smtp_addr: str) -> None:
    # connect to blob
    blob_client = blob_storage.connect(cfg.get_storage_account(cluster))

    tx_ids = []
    with open(input_file, "r") as tx_id_file:
        for line in tx_id_file:
            tx_ids.append(line.strip())

    with smtplib.SMTP(smtp_addr) as smtp:
        for tx_id in tx_ids:
            mime_str = blob_storage.get_mime_message(tx_id, blob_client)
            print(f"Found MIME message for tx '{tx_id}'")
            preprocessed_msg = mail_reconstruction.preprocess_mime_message(
                mime_str).encode("utf-8")
            mime_msg = email.message_from_bytes(preprocessed_msg)
            smtp.send_message(mime_msg)
            print(f"Sent to: {mime_msg['To']}, from: {mime_msg['From']}")