"""reconstruct_mail

Contains the functionality for the mail reconstruction portion of the
mailtoil scripts.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
import datetime
import email
import logging
from os import makedirs
from typing import List, Optional

from .core import blob_storage
from .core import config
from .core import mail_reconstruction
from .core import service_bus


def create_output_dir(output_dir: str) -> None:
    """Create the output directory."""
    try:
        makedirs(output_dir)
    except FileExistsError:
        # don't do anything if it already existed
        pass


def get_dead_letters_from_service_bus(cluster: str,
                                      cfg: config.MailToilConfig) -> List[str]:
    """Get the list of dead letter IDs from the service bus."""
    # connect to the service bus for the cluster
    sb_client = service_bus.connect(
        cfg.get_service_bus_connection_str(cluster))

    # scan for dead letters to get IDs to cross reference in blob storage
    transaction_ids = []
    logging.info(f"Scanning queues on '{cluster}' for dead letters...")
    for queue in cfg.queues:
        dead_letters = service_bus.get_all_dead_letter_ids(queue, sb_client)
        for dead_letter in dead_letters:
            logging.info(f"\tFound dead letter '{dead_letter}'")
        transaction_ids += dead_letters
    logging.info(f"Found {len(transaction_ids)} dead letter(s) on '{cluster}'")
    return transaction_ids


def reconstruct(cfg: config.MailToilConfig, cluster: str, output_dir: str,
                transaction_ids: List[str], anonymise: bool):
    create_output_dir(output_dir)

    # if transaction IDs weren't given then get them from dead letters
    # instead
    if len(transaction_ids) == 0:
        transaction_ids = get_dead_letters_from_service_bus(cluster, cfg)

    # now grab the MIME messages of these transactions and reconstruct them
    logging.info(f"Connecting to blob storage for '{cluster}'...")
    blob_client = blob_storage.connect(cfg.get_storage_account(cluster))

    for transaction_id in transaction_ids:
        mime_msg = blob_storage.get_mime_message(transaction_id, blob_client)
        if mime_msg is not None:
            mail_reconstruction.process_mime_message(mime_msg, transaction_id,
                                                     output_dir, anonymise)
