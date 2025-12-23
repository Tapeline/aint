from dataclasses import dataclass


@dataclass
class GeneratedSource:
    path: str
    content: str


@dataclass
class CompilationRule:
    unit_type: str
    path: str
    template: str
