"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """DeITy."""


if __name__ == "__main__":
    main(prog_name="deity")  # pragma: no cover
