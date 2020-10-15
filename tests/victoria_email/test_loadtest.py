import yaml
from click.testing import CliRunner

from victoria_email import loadtest, schemas


def test_loadtest_cli_with_args():
    runner = CliRunner()
    with open("./tests/victoria_email/test_with_mutiple_filetypes.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        email_schema = schemas.EmailConfigSchema()
        config = email_schema.load(yaml_obj)
        args = ['-e', '0.0.0.0', '-s', 'test@example.com', '-r', 'test@example.com']
    result = runner.invoke(loadtest, args, obj=config)
    assert result.exit_code == 0


def test_loadtest_cli_without_args():
    runner = CliRunner()
    with open("./tests/victoria_email/test_with_generated_random_data.yaml", "r") as f:
        file_content = f.read()
        yaml_obj = yaml.load(file_content)
        email_schema = schemas.EmailConfigSchema()
        config = email_schema.load(yaml_obj)
        args = ['-e', '0.0.0.0']
    result = runner.invoke(loadtest, args, obj=config)
    assert result.exit_code == 0

