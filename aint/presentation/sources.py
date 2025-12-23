from pathlib import Path

from aint.domain.gen import GeneratedSource
from aint.domain.syntax import SourceFile


def load_sources(sources: list[Path]) -> list[SourceFile]:
    return [
        SourceFile(path=str(source), content=source.read_text())
        for source in sources
    ]


def save_generated(
    base_path: str | Path,
    generated: list[GeneratedSource]
) -> None:
    for source in generated:
        Path(base_path, source.path).write_text(source.content)
