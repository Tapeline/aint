from dataclasses import dataclass
from pathlib import Path

import adaptix
import yaml

from aint.domain.flow import RuleParser
from aint.domain.gen import CompilationRule
from aint.domain.syntax import ParseRule
from aint.domain.units import LinkingRule


@dataclass
class _ParseRuleDef:
    slots: dict[str, str]
    pattern: str


@dataclass
class _LinkRuleDef:
    select: list[str]
    rule: str


@dataclass
class _CompileRuleDef:
    path: str
    template: str


class YamlDefLoader(RuleParser):
    def __init__(
        self,
        base_path: Path,
        parse_rules_filename: str = "grammar.yml",
        link_rules_filename: str = "linking.yml",
        compile_rules_filename: str = "compiling.yml",
    ) -> None:
        self.base_path = base_path
        self.parse_rules_path = base_path / parse_rules_filename
        self.link_rules_path = base_path / link_rules_filename
        self.compile_rules_path = base_path / compile_rules_filename

    def get_parse_rules(self) -> list[ParseRule]:
        defs = adaptix.load(
            yaml.safe_load(self.parse_rules_path.read_text()),
            dict[str, _ParseRuleDef]
        )
        return [
            ParseRule(name, rule.slots, rule.pattern)
            for name, rule in defs.items()
        ]

    def get_linking_rules(self) -> list[LinkingRule]:
        defs = adaptix.load(
            yaml.safe_load(self.link_rules_path.read_text()),
            dict[str, _LinkRuleDef]
        )
        return [
            LinkingRule(name, rule.select, rule.rule)
            for name, rule in defs.items()
        ]

    def get_compilation_rules(self) -> list[CompilationRule]:
        defs = adaptix.load(
            yaml.safe_load(self.compile_rules_path.read_text()),
            dict[str, _CompileRuleDef]
        )
        return [
            CompilationRule(unit_type, rule.path, rule.template)
            for unit_type, rule in defs.items()
        ]
