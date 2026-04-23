from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from .notebook import Notebook

app = typer.Typer(help="notebooklm-py — chat with your documents using Claude")
console = Console()


@app.command()
def chat(
    files: list[Path] = typer.Argument(..., help="Documents to load (.txt, .md, .pdf)"),
    model: str = typer.Option("claude-opus-4-7", "--model", "-m"),
):
    """Load documents and start an interactive Q&A session."""
    nb = Notebook(model=model)

    for f in files:
        if not f.exists():
            console.print(f"[red]File not found:[/red] {f}")
            raise typer.Exit(1)
        nb.add_file(f)
        console.print(f"[green]✓[/green] Loaded [bold]{f.name}[/bold]")

    console.print(f"\n[dim]Loaded {len(nb.documents)} document(s). Type 'quit' to exit.[/dim]\n")

    while True:
        question = Prompt.ask("[bold blue]You[/bold blue]")
        if question.strip().lower() in {"quit", "exit", "q"}:
            break
        if not question.strip():
            continue

        console.print("\n[bold green]Assistant[/bold green]")
        answer_chunks = []
        try:
            for chunk in nb.stream(question):
                console.print(chunk, end="", markup=False)
                answer_chunks.append(chunk)
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")
        console.print("\n")


@app.command()
def ask(
    question: str = typer.Argument(...),
    files: list[Path] = typer.Option(..., "--file", "-f", help="Documents to load"),
    model: str = typer.Option("claude-opus-4-7", "--model", "-m"),
):
    """Ask a single question across documents (non-interactive)."""
    nb = Notebook(model=model)
    for f in files:
        nb.add_file(f)

    for chunk in nb.stream(question):
        print(chunk, end="", flush=True)
    print()
