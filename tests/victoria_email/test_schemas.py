import pytest
import victoria_email.schemas as schemas
import yaml
import marshmallow

def test_make_config_single_tenant():
    # Arrange
    with open("./tests/victoria_email/test_single_tenant.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        # Act
        email_schema = schemas.EmailConfigSchema()
        ret = email_schema.load(yaml_obj)
        # Assert
        assert str(ret.load_test.tenant_ids[0]) == "973037a8-eb2c-4637-9e6e-fd2bb1cf0e58"
        assert len(ret.load_test.tenant_ids) == 1


def test_make_config_multiple_tenants():
    # Arrange
    with open("./tests/victoria_email/test_multi_tenant.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        # Act
        email_schema = schemas.EmailConfigSchema()
        ret = email_schema.load(yaml_obj)
        # Assert
        assert len(ret.load_test.tenant_ids) == 2


def test_make_config_no_tenants():
    # Arrange
    with open("./tests/victoria_email/test_no_tenant.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        # Act
        # Assert
        with pytest.raises(marshmallow.exceptions.ValidationError):    
            email_schema = schemas.EmailConfigSchema()
            ret = email_schema.load(yaml_obj)

def test_make_config_with_load_config():
    # Arrange
    with open("./tests/victoria_email/test_with_mutiple_filetypes.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        # Act
        email_schema = schemas.EmailConfigSchema()
        ret = email_schema.load(yaml_obj)
        # Assert
        assert len(ret.load_test.load.attachment_count) == 3
        