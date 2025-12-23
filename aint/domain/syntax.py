from dataclasses import dataclass


@dataclass
class SourceFile:
    path: str
    content: str


@dataclass
class ParseRule:
    name: str
    slots: dict[str, str]
    pattern: str
