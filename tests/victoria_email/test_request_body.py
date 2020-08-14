import pytest
import aiohttp
import aiorun

def test_request_body():
    # Arrange
    endpoint = "unittest.endpoint.com"
    port = 25
    tenant_ids = ["1234-2134-1234", "1234-5678"]
    recipient = "recipient.com"
    sender = "sender.com"
    timeout = 20.0
    # Act
    req_body = {
        "endpoint": endpoint,
        "port": int(port),
        "tenant_ids": [str(tenant_id) for tenant_id in tenant_ids],
        "recipient": recipient,
        "sender": sender,
        "timeout": timeout
    }
    # Assert
    #assert 1 == 1
