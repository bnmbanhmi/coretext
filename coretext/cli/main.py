import typer
from coretext.cli import commands

app = typer.Typer()
app.add_typer(commands.app, name="commands")

if __name__ == "__main__":
    app()