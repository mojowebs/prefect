"""
Command line interface for managing storage settings
"""
import typer
from rich.pretty import Pretty

from prefect.cli.base import app, console, exit_with_error, exit_with_success
from prefect.client import OrionClient
from prefect.utilities.asyncio import sync_compatible

storage_config_app = typer.Typer(
    name="storage",
    help="Commands for managing storage settings",
)
app.add_typer(storage_config_app)


@storage_config_app.command()
@sync_compatible
async def configure(storage_type: str):
    import pendulum

    valid_storageblocks = {"local", "orion", "s3"}
    if storage_type not in valid_storageblocks:
        exit_with_error(
            f"Invalid storage type: pick one of {list(valid_storageblocks)}"
        )

    async with OrionClient() as client:
        await client.update_block_name(
            name="ORION-CONFIG-STORAGE",
            new_name=f"ORION-CONFIG-STORAGE-ARCHIVED-{pendulum.now('UTC')}",
            raise_for_status=False,
        )

        if storage_type == "local":
            await client.create_block(
                name="ORION-CONFIG-STORAGE", blockref="localstorage-block"
            )
        elif storage_type == "orion":
            await client.create_block(
                name="ORION-CONFIG-STORAGE", blockref="orionstorage-block"
            )
        elif storage_type == "s3":
            console.print("Follow the prompts to configure s3 storage")
            s3_data = dict()
            s3_data["aws_access_key_id"] = typer.prompt("AWS access_key_id")
            s3_data["aws_secret_access_key"] = typer.prompt("AWS secret_access_key")
            s3_data["aws_session_token"] = typer.prompt("AWS session_token")
            s3_data["profile_name"] = typer.prompt("AWS profile_name")
            s3_data["region_name"] = typer.prompt("AWS region_name")
            s3_data["bucket"] = typer.prompt(
                "What s3 bucket would you like to persist data to?"
            )

            await client.create_block(
                name="ORION-CONFIG-STORAGE", blockref="s3storage-block", **s3_data
            )

        exit_with_success("Successfully configured Orion storage location!")
