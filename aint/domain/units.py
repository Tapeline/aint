from dataclasses import dataclass

from aint.domain.syntax import ParseRule


@dataclass
class Unit:
    used_rule: ParseRule
    slots: dict[str, str]
    attributes: dict[str, str]

    @property
    def type(self) -> str:
        return self.used_rule.name


@dataclass
class Workspace:
    units: list[Unit]
    attributes: dict[str, str]

    def units_of_types(self, *unit_types: str) -> list[Unit]:
        return [
            unit for unit in self.units
            if unit.type in unit_types
        ]


@dataclass
class LinkingRule:
    name: str
    select: list[str]
    rule: str
