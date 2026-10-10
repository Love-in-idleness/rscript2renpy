"""Flatten text controls not understood by the shared RScript runtime."""

import ast
import io
import re
import tokenize


CONTROL = re.compile(r"\^(?:g[ \t]*-?[0-9]+|a[0-9]{3}|s[0-9]|v[-0-9]+|[agdsw][0-9]+|[cf][A-Za-z]|[A-Za-z])", re.I)
SUPPORTED = re.compile(r"\^(?:[binm]|[dw][0-9]+|s[0-9]|v[-0-9]+|g[ \t]*-?[0-9]+|a[0-9]{3}|c[bgkopsrvwy]|f[mg])\Z", re.I)
TEXT_COMMANDS = {"_say", "_append", "_oload", "_khime_say", "_khime_append",
                 "_rscript_say", "_rscript_append"}


def flatten_unsupported_text_controls(text: str) -> str:
    output = []
    for line in text.splitlines(keepends=True):
        command = line.lstrip().split(maxsplit=1)
        if not command or command[0] not in TEXT_COMMANDS:
            output.append(line)
            continue
        replacements = []
        flattened = []
        for token in tokenize.generate_tokens(io.StringIO(line).readline):
            if token.type != tokenize.STRING:
                continue
            try:
                value = ast.literal_eval(token.string)
            except (SyntaxError, ValueError):
                continue
            if not isinstance(value, str):
                continue

            def replace(match):
                control = match.group()
                if SUPPORTED.fullmatch(control):
                    return control
                if control not in flattened:
                    flattened.append(control)
                return ""

            changed = CONTROL.sub(replace, value)
            if changed != value:
                replacements.append((token.start[1], token.end[1], repr(changed)))
        for start, end, replacement in reversed(replacements):
            line = line[:start] + replacement + line[end:]
        if flattened:
            indent = line[:len(line) - len(line.lstrip())]
            output.append("%s# RScript conversion: unsupported text control %s "
                          "flattened to empty.\n" % (indent, ", ".join(flattened)))
        output.append(line)
    return "".join(output)
