"""victoria_email

A Victoria plugin for managing the FileTrust Rebuild for Email platform.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
from typing import List, Optional

import aiorun
import click
from victoria.plugin import Plugin

from . import load_test, schemas, reconstruct_mail


@click.group()
def root_cmd() -> None:
    """Perform various actions on the Rebuild for Email platform."""


@root_cmd.command()
@click.option(
    "-n",
    "--frequency",
    type=int,
    required=False,
    default=1,
    help="The number of emails to send per second of the test. Default: 1.")
@click.option("-e",
              "--endpoint",
              type=str,
              required=True,
              help="The SMTP endpoint (and optional port) to send to.")
@click.option("-t",
              "--duration",
              type=int,
              required=False,
              default=1,
              help="The duration in seconds of the test. Default: 1.")
@click.option("-r",
              "--recipient",
              type=str,
              required=True,
              help="The email recipient address.")
@click.option("-s",
              "--sender",
              type=str,
              required=True,
              help="The email sender address.")
@click.pass_obj
def loadtest(cfg: schemas.EmailConfig, frequency: int, endpoint: str,
             duration: int, recipient: str, sender: str) -> None:
    """Perform a load test on a cluster.
    
    \b
    Send a single email:
    $ victoria email loadtest -e smtp.example.com -s test@example.com -r test@example.com

    \b
    Send 46 mails per second for 60 seconds:
    $ victoria email loadtest -e smtp.example.com -n 46 -t 60 -s test@example.com -r test@example.com

    \b
    Send using a different port than port 25:
    $ victoria email loadtest -e smtp.example.com:465 -s test@example.com -r test@example.com
    """
    loop = aiorun.get_event_loop()
    loop.set_exception_handler(lambda loop, context: "Error")
    loop.run_until_complete(
        load_test.perform_load_test(frequency, endpoint, duration, recipient,
                                    sender, cfg.load_test))


@root_cmd.command()
@click.argument("cluster", nargs=1, type=str)
@click.option("-o",
              "--output",
              type=str,
              required=True,
              help="The directory to write reconstructed mail to.")
@click.option("-a", "--anon", type=bool, is_flag=True)
@click.option("-i",
              "--transaction-id",
              multiple=True,
              type=str,
              help="Cherry-pick GUIDs from blob storage to reconstruct. "
              "This bypasses dead letter scanning.")
@click.pass_obj
def reconstruct(cfg: schemas.EmailConfig, cluster: str, output: str,
                anon: bool, transaction_id: List[str]) -> None:
    """Reconstruct mail from blob storage.

    Can also scan dead letter queues to find mail that needs to be reconstructed.

    \b
    Reconstruct mail in dead letters:
    $ victoria email reconstruct uksprod1 -o output_dir

    \b
    Reconstruct a specific transaction ID
    $ victoria email reconstruct useprod2 -i <guid> -o output_dir

    \b
    Reconstruct a specific transaction ID, anonymising contents
    $ victoria email reconstruct useprod4 -i <guid> -o output_dir --anon
    """
    reconstruct_mail.reconstruct(cfg.mail_toil, cluster, output,
                                 transaction_id, anon)


# plugin entry point
plugin = Plugin(name="email",
                cli=root_cmd,
                config_schema=schemas.EmailConfigSchema())
