<div align="center" style="text-align:center">
<h1> Victoria Email </h1>

Victoria Email is a V.I.C.T.O.R.I.A is a plugin that allows you to manipulate emails through an email platform 

![Gated Pipeline](https://github.com/glasswall-sre/victoria_email/workflows/Gated%20Pipeline/badge.svg)
![CI Pipeline](https://github.com/glasswall-sre/victoria_email/workflows/CI%20Pipeline/badge.svg)
![CD Pipeline](https://github.com/glasswall-sre/victoria_email/workflows/CD%20Pipeline/badge.svg)
![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=victoria-email&metric=sqale_rating&token=6f7ff43b4d5e3c325dd62e49e71acc338009be41)
![Reliability](https://sonarcloud.io/api/project_badges/measure?project=victoria-email&metric=reliability_rating&token=6f7ff43b4d5e3c325dd62e49e71acc338009be41)
![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=victoria-email&metric=security_rating&token=6f7ff43b4d5e3c325dd62e49e71acc338009be41)

</div>

## Features
- Load testing SMTP endpoints
- Sending single test emails from the CLI
- Reconstructing email from a deconstructed state
- Recovering email from Dead Letter Azure Service Bus Queues

## User guide

### Prerequisites
- Python 3.7+
- Pip
- [Victoria](https://github.com/glasswall-sre/victoria)

### Installation
```
$ pip install -U victoria_email
```

### Operation

#### Configuration
This plugin expects a section in your Victoria config file's `plugins_config` or
`plugins_config_location`. Its key is `email`. 

An easy way to edit your config file if you have VSCode installed is by running:
`code "$(victoria config path)"`.

A full config example is:
```yaml
email:
  load_test:
    mail_send_function_endpoints:
      - function: "<Azure Function endpoint URL>",
        mail_send_function_code: <the code to access the Azure Function>
      - function: "<Azure Function endpoint URL>",
        mail_send_function_code: <the code to access the Azure Function>
    tenant_ids: [<tenant ID(s) to attach to the email>]
    timeout: 10.0
    attachments:
      storage_connection_strings: <encrypted data>
  mail_toil:
    service_bus_connection_strings:
      <cluster-name>: <encrypted data>
      <cluster-name>: <encrypted data>
    # these are the Azure Service Bus Queues we want to check for dead letters
    queues:
      - "queues"
      - "you"
      - "want"
      - "to"
      - "check"
    storage_accounts:
      <cluster-name>: <encrypted data>
      <cluster-name>: <encrypted data>
    # this is the directory to use when backing up replayed messages
    vault_dir: "vault"
```

The `load_test` and `mail_toil` sections are both optional. If you don't need
mail toil or load testing functionality you can leave it out. The plugin will
give you a warning if you're missing either and attempting to use the
functionality.

##### Encrypting data for config values
In the `mail_toil` section of the config, the `service_bus_connection_strings`
and `storage_accounts` fields expect data that is encrypted. This can be
achieved with the pre-build `victoria encrypt` command. Details on this
can be found in [the documentation](https://sre.glasswallsolutions.com/victoria/user-guide.html#cloud-encryption)
but for a whistlestop tour:

1. Make sure you've set up your [Victoria cloud encryption backend](https://sre.glasswallsolutions.com/victoria/user-guide.html#azure).
2. Find a service bus you want to use with MailToil in the Azure Portal, and
   click on 'shared access policies' on the sidebar. Click on the policy here.
   Copy the 'primary connection string' from here.
3. Paste it into the following Victoria command:
   ```
   $ victoria encrypt data <the connection string>
   ```
4. The command should output a YAML object containing fields `data`, `iv`, `key`, and `version`.
   This is the encrypted connection string and can be safely stored in config.
   Put this YAML object in a key in your `service_bus_connection_strings` config field.
   The key name should be the cluster name, i.e. for uksprod1:
   ```yaml
   mail_toil:
     service_bus_connection_strings:
       cluster_name:
         data: <snip>
         iv: <snip>
         key: <snip>
         version: <snip>
   ```
5. Continue to do this for all of the service buses.
6. For storage accounts, follow the same steps, except for step 2. Instead:
   Find a storage account you want to use with MailToil in Azure Portal, and
   click on 'Access keys' on the sidebar. Copy the `key1` connection string from
   here.

#### Load testing
The `loadtest` command can be used to load test an SMTP endpoint.

It accepts the following **required** arguments:
- `-e`, `--endpoint`: The SMTP endpoint to send to, with optional port i.e. 
  `smtp.example.com:465` if the port is unspecified, i.e. `smtp.example.com`
  then port 25 is used
- `-r`, `--recipient`: The email address to send mail to, i.e. `test@example.com`
- `-s`, `--sender`: The email address to send mail from, i.e. `test@example.com`

Running with just the required arguments will send a single test

It also accepts the following **optional** arguments:
- `-n`, `--frequency`: The number of tests to send per second. Defaults to 1
- `-t`, `--duration`: The number of seconds to run the test for. Defaults to 1
- `-i`, `--tenant_ids`: Custom tenant id. Can be used multiple times. Defaults to random

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

Example of sending messages with random data and (recipient, sender):
```
$ victoria email loadtest -e smtp.example.com
```

#### Sending email
The `send` command can be used to send single emails (based on a YAML manifest
format) to an SMTP endpoint.

It accepts one argument, the path to the manifest file to send.

The format of the manifest file is as follows:
```yaml
sender: "test@example.com"
to: ["test@example.com"]
smtp_server: smtp.endpoint.com
tenant_id: <guid>
port: 25
attach:
- "C:/path/to/an/attachment.pdf"
```

Where:
- `sender`: The email address sending the email.
- `to`: The list of emails to send the email to.
- `smtp_server`: The SMTP server to send the email to.
- `tenant_id`: The FileTrust tenant ID to send the email with.
- `port`: The port on the SMTP server to connect via.
- `attach`: The list of files to attach.

If that manifest YAML file was `localhost.yml`, then to send it you would run:
```
$ victoria email send localhost.yml
```

#### Replaying dead letters
The `replay` command is used for replaying dead letters.

Simply run it with a cluster name and it will scan for dead letters in the queues
and replay them.

Example:
```
$ victoria email replay cluster
```

Will replay dead letters using the service bus connection string under key `cluster`
in the config file's `service_bus_connection_strings` section.

The queues it scans can be modified by editiing the config file's `queues` section.

#### Reconstructing mail
The `reconstruct` command can be used to reconstruct emails to files, cloud storage(Azure Blob/AWS S3) from transaction IDs.

It can also optionally anonymise the email contents if you need to give the email to a developer for them to help identify an issue.

Example of reconstructing mail with a transaction ID on local machine:
```
$ victoria email reconstruct cluster -id <guid> -o local -loc output_folder
```

Example of reconstructing mail with a transaction ID on azure blob:
```
$ victoria email reconstruct cluster -id <guid> -o blob -loc output_folder -blob-conn <conn-str-in-single-quotes>
```

Example of reconstructing and anonymising mail on local machine:
```
$ victoria email reconstruct cluster -id <guid> -o local -loc output_folder --anon
```

Example of reconstructing multiple transactions:
```
$ victoria email reconstruct cluster -id <guid1> -id <guid2> -id <guid3> -o local -loc output_folder
```

The cluster name given corresponds to keys in `storage_accounts` in the config

#### Replaying mail through the system
The `recover` command can replay mail through the system right from the beginning.
It does this by using a transaction ID to grab the failed mail, reconstructing it,
and sending it to an SMTP endpoint, as if it were a new mail.

This should only be done in the event of an emergency (mostly when SMTP receiver
was not able to put a received email on the message inspection queue). If you
replay a message more than once or replay a message that has already been
transmitted then customers will receive duplicate emails.

It accepts a list of transaction IDs to replay in the form of a text file, with
each transaction ID on a separate line:
```
896551ff-520f-4055-8452-36b4de64f0b4
fd18b432-4307-4fbb-a7f6-e149bace0bae
52b4686b-0ac4-4b6a-b3e0-3a8f3db47711
...
```

For example, to replay multiple transactions in file `bad-tx.txt` (with SMTP Rx
port forwarded on port 25 via `kubectl`):
```
$ victoria email recover cluster -f bad-tx.txt -o smtp.endpoint.com:25
```

For example, to replay single transaction `896551ff-520f-4055-8452-36b4de64f0b4` (with SMTP Rx
port forwarded on port 25 via `kubectl`):
```
$ victoria email recover cluster -id 896551ff-520f-4055-8452-36b4de64f0b4 -o localhost:25
```

The cluster name given here corresponds to a key in `storage_accounts` in the
config.

## Developer guide

### Prerequisites
- Python 3.7+
- Pipenv

### Quick start
1. Clone this repo
2. In the root of the repo, run `pipenv sync --dev`
3. You're good to go. You can run the plugin during development with 
   `pipenv run victoria email`
