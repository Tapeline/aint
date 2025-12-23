from abc import abstractmethod
from asyncio import Protocol

from aint.domain.gen import CompilationRule, GeneratedSource
from aint.domain.syntax import ParseRule, SourceFile
from aint.domain.units import LinkingRule, Unit, Workspace


class RuleParser(Protocol):
    @abstractmethod
    def get_parse_rules(self) -> list[ParseRule]:
        raise NotImplementedError

    @abstractmethod
    def get_linking_rules(self) -> list[LinkingRule]:
        raise NotImplementedError

    @abstractmethod
    def get_compilation_rules(self) -> list[CompilationRule]:
        raise NotImplementedError


class RuleExplainer(Protocol):
    @abstractmethod
    def explain_rules(self, rules: list[ParseRule]) -> str:
        raise NotImplementedError


class SourceParser(Protocol):
    @abstractmethod
    def parse_source(
        self,
        rules: dict[str, ParseRule],
        source: SourceFile,
        parse_algo: str
    ) -> list[Unit]:
        raise NotImplementedError


class UnitLinker(Protocol):
    @abstractmethod
    def apply_rule(self, workspace: Workspace, rule: LinkingRule) -> None:
        raise NotImplementedError


class UnitCompiler(Protocol):
    @abstractmethod
    def compile(
        self, workspace: Workspace, rule: CompilationRule
    ) -> list[GeneratedSource]:
        raise NotImplementedError


def run_compiler_flow(
    rule_parser: RuleParser,
    explainer: RuleExplainer,
    sources: list[SourceFile],
    source_parser: SourceParser,
    linker: UnitLinker,
    compiler: UnitCompiler,
    default_ws_attributes: dict[str, str] | None = None,
) -> list[GeneratedSource]:
    parse_rules = rule_parser.get_parse_rules()
    parse_rules_dict = {rule.name: rule for rule in parse_rules}
    link_rules = rule_parser.get_linking_rules()
    compile_rules = rule_parser.get_compilation_rules()
    parser_algo = explainer.explain_rules(parse_rules)
    units = []
    for source in sources:
        units.extend(
            source_parser.parse_source(
                parse_rules_dict, source, parser_algo
            )
        )
    workspace = Workspace(units, attributes=default_ws_attributes or {})
    for link_rule in link_rules:
        linker.apply_rule(workspace, link_rule)
    generated = []
    for compile_rule in compile_rules:
        generated.extend(compiler.compile(workspace, compile_rule))
    return generated
