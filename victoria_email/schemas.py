"""schemas

Marshmallow schemas for the email plugin.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID
from typing import List, Dict

from marshmallow import Schema, fields, post_load, validate

from .core.blob_storage import CONNECTION_STR, get_blob_properties
from .core.util import get_random_items
from .core.config import MailToilConfigSchema, MailToilConfig


class Distribution:
    def __init__(self, file: str, weight: float):
        self.file = file
        self.weight = weight

    @classmethod
    def get_random_distributions(cls):
        properties = get_blob_properties('fileattachments', CONNECTION_STR)
        return [cls(attachment.name, attachment.size) for attachment in
                get_random_items(properties, count=100)]


class Load:
    def __init__(self, distribution: List[Dict] = None, attachment_count: List[int] = None):
        self.distribution = distribution
        self.attachment_count = attachment_count


class DistributionSchema(Schema):
    file = fields.Str(required=True)
    weight = fields.Float(required=True)

    @post_load
    def make_config(self, data, **kwargs):
        return Distribution(**data)


class LoadSchema(Schema):
    distribution = fields.List(fields.Nested(DistributionSchema))
    attachment_count = fields.List(fields.Int())

    @post_load
    def make_config(self, data, **kwargs):
        return Load(**data)


class LoadTestConfigSchema(Schema):
    """Marshmallow schema for the load testing config section."""
    mail_send_function_endpoint = fields.Str(required=True,
                                             allow_none=False,
                                             validate=validate.URL(
                                                 relative=False,
                                                 schemes="https"))
    mail_send_function_code = fields.Str(required=True, allow_none=False)
    tenant_ids = fields.List(fields.UUID(allow_none=False), required=False)
    timeout = fields.Float(required=False, allow_none=False, missing=1.0)
    load = fields.Nested(LoadSchema, required=False)

    @post_load
    def make_config(self, data, **kwargs):
        return LoadTestConfig(**data)


@dataclass
class LoadTestConfig:
    """The config of the load tester.

    Attributes:
        mail_send_function_endpoint: The HTTP endpoint of the going-postal backend.
        mail_send_function_code: The auth code to use the Azure function backend.
        tenant_ids: The tenant ID(s) to attach to the sent tests.
        timeout: The SMTP sending timeout to use.
        load:
    """
    mail_send_function_endpoint: str
    mail_send_function_code: str
    timeout: float
    load: Load = field(default_factory=Load)
    tenant_ids: List[UUID] = field(default_factory=list)


class EmailConfigSchema(Schema):
    """Marshmallow schema for the email plugin config."""
    load_test = fields.Nested(LoadTestConfigSchema,
                              required=False,
                              allow_none=True,
                              missing=None)
    mail_toil = fields.Nested(MailToilConfigSchema,
                              required=False,
                              allow_none=True,
                              missing=None)

    @post_load
    def make_config(self, data, **kwargs):
        return EmailConfig(**data)


@dataclass
class EmailConfig:
    """The email plugin config.

    Attributes:
        load_test: The config for the load testing command.
        mail_toil: The config for the mail toil commands.
    """
    load_test: LoadTestConfig
    mail_toil: Optional[MailToilConfig]
