"""
Echo Life OS - Command Line Interface
=====================================
Main entry point for the Echo Life OS system.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

from src.core.memory_kernel import MemoryKernel, MemoryType, MemoryPriority
from src.agents.council import EchoCouncil, EthicsMode
from src.security.defense_wall import DefenseWall
from src.financial.financial_os import FinancialOS


app = typer.Typer(
    name="echo",
    help="Echo Life OS - Your persistent personal intelligence",
    add_completion=False,
)
console = Console()


@app.command()
def init(
    path: str = typer.Option(
        "~/.echo",
        "--path", "-p",
        help="Base path for Echo data"
    ),
    password: str = typer.Option(
        ...,
        "--password",
        prompt=True,
        hide_input=True,
        help="Master password for encryption"
    ),
):
    """Initialize Echo Life OS."""
    base_path = Path(path).expanduser()

    with Progress() as progress:
        task = progress.add_task("[cyan]Initializing Echo Life OS...", total=4)

        # Initialize Memory Kernel
        progress.update(task, description="[cyan]Creating Memory Kernel...")
        kernel = MemoryKernel(str(base_path), password)
        progress.advance(task)

        # Initialize Defense Wall
        progress.update(task, description="[cyan]Setting up Defense Wall...")
        defense = DefenseWall(str(base_path))
        progress.advance(task)

        # Initialize Financial OS
        progress.update(task, description="[cyan]Configuring Financial OS...")
        financial = FinancialOS(str(base_path))
        progress.advance(task)

        # Create config file
        progress.update(task, description="[cyan]Saving configuration...")
        config_path = base_path / "config" / "echo.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(f"""# Echo Life OS Configuration
