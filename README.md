# victoria_email
Victoria plugin for managing the Glasswall Rebuild for Email platform.

## Features
- Load testing SMTP endpoints

## User guide

### Prerequisites
- Python 3.6+
- Pip

### Installation
```
$ pip install -U victoria_email
```

### Operation

#### Configuration
This plugin expects a section in your Victoria config file's `plugins_config` or
`plugins_config_location`. Its key is `email`. 

An easy way to edit your config file if you have VSCode installed is by running:
`code $(victoria config path)`.

A full config example is:
```yaml
email:
  load_test:
    mail_send_function_endpoint: https://sls-weur-dev-going-postal.azurewebsites.net/api/send
    mail_send_function_code: <the code to access the Azure Function>
    tenant_id: <the tenant ID to attach to the email>
    timeout: 10.0
```

#### Load testing
The `loadtest` command can be used to load test an SMTP endpoint.

It accepts the following **required** arguments:
- `-e`, `--endpoint`: The SMTP endpoint to send to, with optional port i.e. 
  `smtp.example.com:465`. If the port is unspecified, i.e. `smtp.example.com`
  then port 25 is used.
- `-r`, `--recipient`: The email address to send mail to, i.e. `test@example.com`.
- `-s`, `--sender`: The email address to send mail from, i.e. `test@example.com`.

Running with just the required arguments will send a single test.

It also accepts the following **optional** arguments:
- `-n`, `--frequency`: The number of tests to send per second. Defaults to 1.
- `-t`, `--duration`: The number of seconds to run the test for. Defaults to 1.

All of this information can be found by running `victoria email loadtest -h`.

Example of sending a single email:
```
$ victoria email loadtest -e smtp.example.com -s test@example.com -r test@example.com
```

Example of sending 46 mails per second for 60 seconds:
```
$ victoria email loadtest -e smtp.example.com -n 46 -t 60 -s test@example.com -r test@example.com
```

Example of sending using a different port than port 25:
```
$ victoria email loadtest -e smtp.example.com:465 -s test@example.com -r test@example.com
```

## Developer guide

### Prerequisites
- Python 3.6+
- Pipenv

### Quick start
1. Clone this repo.
2. In the root of the repo, run `pipenv sync --dev`.
3. You're good to go. You can run the plugin during development with 
   `pipenv run victoria email`.