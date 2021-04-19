"""reconstruct_mail

Contains the functionality for the mail reconstruction portion of the
mailtoil scripts.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
import datetime
import email
import logging
import sys
import shutil
import boto3
import os

from os import makedirs
from typing import List, Optional
from distutils.dir_util import copy_tree
from azure.storage.blob import BlobServiceClient

from .core import blob_storage
from .core import config
from .core import mail_reconstruction
from .core import service_bus
from .schemas import EmailConfig


def create_dir(dir: str) -> None:
    """Create the output directory."""
    try:
        makedirs(dir)
    except FileExistsError:
        # don't do anything if it already existed
        pass


def delete_dir(dir: str) -> None:
    """Deletes a directory and all its contents."""
    try:
        shutil.rmtree(dir)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def upload_blob(source, container_name, conn_str):
    try:
        service_client = BlobServiceClient.from_connection_string(conn_str)
        client = service_client.get_container_client(container_name)
        prefix = os.path.basename(source) + '/'
        for root, dirs, files in os.walk(source):
            for name in files:
                dir_part = os.path.relpath(root, source)
                dir_part = '' if dir_part == '.' else dir_part + '/'
                file_path = os.path.join(root, name)
                blob_path = prefix + dir_part + name
                print(f'Uploading {file_path} to {blob_path}')
                with open(file_path, 'rb') as data:
                    client.upload_blob(name=blob_path, data=data, overwrite=True)
    except Exception as ex:
        print(ex)


def upload_s3(source, aws_access_key, aws_secret_key, bucket_name):
    try:
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key,
                          aws_secret_access_key=aws_secret_key)
        prefix = os.path.basename(source) + '/'
        for root, dirs, files in os.walk(source):
            for name in files:
                dir_part = os.path.relpath(root, source)
                dir_part = '' if dir_part == '.' else dir_part + '/'
                file_path = os.path.join(root, name)
                s3_path = prefix + dir_part + name
                print(f'Uploading {file_path} to {s3_path}')
                s3.upload_file(file_path, bucket_name, s3_path)
    except Exception as ex:
        print(ex)


def write_to_output_location(cur_dir, output_type, output_loc, blob_conn, s3_access_key, s3_secret_key):
    """Write output to actual location"""
    if output_type == "blob":
        # write to azure blob
        upload_blob(cur_dir, output_loc, blob_conn)
    elif output_type == "s3":
        # write to AWS S3
        upload_s3(cur_dir, s3_access_key, s3_secret_key, output_loc)
    else:
        # write to local filesystem
        copy_tree(cur_dir, output_loc)


def get_dead_letters_from_service_bus(cluster: str, cfg: config.MailToilConfig,
                                      conn_str: str) -> List[str]:
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


def reconstruct(cfg: config.MailToilConfig, cluster: str, output: str,
                transaction_ids: List[str], anonymise: bool,
                plugin_cfg: EmailConfig, output_location: str, blob_conn: str,
                s3_access_key: str, s3_secret_key: str) -> None:
    """Perform the reconstruct functionality.

    Args:
        cfg: The mail toil config.
        cluster: The cluster to grab transactions from.
        output: The output where to write reconstructed mail to
        transaction_ids: The tx IDs to reconstruct.
        anonymise: Whether we should anonymise.
        plugin_cfg: The email plugin config object.
        output_location: The output location where to write the reconstructed mail to.
        blob_conn: The blob connection string to write reconstructed mail to
        s3_access_key: The S3 access key to write reconstructed mail to
        s3_secret_key: The S3 secret key to write reconstruct mail to
    """
    temp_dir = None
    try:
        encryption_provider = plugin_cfg.victoria_config.get_encryption()
        storage_conn_str = encryption_provider.decrypt_str(
            cfg.get_storage_account(cluster))

        if storage_conn_str is None:
            raise SystemExit(1)

        # if transaction IDs weren't given then get them from dead letters
        # instead
        if len(transaction_ids) == 0:
            service_bus_conn_str = encryption_provider.decrypt_str(
                cfg.get_service_bus_connection_str(cluster))

            if service_bus_conn_str is None:
                raise SystemExit(1)
            transaction_ids = get_dead_letters_from_service_bus(
                cluster, cfg, service_bus_conn_str)

        # now grab the MIME messages of these transactions and reconstruct them
        logging.info(f"Connecting to blob storage for '{cluster}'...")
        blob_client = blob_storage.connect(storage_conn_str)

        for transaction_id in transaction_ids:
            mime_msg = blob_storage.get_mime_message(transaction_id, blob_client)
            # create a temporary reconstruct directory
            temp_dir = str(transaction_id)
            create_dir(temp_dir)
            if mime_msg is not None:
                mail_reconstruction.process_mime_message(mime_msg, transaction_id,
                                                         temp_dir, anonymise)

        write_to_output_location(temp_dir, output, output_location, blob_conn, s3_access_key, s3_secret_key)
    except Exception as e:
        print(e)
    finally:
        if temp_dir:
            delete_dir(temp_dir)