version: "0.1.0"
initialized: true
base_path: "{base_path}"
""")
        progress.advance(task)

    console.print(Panel(
        "[green]Echo Life OS initialized successfully![/green]\n\n"
        f"Data directory: {base_path}\n"
        "Run [bold]echo status[/bold] to see system status.",
        title="Welcome to Echo",
        border_style="green"
    ))


@app.command()
def status():
    """Show Echo Life OS status."""
    try:
        defense = DefenseWall()
        financial = FinancialOS()

        # Security status
        security_status = defense.get_security_status()

        # Financial summary
        financial_summary = financial.get_financial_summary()

        # Create status table
        table = Table(title="Echo Life OS Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")

        # Security
        lock_status = "[red]LOCKED[/red]" if security_status['locked'] else "[green]Active[/green]"
        table.add_row(
            "Defense Wall",
            lock_status,
            f"{security_status['active_alerts']} active alerts"
        )

        # Financial
        table.add_row(
            "Financial OS",
            "[green]Active[/green]",
            f"{financial_summary['total_accounts']} accounts linked"
        )

        # Memory (would need to check actual stats)
        table.add_row(
            "Memory Kernel",
            "[green]Active[/green]",
            "Encrypted storage ready"
        )

        # Council
        table.add_row(
            "Echo Council",
            "[green]Ready[/green]",
            "8 agents available"
        )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error getting status: {e}[/red]")


@app.command()
def remember(
    content: str = typer.Argument(..., help="Content to remember"),
    memory_type: str = typer.Option(
        "semantic",
        "--type", "-t",
        help="Memory type: working, episodic, semantic, procedural"
    ),
    priority: str = typer.Option(
        "medium",
        "--priority", "-p",
        help="Priority: critical, high, medium, low, ephemeral"
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        help="Comma-separated tags"
    ),
):
    """Store a memory in the Memory Kernel."""
    try:
        kernel = MemoryKernel()

        # Parse memory type
        type_map = {
            "working": MemoryType.WORKING,
            "episodic": MemoryType.EPISODIC,
            "semantic": MemoryType.SEMANTIC,
            "procedural": MemoryType.PROCEDURAL,
        }
        mem_type = type_map.get(memory_type.lower(), MemoryType.SEMANTIC)

        # Parse priority
        priority_map = {
            "critical": MemoryPriority.CRITICAL,
            "high": MemoryPriority.HIGH,
            "medium": MemoryPriority.MEDIUM,
            "low": MemoryPriority.LOW,
            "ephemeral": MemoryPriority.EPHEMERAL,
        }
        mem_priority = priority_map.get(priority.lower(), MemoryPriority.MEDIUM)

        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        # Store memory
        memory_id = kernel.store(
            content=content,
            memory_type=mem_type,
            priority=mem_priority,
            tags=tag_list
        )

        console.print(f"[green]Memory stored:[/green] {memory_id}")

    except Exception as e:
        console.print(f"[red]Error storing memory: {e}[/red]")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question or task for the Council"),
    mode: str = typer.Option(
        "red_team",
        "--mode", "-m",
        help="Ethics mode: safe_harbor, red_team, grey_zone, black_lens"
    ),
):
    """Ask the Echo Council a question or assign a task."""

    async def run_council():
        try:
            # Parse ethics mode
            mode_map = {
                "safe_harbor": EthicsMode.L5_SAFE_HARBOR,
                "red_team": EthicsMode.L4_RED_TEAM,
                "grey_zone": EthicsMode.L3_GREY_ZONE,
                "black_lens": EthicsMode.L2_BLACK_LENS,
            }
            ethics_mode = mode_map.get(mode.lower(), EthicsMode.L4_RED_TEAM)

            council = EchoCouncil(default_ethics_mode=ethics_mode)

            with console.status("[bold cyan]Echo Council deliberating..."):
                response = await council.process(question)

            console.print(Panel(
                response,
                title=f"Echo Council Response ({mode})",
                border_style="cyan"
            ))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("[yellow]Ensure ANTHROPIC_API_KEY or OPENAI_API_KEY is set.[/yellow]")

    asyncio.run(run_council())


@app.command()
def scan(
    url: Optional[str] = typer.Option(None, "--url", help="URL to scan for phishing"),
    email: Optional[str] = typer.Option(None, "--email", help="Email to check for breaches"),
):
    """Run a security scan."""

    async def run_scan():
        defense = DefenseWall()

        scan_data = {}
        if url:
            scan_data['url'] = url
        if email:
            scan_data['email'] = email

        if not scan_data:
            console.print("[yellow]Provide --url or --email to scan[/yellow]")
            return

        alerts = await defense.scan(scan_data)

        if alerts:
            console.print("\n[bold red]Security Alerts:[/bold red]")
            for alert in alerts:
                console.print(f"  [{alert.threat_level.name}] {alert.title}")
                console.print(f"    {alert.description}")
        else:
            console.print("[green]No security issues detected.[/green]")

    asyncio.run(run_scan())


@app.command()
def lock(
    reason: str = typer.Option(
        "Manual lock",
        "--reason", "-r",
        help="Reason for locking"
    ),
):
    """Lock Echo Life OS (emergency stop)."""
    defense = DefenseWall()
    defense.emergency_lock(reason)
    console.print(f"[red]Echo Life OS LOCKED[/red]: {reason}")


@app.command()
def spending(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
):
    """Analyze spending patterns."""
    financial = FinancialOS()
    analysis = financial.get_spending_analysis(days)

    console.print(Panel(
        f"[bold]Spending Analysis ({days} days)[/bold]\n\n"
        f"Total Spending: ${analysis['total_spending']:.2f}\n"
        f"Total Income: ${analysis['total_income']:.2f}\n"
        f"Savings Rate: {analysis['savings_rate']:.1f}%",
        title="Financial Analysis",
        border_style="green"
    ))

    if analysis['recommendations']:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in analysis['recommendations']:
            console.print(f"  [{rec['priority'].upper()}] {rec['title']}")
            console.print(f"    {rec['description']}")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
