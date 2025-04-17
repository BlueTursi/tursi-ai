"""Command-line interface for Tursi AI model deployment."""
import os
import sys
import signal
import psutil
from enum import Enum
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint
from rich.table import Table
from . import __version__
from .engine import TursiEngine

# Create console for rich output
console = Console()

def print_help(command: Optional[str] = None):
    """Print help message."""
    if command == "up":
        console.print("""
[bold]Usage:[/bold]
  tursi up [OPTIONS] MODEL_NAME

[bold]Arguments:[/bold]
  MODEL_NAME  Name of the model to deploy (e.g., 'distilbert-base-uncased') [required]

[bold]Options:[/bold]
  --port, -p INTEGER           Port to run the API server on [default: 5000]
  --host TEXT                  Host to bind the API server to [default: 127.0.0.1]
  --quantization, -q TEXT      Quantization mode: 'dynamic' or 'static' [default: dynamic]
  --bits, -b INTEGER          Number of bits for quantization (4 or 8) [default: 8]
  --rate-limit, -r TEXT       API rate limit (e.g., '100/minute') [default: 100/minute]
  --cache-dir, -c PATH        Directory to cache models (default: ~/.tursi/models)
  -h, --help                  Show this message and exit

[bold]Example:[/bold]
  $ tursi up distilbert-base-uncased --port 8000 --quantization dynamic
""")
    else:
        console.print("""
[bold]Tursi AI[/bold] - Deploy AI models with unmatched simplicity

[bold]Usage:[/bold]
  tursi [OPTIONS] COMMAND [ARGS]...

[bold]Commands:[/bold]
  up        Start a model server
  down      Stop a running model server
  ps        List running models
  logs      View server logs
  stats     Show resource usage statistics

[bold]Options:[/bold]
  -h, --help     Show this message and exit
  -v, --version  Show version and exit
""")
    raise typer.Exit()

# Create Typer app instance
app = typer.Typer(
    help="Deploy AI models with unmatched simplicity",
    no_args_is_help=True,
    add_help_option=False,
)

# Define valid quantization modes
class QuantizationMode(str, Enum):
    DYNAMIC = "dynamic"
    STATIC = "static"

def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"Tursi AI version: {__version__}")
        raise typer.Exit()

def validate_bits(value: int) -> int:
    """Validate quantization bits."""
    if value not in (4, 8):
        raise typer.BadParameter("Quantization bits must be either 4 or 8")
    return value

@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    help: Optional[bool] = typer.Option(
        None,
        "--help",
        "-h",
        is_eager=True,
        callback=lambda x: print_help() if x else None,
        help="Show this message and exit",
    ),
):
    """Deploy AI models with unmatched simplicity."""
    pass

@app.command()
def up(
    model_name: str = typer.Argument(
        ...,  # Required argument
        help="Name of the model to deploy (e.g., 'distilbert-base-uncased')",
    ),
    port: int = typer.Option(
        5000,
        "--port",
        "-p",
        help="Port to run the API server on",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Host to bind the API server to",
    ),
    quantization_mode: QuantizationMode = typer.Option(
        QuantizationMode.DYNAMIC,
        "--quantization",
        "-q",
        help="Quantization mode: 'dynamic' or 'static'",
        case_sensitive=False,
    ),
    quantization_bits: int = typer.Option(
        8,
        "--bits",
        "-b",
        help="Number of bits for quantization (4 or 8)",
        callback=validate_bits,
    ),
    rate_limit: str = typer.Option(
        "100/minute",
        "--rate-limit",
        "-r",
        help="API rate limit (e.g., '100/minute')",
    ),
    cache_dir: Optional[Path] = typer.Option(
        None,
        "--cache-dir",
        "-c",
        help="Directory to cache models (default: ~/.tursi/models)",
    ),
    help: Optional[bool] = typer.Option(
        None,
        "--help",
        "-h",
        is_eager=True,
        callback=lambda x: print_help("up") if x else None,
        help="Show this message and exit",
    ),
):
    """Start a model server.

    Example:
        $ tursi up distilbert-base-uncased --port 8000 --quantization dynamic
    """
    try:
        # Show welcome message
        console.print(
            Panel(
                "[bold]Tursi AI[/bold] - Deploy AI models with unmatched simplicity",
                style="blue",
            )
        )

        # Initialize engine
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Initializing Tursi engine...", total=None)
            engine = TursiEngine()

            # Set cache directory if provided
            if cache_dir:
                engine.MODEL_CACHE_DIR = cache_dir
                engine.setup_model_cache()

            # Configure quantization
            engine.QUANTIZATION_MODE = quantization_mode.value
            engine.QUANTIZATION_BITS = quantization_bits

            # Create Flask app
            progress.add_task("Creating API server...", total=None)
            app = engine.create_app(
                model_name=model_name,
                rate_limit=rate_limit,
            )

            # Show success message
            console.print("\n[green]✓[/green] Model server started successfully!")
            console.print(f"\nAPI server running at: http://{host}:{port}")
            console.print("Available endpoints:")
            console.print("  • POST /predict - Make predictions")
            console.print("  • GET  /health - Check server health")

            # Run Flask app
            app.run(host=host, port=port)

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

def find_tursi_processes() -> List[psutil.Process]:
    """Find all running Tursi model server processes."""
    tursi_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'tursi' in ' '.join(proc.info['cmdline']) and 'up' in proc.info['cmdline']:
                tursi_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return tursi_processes

@app.command()
def down():
    """Stop a running model server."""
    try:
        processes = find_tursi_processes()

        if not processes:
            console.print("[yellow]No running Tursi model servers found[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Stopping model servers...", total=None)

            for proc in processes:
                try:
                    # Try graceful shutdown first
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
                    except psutil.TimeoutExpired:
                        # If graceful shutdown fails, force kill
                        proc.kill()
                        proc.wait()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            progress.update(task, completed=True)

        console.print("\n[green]✓[/green] Model servers stopped successfully!")

    except Exception as e:
        console.print(f"\n[red]Error stopping model servers:[/red] {str(e)}")
        console.print("You can manually stop the server by pressing Ctrl+C in the terminal where it's running")
        raise typer.Exit(1)

@app.command()
def ps():
    """List running models."""
    table = Table(title="Running Models")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Model", style="magenta")
    table.add_column("Port", justify="right", style="green")
    table.add_column("Status", style="blue")
    table.add_column("Uptime", justify="right", style="yellow")

    console.print(table)
    console.print("[yellow]⚠️ Process monitoring will be available in v0.4.0[/yellow]")
    console.print("For now, use your system's process manager to view running Tursi instances")
    console.print("\nTo track progress, visit: https://github.com/BlueTursi/tursi-ai/issues")

@app.command()
def logs():
    """View server logs."""
    console.print("[yellow]⚠️ Log viewing will be available in v0.4.0[/yellow]")
    console.print("For now, logs are printed to the console where the server is running")
    console.print("\nTo track progress, visit: https://github.com/BlueTursi/tursi-ai/issues")
    raise typer.Exit(1)

@app.command()
def stats():
    """Show resource usage statistics."""
    console.print("[yellow]⚠️ Resource monitoring will be available in v0.4.0[/yellow]")
    console.print("For now, use your system's resource monitor to track memory and CPU usage")
    console.print("\nTo track progress, visit: https://github.com/BlueTursi/tursi-ai/issues")
    raise typer.Exit(1)

def main():
    """Deploy AI models with unmatched simplicity."""
    app()
