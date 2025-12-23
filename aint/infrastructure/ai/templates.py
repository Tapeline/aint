import textwrap
from typing import Any

from jinja2 import Environment, Template


def _t(text: str) -> Template:
    return Environment().from_string(textwrap.dedent(text))


def render_templates(
    templates: tuple[Template, Template],
    data: dict[str, Any]
) -> tuple[str, str]:
    sys_template, user_template = templates
    sys_template_s = sys_template.render(**data)
    user_template_s = user_template.render(**data)
    return sys_template_s, user_template_s


EXPLAIN_PROMPT = (
    _t(
        """
        <role>You're an AI-powered compiler.</role> 
        <user-input>
            A definition of a language in semi-free form. `$` denotes a
            slot (variable) in syntactic construction, `#` starts a line
            comment.
        </user-input>
        <task>
            Based on definition given by user, create instructions for LLM
            to parse programs using provided grammar. 
        </task>
        <output>
            <format>XML</format>
            <template>
                <steps>
                    <step>Step to parse</step>
                </steps>
                <rules>
                    <rule>
                        <name>Rule name exactly as in input data</name>
                        <description>Rule description</description>
                        <slots>
                            <slot>
                                <name>Slot name exactly as in input data</name>
                                <type>Slot type exactly as in input data</type>
                                <description>Slot description</description>
                            </slot>
                        </slots>
                        <pattern>Rule pattern exactly as in input data</pattern>
                    </rule>
                </rules>
            </template>
            <example>
                <steps>
                    <step>Parse the input text to identify and extract syntactic constructions based on the provided grammar rules.</step>
                    <step>For each identified construction, match the pattern and extract the slot values according to their types.</step>
                    <step>Validate that the extracted slot values conform to their specified types (e.g., string, integer, etc.).</step>
                    <step>Generate a structured representation of the parsed input, including the rule name, slot names, slot types, and extracted values.</step>
                    <step>Return the structured representation as the output of the parsing process.</step>
                </steps>
                <rules>
                    <rule>
                        <name>addition</name>
                        <description>Rule for parsing addition operations in the language.</description>
                        <slots>
                            <slot>
                                <name>a</name>
                                <type>string</type>
                                <description>The first operand in the addition operation.</description>
                            </slot>
                            <slot>
                                <name>b</name>
                                <type>string</type>
                                <description>The second operand in the addition operation.</description>
                            </slot>
                        </slots>
                        <pattern>add $a to $b</pattern>
                    </rule>
                </rules>
            </example>
        </output>
        """
    ),
    _t(
        """
        {% for rule in rules %}
        <rule>
            <name>{{ rule.name }}</name>
            <slots>
                {% for name, type in rule.slots.items() %}
                <slot name="{{ name }}" type="{{ type }}"/>
                {% endfor %}
            </slots>
            <pattern>
                {{ rule.pattern }}
            </pattern>
        </rule>
        {% endfor %}
        """
    )
)

PARSE_SOURCE_PROMPT = (
    _t(
        """
        <role>You're an AI-powered compiler.</role> 
        <user-input>A program in defined language.</user-input>
        <parse-instructions>{{ parse_algo }}</parse-instructions>
        <task>Based on given instructions parse given program.</task>
        <output>
            <format>JSON list</format>
            <template>
                [{"rule": parse rule used name, 
                "slots": {slot name: slot value}}]
            </template>
            <example>
                [{"rule": "addition", "slots": {"a": "1", "b": "2"}}]
            </example>
        </output>
        """
    ),
    _t(
        """
        <code>{{ code }}</code>
        """
    )
)

LINK_UNITS_PROMPT = (
    _t(
        """
        <role>You're an AI-powered compiler.</role> 
        <user-input>
            A list of compilation units and workspace attributes
            followed by a some rule.
        </user-input>
        <task>
            Based on given rule carry out attribute modification (if needed)
            on every affected unit and modify workspace attributes (if needed).
        </task>
        <output>
            <format>JSON list of modifications</format>
            <template>
                [
                    {
                        "type": "set_workspace_attr", 
                        "name": attr name, 
                        "value": attr value
                    },
                    {
                        "type": "set_unit_attr",
                        "index": index of unit in input list starting from 0,
                        "name": attr name, 
                        "value": attr value
                    }
                ]
            </template>
            <example>
                [
                    {
                        "type": "set_workspace_attr", 
                        "name": "package_path",
                        "value": "com.my.package"
                    },
                    {
                        "type": "set_unit_attr",
                        "index": 425,
                        "name": "used_by", 
                        "value": ["unit 1234", "unit 5234"]
                    }
                ]
            </example>
        </output>
        """
    ),
    _t(
        """
        <units>
            {% for unit in units %}
            <unit>
                <type>{{ unit.type }}</type>
                <slots>
                    {% for name, value in unit.slots.items() %}
                    <{{ name }}>{{ value }}</{{ name }}>
                    {% endfor %}
                </slots>
                <attributes>
                    {% for name, value in unit.attributes.items() %}
                    <{{ name }}>{{ value }}</{{ name }}>
                    {% endfor %}
                </attributes>
            </unit>
            {% endfor %}
        </units>
        <workspace-attributes>
            {% for name, value in workspace.attributes.items() %}
            <{{ name }}>{{ value }}</{{ name }}>
            {% endfor %}
        </workspace-attributes>
        <rule>
            {{ rule }}
        </rule>
        """
    )
)

COMPILE_UNIT_PROMPT = (
    _t(
        """
        <role>You're an AI-powered compiler.</role> 
        <user-input>
            A compilation unit, 
            workspace attributes,
            generated file path template,
            compilation template.
        </user-input>
        <task>Compile unit and create path from template.</task>
        <output>
            <format>JSON</format>
            <template>
                {
                    "path": file path,
                    "content": compiled code
                }
            </template>
            <example>
                {
                    "path": "com/my/package/file.py",
                    "content": "print('Hello, World')"
                }
            </example>
        </output>
        """
    ),
    _t(
        """
        <unit>
            <type>{{ unit.type }}</type>
            <slots>
                {% for name, value in unit.slots.items() %}
                <{{ name }}>{{ value }}</{{ name }}>
                {% endfor %}
            </slots>
            <attributes>
                {% for name, value in unit.attributes.items() %}
                <{{ name }}>{{ value }}</{{ name }}>
                {% endfor %}
            </attributes>
        </unit>
        <workspace-attributes>
            {% for name, value in workspace.attributes.items() %}
            <{{ name }}>{{ value }}</{{ name }}>
            {% endfor %}
        </workspace-attributes>
        <path-template>
            {{ rule.path }}
        </path-template>
        <code-template>
            {{ rule.template }}
        </code-template>
        """
    )
)
