"""schemas

Marshmallow schemas for the email plugin.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
from dataclasses import dataclass
from uuid import UUID

from marshmallow import Schema, fields, post_load, validate


class LoadTestConfigSchema(Schema):
    """Marshmallow schema for the load testing config section."""
    mail_send_function_endpoint = fields.Str(required=True,
                                             allow_none=False,
                                             validate=validate.URL(
                                                 relative=False,
                                                 schemes="https"))
    mail_send_function_code = fields.Str(required=True, allow_none=False)
    tenant_id = fields.UUID(required=True, allow_none=False)
    timeout = fields.Float(required=False, allow_none=False, missing=1.0)

    @post_load
    def make_config(self, data, **kwargs):
        return LoadTestConfig(**data)


@dataclass
class LoadTestConfig:
    """The config of the load tester.

    Attributes:
        mail_send_function_endpoint: The HTTP endpoint of the going-postal backend.
        mail_send_function_code: The auth code to use the Azure function backend.
        tenant_id: The tenant ID to attach to the sent tests.
        timeout: The SMTP sending timeout to use.
    """
    mail_send_function_endpoint: str
    mail_send_function_code: str
    tenant_id: UUID
    timeout: float


class EmailConfigSchema(Schema):
    """Marshmallow schema for the email plugin config."""
    load_test = fields.Nested(LoadTestConfigSchema,
                              required=True,
                              allow_none=False)

    @post_load
    def make_config(self, data, **kwargs):
        return EmailConfig(**data)


@dataclass
class EmailConfig:
    """The email plugin config.

    Attributes:
        load_test: The config for the load testing command.
    """
    load_test: LoadTestConfig