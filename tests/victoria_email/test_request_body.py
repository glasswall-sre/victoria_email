import pytest
import aiohttp
import aiorun
import yaml
import victoria_email.schemas as schemas
import victoria_email.load_test as lt
import asyncio


def test_request_body():
    # Arrange
    endpoint = "unittest.endpoint.com"
    port = 25
    tenant_ids = ["1234-2134-1234", "1234-5678"]
    recipient = "recipient.com"
    sender = "sender.com"
    timeout = 20.0
    ret = None
    with open("./tests/victoria_email/test_with_mutiple_filetypes.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        # Act
        email_schema = schemas.EmailConfigSchema()
        ret = email_schema.load(yaml_obj)
    # Act
    req_body = {
        "endpoint": endpoint,
        "port": int(port),
        "tenant_ids": [str(tenant_id) for tenant_id in tenant_ids],
        "recipient": recipient,
        "sender": sender,
        "timeout": timeout,
        "load": ret.load_test.load
    }
    print(".")
    # Assert
    assert 'load' in req_body


def test_more():
    # Arrange
    endpoint = "unittest.endpoint.com"
    port = 25
    tenant_ids = ["1234-2134-1234", "1234-5678"]
    recipient = "recipient.com"
    sender = "sender.com"
    timeout = 20.0
    with open("./tests/victoria_email/test_with_mutiple_filetypes.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        # Act
        load_test_config_schema = schemas.LoadTestConfigSchema()
        load_test_config = load_test_config_schema.load(yaml_obj['load_test'])
        # Act
        req_body = {
            "endpoint": endpoint,
            "port": int(port),
            "tenant_ids": [str(tenant_id) for tenant_id in load_test_config.tenant_ids],
            "recipient": recipient,
            "sender": sender,
            "timeout": load_test_config.timeout,
            "load": {
                "distribution": [
                    {
                        "file": str(distrib.file),
                        "weight": int(distrib.weight)
                    }
                    for distrib in load_test_config.load.distribution
                ],
                "attachment_count": [int(x) for x in load_test_config.load.attachment_count]
            }
        }

    # Assert
    assert 'load' in req_body
