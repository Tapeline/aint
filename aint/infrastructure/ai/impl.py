import json
from dataclasses import dataclass
from typing import Any

import adaptix

from aint.domain.flow import (
    RuleExplainer,
    SourceParser,
    UnitCompiler,
    UnitLinker,
)
from aint.domain.gen import CompilationRule, GeneratedSource
from aint.domain.syntax import ParseRule, SourceFile
from aint.domain.units import LinkingRule, Unit, Workspace
from aint.infrastructure.ai.client import AI
from aint.infrastructure.ai.templates import (
    COMPILE_UNIT_PROMPT, EXPLAIN_PROMPT,
    LINK_UNITS_PROMPT, PARSE_SOURCE_PROMPT,
    render_templates,
)


@dataclass
class AIRuleExplainer(RuleExplainer):
    ai: AI

    def explain_rules(self, rules: list[ParseRule]) -> str:
        return self.ai.request(
            *render_templates(
                EXPLAIN_PROMPT,
                data={"rules": rules}
            )
        )


@dataclass
class _ParsedUnit:
    rule: str
    slots: dict[str, Any]


@dataclass
class AISourceParser(SourceParser):
    ai: AI

    def parse_source(
        self,
        rules: dict[str, ParseRule],
        source: SourceFile,
        parse_algo: str
    ) -> list[Unit]:
        units_json = self.ai.request(
            *render_templates(
                PARSE_SOURCE_PROMPT,
                data={"parse_algo": parse_algo, "code": source.content}
            )
        ).removeprefix("```json").removesuffix("```")
        units_list = json.loads(units_json)
        parsed_units = adaptix.load(units_list, list[_ParsedUnit])
        return [
            Unit(
                used_rule=rules[parsed_unit.rule],
                slots=parsed_unit.slots,
                attributes={}
            )
            for parsed_unit in parsed_units
        ]


@dataclass
class AIUnitLinker(UnitLinker):
    ai: AI

    def apply_rule(self, workspace: Workspace, rule: LinkingRule) -> None:
        units = workspace.units_of_types(*rule.select)
        changes_json = self.ai.request(
            *render_templates(
                LINK_UNITS_PROMPT,
                data={"units": units, "workspace": workspace, "rule": rule}
            )
        ).removeprefix("```json").removesuffix("```")
        changes_list = json.loads(changes_json)
        for change in changes_list:
            if change["type"] == "set_workspace_attr":
                workspace.attributes[change["name"]] = change["value"]
            elif change["type"] == "set_unit_attr":
                units[change["index"]].attributes[change["name"]] = change["value"]


@dataclass
class AIUnitCompiler(UnitCompiler):
    ai: AI

    def compile(
        self, workspace: Workspace, rule: CompilationRule
    ) -> list[GeneratedSource]:
        units = workspace.units_of_types(rule.unit_type)
        generated = []
        for unit in units:
            generated_json = self.ai.request(
                *render_templates(
                    COMPILE_UNIT_PROMPT,
                    data={"unit": unit, "workspace": workspace, "rule": rule}
                )
            ).removeprefix("```json").removesuffix("```")
            generated_dict = json.loads(generated_json)
            generated.append(adaptix.load(generated_dict, GeneratedSource))
        return generated
