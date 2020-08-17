"""schemas

Marshmallow schemas for the email plugin.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from typing import List, Dict

from marshmallow import Schema, fields, post_load, validate

from .core.config import MailToilConfigSchema, MailToilConfig


class Disitribution:
    def __init__(self, file: str, weight: float):
        self.file = file
        self.weight = weight

class Load:
    def __init__(self, distribution: List[Dict], attachment_count: List[int]):
        self.distribution = distribution
        self.attachment_count = attachment_count

class DisitributionSchema(Schema):
    file = fields.Str(required=True)
    weight = fields.Float(required=True)

    @post_load
    def make_config(self, data, **kwargs):
        return Disitribution(**data)

class LoadSchema(Schema):
    distribution = fields.List(fields.Nested( DisitributionSchema ))
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
    tenant_ids = fields.List(fields.UUID(allow_none=False), required=True, allow_none=False, validate=validate.Length(min=1))
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
    tenant_ids: List[UUID]
    timeout: float
    load: Load


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