import os
from pathlib import Path

import click
import openai

from aint.domain.flow import run_compiler_flow
from aint.domain.syntax import SourceFile
from aint.infrastructure.ai.client import AI
from aint.infrastructure.ai.impl import (
    AIRuleExplainer,
    AISourceParser,
    AIUnitCompiler, AIUnitLinker,
)
from aint.presentation.definition_loaders import YamlDefLoader
from aint.presentation.sources import load_sources, save_generated


def err_exit(text: str) -> None:
    """Print error and exit."""
    click.echo(
        click.style(text, fg="red"),
        err=True,
        color=True
    )
    raise click.exceptions.Exit(1)


@click.command()
def aint() -> None:
    click.echo("aint v0.0.0")


@click.group()
def aint_group():
    """Aint CLI tool."""


@aint_group.command("compile")
@click.argument("input_file", type=click.File("r"))
@click.argument(
    "output_base_dir",
    type=click.Path(dir_okay=True, file_okay=False)
)
def compile_command(input_file, output_base_dir):
    client = openai.Client(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1"
    )
    ai = AI(client, "kwaipilot/kat-coder-pro:free")
    loader = YamlDefLoader(Path(input_file.name).parent)
    explainer = AIRuleExplainer(ai)
    parser = AISourceParser(ai)
    linker = AIUnitLinker(ai)
    compiler = AIUnitCompiler(ai)
    sources = [SourceFile(input_file.name, input_file.read())]
    generated = run_compiler_flow(
        loader, explainer, sources, parser, linker, compiler
    )
    save_generated(output_base_dir, generated)
