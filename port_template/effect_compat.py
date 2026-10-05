"""Flatten visual effects the shared Ren'Py runtime cannot execute."""

from pathlib import Path


# Operand position, field name, safe fallback. Keep in step with runtime/*.rpy.
FIELDS = {
    "_load": ((4, "effect", 0), (5, "colormode", 0)),
    "_cls": ((1, "effect", 0),),
    "_oload": ((3, "effect", 0), (4, "colormode", 0)),
    "_gload": ((1, "colormode", 0),),
    "_update": ((0, "effect", 0),),
    "_effect": ((0, "effect", 0),),
    "_move": ((3, "effect", 0),),
    "_movi": ((3, "effect", 0),),
    "_gmove": ((0, "effect", 0),),
    "_flash": ((1, "effect", 0),),
    "_zupdate": ((0, "effect", 1),),
    "_draw": ((1, "blend mode", 0),),
    "_oaction": ((1, "action", None),),
}
COUNTS = {
    "_load": 6, "_cls": 2, "_oload": 6, "_gload": 2,
    "_update": 3, "_effect": 2, "_move": 5, "_movi": 5,
    "_gmove": 4, "_flash": 2, "_zupdate": 2,
    "_draw": 3, "_oaction": 2,
}
LOAD_EFFECTS = set(range(9)) | {10, 15, 16, 19} | set(range(20, 29))
MOVE_EFFECTS = {0, 1, 2, 3, 7, 8, 9, 10}


def _supported(command: str, field: str, value: int,
               resources: Path) -> tuple[bool, str]:
    if field == "colormode":
        return value in range(7), "not implemented"
    if command == "_draw":
        return value in (0, 1, 2), "not implemented"
    if command == "_oaction":
        return value == 4, "not implemented"
    if command in ("_load", "_cls", "_oload"):
        return value in LOAD_EFFECTS, "not implemented"
    if command in ("_move", "_movi", "_gmove"):
        effect = value - 100 if value > 100 else value
        return effect in MOVE_EFFECTS, "not implemented"
    if command == "_flash":
        return value in range(4), "not implemented"
    if command == "_zupdate":
        return value == 1, "not implemented"
    if command in ("_update", "_effect"):
        if value == 0 or (command == "_update" and value in range(1, 5)):
            return True, ""
        if value < 11:
            return False, "not implemented"
        mask = ("ef%02d.png" if command == "_update" else "es%03d.png") % value
        relative = Path("grps") / mask
        # install_base converts source .msk masks to these PNG names.
        found = any((resources / prefix / candidate).is_file()
                    for prefix in (Path(), Path("images"))
                    for candidate in (relative, relative.with_suffix(".msk")))
        if not found and command == "_effect":
            # Image registration lowercases tags, not actual resource filenames.
            found = any(path.name.lower() == mask
                        for prefix in (Path(), Path("images"))
                        for path in (resources / prefix / "grps").glob("*")
                        if path.is_file())
        return found, "missing %s" % relative
    raise ValueError("unlisted effect command: %s" % command)


def flatten_unsupported_effects(text: str, resources: Path,
                                label: str = "RScript",
                                preserve_dynamic: bool = False) -> str:
    """Return RPY with unsupported literal or dynamic effects made safe."""
    output = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        newline = line[len(body):]
        indent = body[:len(body) - len(body.lstrip(" \t"))]
        statement = body[len(indent):]
        split = statement.split(maxsplit=1)
        command = split[0] if split else ""
        if command not in FIELDS:
            output.append(line)
            continue
        rest = split[1] if len(split) > 1 else ""
        operands = rest.split(maxsplit=5) if command == "_oload" else rest.split()
        if len(operands) != COUNTS[command]:
            raise ValueError("malformed %s statement: %s" % (command, body))
        comments = []
        for index, field, fallback in FIELDS[command]:
            original = operands[index]
            try:
                value = int(original, 0)
            except ValueError:
                if preserve_dynamic:
                    # Established dialects retain their runtime-selected effects.
                    comments.append("%s# %s conversion: %s %s %s preserved "
                                    "for runtime validation.%s" %
                                    (indent, label, command, field, original,
                                     newline or "\n"))
                    continue
                supported, reason = False, "not statically supported"
            else:
                supported, reason = _supported(command, field, value, resources)
            if not supported:
                replacement = "no-op" if fallback is None else str(fallback)
                comments.append("%s# %s conversion: %s %s %s flattened to %s "
                                "(%s).%s" % (indent, label, command, field,
                                             original, replacement, reason,
                                             newline or "\n"))
                if fallback is None:
                    command = "pass"
                    operands = []
                    break
                operands[index] = replacement
        output.extend(comments)
        output.append((indent + command + (" " + " ".join(operands) if operands else "") + newline)
                      if comments else line)
    return "".join(output)
