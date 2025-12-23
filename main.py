import os
from pathlib import Path

from openai import Client

from aint.domain.flow import run_compiler_flow
from aint.infrastructure.ai.client import AI
from aint.infrastructure.ai.impl import (
    AIRuleExplainer,
    AISourceParser,
    AIUnitCompiler, AIUnitLinker,
)
from aint.presentation.definition_loaders import YamlDefLoader
from aint.presentation.sources import load_sources, save_generated


def main():
    client = Client(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1"
    )
    ai = AI(client, "kwaipilot/kat-coder-pro:free")
    loader = YamlDefLoader(Path("test"))
    explainer = AIRuleExplainer(ai)
    parser = AISourceParser(ai)
    linker = AIUnitLinker(ai)
    compiler = AIUnitCompiler(ai)
    sources = load_sources([Path("test/test.txt")])
    generated = run_compiler_flow(
        loader, explainer, sources, parser, linker, compiler
    )
    save_generated("test", generated)


if __name__ == "__main__":
    main()
