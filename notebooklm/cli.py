from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
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
        console.print(f"[green]✓[/green] Loaded file [bold]{f.name}[/bold]")

    for url in urls:
        if _is_youtube(url):
            console.print(f"[yellow]⏳[/yellow] Fetching YouTube transcript: {url}")
            nb.add_youtube(url, lang=lang)
            console.print(f"[green]✓[/green] Loaded [bold]{nb.documents[-1].name}[/bold]")
        else:
            console.print(f"[red]Unknown URL type (use --youtube for YouTube):[/red] {url}")
            raise typer.Exit(1)


@app.command()
def chat(
    files: list[Path] = typer.Argument(default=None, help="Local files (.txt, .md, .pdf)"),
    youtube: list[str] = typer.Option([], "--youtube", "-y", help="YouTube URL(s)"),
    lang: str = typer.Option("zh-Hant,zh,en", "--lang", "-l", help="Subtitle language preference"),
    model: str = typer.Option("claude-opus-4-7", "--model", "-m"),
):
    """Interactive Q&A session over local files and/or YouTube videos."""
    if not files and not youtube:
        console.print("[red]Provide at least one file or --youtube URL.[/red]")
        raise typer.Exit(1)

    nb = Notebook(model=model)
    _load_sources(nb, files or [], youtube, lang)

    console.print(f"\n[dim]Loaded {len(nb.documents)} source(s). Type 'quit' to exit.[/dim]\n")

    while True:
        question = Prompt.ask("[bold blue]You[/bold blue]")
        if question.strip().lower() in {"quit", "exit", "q"}:
            break
        if not question.strip():
            continue

        console.print("\n[bold green]Assistant[/bold green]")
        try:
            for chunk in nb.stream(question):
                console.print(chunk, end="", markup=False)
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")
        console.print("\n")


@app.command()
def ask(
    question: str = typer.Argument(...),
    files: list[Path] = typer.Option(..., "--file", "-f", help="Documents to load"),
    model: str = typer.Option("claude-opus-4-7", "--model", "-m"),
):
    """Ask a single question across local files and/or YouTube videos (non-interactive)."""
    if not files and not youtube:
        console.print("[red]Provide at least one --file or --youtube URL.[/red]")
        raise typer.Exit(1)

    nb = Notebook(model=model)
    _load_sources(nb, files, youtube, lang)

    for chunk in nb.stream(question):
        print(chunk, end="", flush=True)
    print()
