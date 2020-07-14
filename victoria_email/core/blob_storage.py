import json
import logging

from azure.common import AzureMissingResourceHttpError
from azure.storage.blob import BlockBlobService
import azure.storage.blob

from .config import StorageAccount

# sometimes it's in different places...
MIME_BLOB_NAMES = [
    "Received/MimeMessage",
    "MessageInspectionQueue/Glasswall.FileTrust.Messaging.ReceivedMessage.json"
]
"""The name of the blob within the container that contains the MIME message."""


def connect(storage_account: StorageAccount) -> BlockBlobService:
    """Connect to the Azure Blob Storage account using a StorageAccount.

    Args:
        storage_account (StorageAccount): The storage account creds to use.

    Returns:
        BlockBlobService: The blob service to use.
    """
    return BlockBlobService(account_name=storage_account.account_name,
                            account_key=storage_account.key)


def get_mime_message(transaction_id: str,
                     blob_service: BlockBlobService) -> str:
    """Get the MIME message received from a transaction ID.

    Args:
        transaction_id (str): The transaction ID to use to get the message.
        blob_service (BlockBlobService): The service to use to get the message.

    Returns:
        str: The MIME message.
    """
    for blob_name in MIME_BLOB_NAMES:
        try:
            print(transaction_id, blob_name)
            blob = blob_service.get_blob_to_text(transaction_id.lower(),
                                                 blob_name)
            if blob_name.endswith(".json"):
                mime_json = json.loads(blob.content)
                return mime_json["receivedMimeMessage"]
            else:
                return blob.content
        except AzureMissingResourceHttpError:
            # this is pure filth, but some of the blobs are in messed up formats
            # and we need to try multiple times to get the MIME message
            continue

    logging.error(
        f"Transaction ID '{transaction_id}' not found in blob storage")
    return None