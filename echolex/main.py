"""
EchoLex - Global Legal Research Engine

Main application entry point.

DISCLAIMER: This system is for RESEARCH PURPOSES ONLY.
It does not constitute legal advice. Always consult a licensed
attorney for legal matters in your jurisdiction.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from rich.console import Console
from rich.panel import Panel

from echolex.api.routes import router
from echolex.api.websocket import websocket_router


# Application metadata
APP_NAME = "EchoLex"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
EchoLex - Global Legal Research Engine

A comprehensive legal research platform providing:
- Case analysis across all legal domains (traffic violations to capital offenses)
- Judge scorecards with bench follow-rate analytics
- Predictive models for case outcomes, sentencing, and appeals
- Real-time legal updates and notifications
- Jurisdiction comparison and analytics

**DISCLAIMER**: This system is for RESEARCH PURPOSES ONLY.
It does not constitute legal advice. Always consult a licensed
attorney for legal matters in your jurisdiction.
"""

DISCLAIMER = """
╔══════════════════════════════════════════════════════════════════╗
║                    FOR RESEARCH PURPOSES ONLY                     ║
║                                                                   ║
║  This system provides legal information and analytics for         ║
║  research purposes. It does NOT constitute legal advice.          ║
║                                                                   ║
║  Always consult a licensed attorney for legal matters in          ║
║  your jurisdiction.                                               ║
╚══════════════════════════════════════════════════════════════════╝
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.warning(DISCLAIMER)

    # Initialize services
    # In production: connect to databases, load ML models, etc.

    yield

    # Shutdown
    logger.info(f"Shutting down {APP_NAME}")
    # In production: close connections, cleanup resources


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=APP_NAME,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(router, tags=["Legal Research"])
    app.include_router(websocket_router, tags=["Live Updates"])

    return app


# Create the application instance
app = create_app()


# CLI Interface
console = Console()


@click.group()
@click.version_option(version=APP_VERSION, prog_name=APP_NAME)
def cli():
    """EchoLex - Global Legal Research Engine CLI"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--workers", default=1, help="Number of workers")
def serve(host: str, port: int, reload: bool, workers: int):
    """Start the EchoLex API server."""
    console.print(Panel.fit(
        f"[bold blue]{APP_NAME}[/bold blue] v{APP_VERSION}\n"
        f"Global Legal Research Engine\n\n"
        f"[yellow]{DISCLAIMER}[/yellow]",
        title="Starting Server"
    ))

    console.print(f"\n[green]Server starting on http://{host}:{port}[/green]")
    console.print(f"[dim]API Docs: http://{host}:{port}/docs[/dim]")
    console.print(f"[dim]WebSocket: ws://{host}:{port}/ws/{{client_id}}[/dim]\n")

    uvicorn.run(
        "echolex.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level="info"
    )


@cli.command()
@click.argument("case_type")
@click.option("--severity", help="Case severity level")
@click.option("--jurisdiction", help="Jurisdiction code")
def predict(case_type: str, severity: str, jurisdiction: str):
    """
    Predict case outcome from command line.

    CASE_TYPE: Type of case (e.g., dui_dwi, murder_1, fraud)
    """
    from echolex.models.case import Case, CaseType, CaseSeverity
    from echolex.predictions.case_predictor import CasePredictor, OutcomeExplainer
    from uuid import uuid4
    from datetime import date

    console.print(Panel.fit(
        "[bold yellow]FOR RESEARCH PURPOSES ONLY[/bold yellow]\n"
        "This prediction does not constitute legal advice.",
        title="Disclaimer"
    ))

    try:
        # Parse case type
        try:
            ct = CaseType(case_type.lower())
        except ValueError:
            console.print(f"[red]Unknown case type: {case_type}[/red]")
            console.print(f"Available types: {', '.join(t.value for t in CaseType)}")
            return

        # Parse severity
        sev = CaseSeverity.MISDEMEANOR
        if severity:
            try:
                sev = CaseSeverity(severity.lower())
            except ValueError:
                console.print(f"[red]Unknown severity: {severity}[/red]")
                return

        # Create case
        case = Case(
            case_number="CLI-PREDICT",
            jurisdiction_id=uuid4(),
            court_id=uuid4(),
            primary_type=ct,
            severity=sev,
            filing_date=date.today(),
            defendant_id=uuid4()
        )

        # Predict
        predictor = CasePredictor()
        result = predictor.predict(case)

        # Display results
        console.print(f"\n[bold]Case Type:[/bold] {case_type}")
        console.print(f"[bold]Severity:[/bold] {sev.value}")
        console.print()

        explanation = OutcomeExplainer.explain_prediction(result)
        console.print(Panel(explanation, title="Prediction Result"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def case_types():
    """List all available case types."""
    from echolex.models.case import CaseType

    console.print(Panel.fit(
        "[bold]Available Case Types[/bold]",
        title=APP_NAME
    ))

    for ct in CaseType:
        console.print(f"  - {ct.value}")


@cli.command()
def severities():
    """List all severity levels."""
    from echolex.models.case import CaseSeverity

    console.print(Panel.fit(
        "[bold]Severity Levels[/bold]\n"
        "(From least to most severe)",
        title=APP_NAME
    ))

    for sev in CaseSeverity:
        console.print(f"  - {sev.value}")


@cli.command()
def info():
    """Display system information."""
    console.print(Panel.fit(
        f"[bold blue]{APP_NAME}[/bold blue] v{APP_VERSION}\n\n"
        f"Global Legal Research Engine\n\n"
        f"Features:\n"
        f"  • Case outcome prediction\n"
        f"  • Sentence prediction\n"
        f"  • Appeal analysis\n"
        f"  • Judge scorecards\n"
        f"  • Jurisdiction analytics\n"
        f"  • Real-time updates\n\n"
        f"[yellow]{DISCLAIMER}[/yellow]",
        title="System Information"
    ))


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
