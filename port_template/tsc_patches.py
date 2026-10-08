"""Shared text/subtitle patch alignment; dialects retain opcode policies."""

from pathlib import Path
from functools import lru_cache
import re

from rscript_tsc import STRING_OPERANDS, read_tsc
from tsc_vm import packed

PATCH_INSERT_OPCODES = {13, 32, 36}


def patch_text_expression(language_texts, item, kind, default):
    replacements = {language: texts[(item.offset, kind)]
                    for language, texts in language_texts.items()
                    if (item.offset, kind) in texts}
    return (("%r.get(_preferences.language, %r)" % (replacements, default), True)
            if replacements else (repr(default), False))


def emit_insertions(lines, insertions, offset):
    for language, commands in insertions.items():
        added = commands.get(offset, ())
        if added:
            lines.append("    if _preferences.language == %r:" % language)
            lines.extend("        " + command for command in added)


def emit_operand_variants(lines, overrides, item, statement):
    variants = {language: mapping[item.offset]
                for language, mapping in overrides.items()
                if item.offset in mapping}
    for index, (language, values) in enumerate(variants.items()):
        lines.extend(("    %s _preferences.language == %r:" %
                      ("if" if index == 0 else "elif", language),
                      "        " + statement(values)))
    if variants:
        lines.append("    else:")
    lines.append(("        " if variants else "    ") + statement(item.operands))


def menu_text(value: str) -> str:
    asset = re.fullmatch(r"<@(\d+)>", value)
    if asset:
        return "rscript_asset_%s" % asset.group(1)
    return re.sub(r"<@(\d+)>", lambda match: "[_r[%s]]" % match.group(1), value)


def scenario_sources(folder: Path) -> list[Path]:
    """Return current command-based TSC scripts in a resource directory."""
    if not folder.is_dir():
        return []
    return sorted(source for source in folder.iterdir()
                  if source.is_file() and source.suffix.lower() == ".tsc")


def instruction_strings(tsc, item, menu_transform=lambda value: value) -> dict[str, str]:
    """Return the translatable strings carried by one instruction."""
    result = {}
    opcode, operands = item.opcode, item.operands
    if opcode == 14:
        result["prompt"] = menu_transform(tsc.string(operands[1]))
        for number, index in enumerate(operands[7:7 + min(operands[0], 5)]):
            if index < len(tsc.strings):
                result["choice%d" % number] = menu_transform(tsc.string(index))
    elif opcode == 81:
        name, text = tsc.string(operands[4]), tsc.string(operands[5])
        if re.fullmatch(r"(?:\^c[ygwk])+", name):
            name = ""
        result["say"] = (name + "：" if name else "") + text
    elif opcode == 82:
        result["append"] = tsc.string(operands[4])
    elif opcode == 32:
        result["oload"] = tsc.string(operands[5])
    return result


def scene_strings(source: Path, dialect=None, menu_transform=lambda value: value) -> dict[tuple[int, str], str]:
    """Return strings that a language patch may replace, keyed by command."""
    tsc = read_tsc(source, dialect) if dialect else read_tsc(source)
    return {(item.offset, kind): value
            for item in tsc.instructions()
            for kind, value in instruction_strings(tsc, item, menu_transform).items()}


def align_insertable_segment(base, patch):
    """Match existing wait/font/cls commands and leave patch additions."""
    @lru_cache(maxsize=None)
    def align(base_index, patch_index):
        if base_index == len(base):
            return ()
        if patch_index == len(patch):
            return None
        if base[base_index].opcode == patch[patch_index].opcode:
            rest = align(base_index + 1, patch_index + 1)
            if rest is not None:
                return ((base_index, patch_index),) + rest
        return align(base_index, patch_index + 1)

    result = align(0, 0)
    if result is None:
        raise ValueError("language patch removes an existing display command")
    return result


def render_patch_command(tsc, item) -> str:
    if item.opcode == 13:
        return "_wait %s" % packed(item.operands[0])
    if item.opcode == 32:
        args = " ".join(packed(value) for value in item.operands[:5])
        return "_oload %s %r" % (args, tsc.string(item.operands[5]))
    if item.opcode == 36:
        args = " ".join(packed(value) for value in item.operands)
        return "_cls %s" % args
    raise ValueError("unsupported language-patch insertion")


def changed_instruction_parameters(base_tsc, patch_tsc, base_item, patch_item,
                                   patch_to_base_offsets) -> bool:
    """Whether aligned commands differ outside translatable strings."""
    text_positions = {81: {4, 5}, 82: {4}, 32: {5}}.get(base_item.opcode, set())
    if base_item.opcode == 14:
        text_positions = {1, *range(7, 7 + min(base_item.operands[0], 5))}
    for index, (base, patch) in enumerate(zip(base_item.operands,
                                               patch_item.operands)):
        if index in STRING_OPERANDS.get(base_item.opcode, set()):
            if index not in text_positions and base_tsc.string(base) != patch_tsc.string(patch):
                return True
            continue
        if (base_item.opcode == 14 and 2 + min(base_item.operands[0], 5) <= index < 7):
            continue  # Unused choice destinations carry no branch semantics.
        target = (base_item.opcode in (3, 4, 5) or
                  (base_item.opcode == 200 and index == 0) or
                  (base_item.opcode == 14 and
                   2 <= index < 2 + min(base_item.operands[0], 5)))
        if target:
            patch = patch_to_base_offsets.get(patch, ("unmapped", patch))
        elif base_item.opcode == 18 and index == 1:
            base, patch = base_tsc.data(base), patch_tsc.data(patch)
        if base != patch:
            return True
    return False


def language_patch_data(base_scr: Path, patch_scr: Path, *, dialect=None,
                        excluded_scenes=(), override_opcodes=(),
                        menu_transform=lambda value: value, source_names=None):
    """Return translated strings, subtitle insertions, and operand overrides."""
    replacements = {}
    insertions = {}
    operand_overrides = {}
    for patch_source in scenario_sources(patch_scr):
        if source_names is not None and patch_source.name not in source_names:
            continue
        base_source = base_scr / patch_source.name
        if not base_source.is_file():
            raise FileNotFoundError(
                "%s has no matching base scenario" % patch_source)
        if patch_source.name in excluded_scenes:
            continue
        base_tsc = read_tsc(base_source, dialect) if dialect else read_tsc(base_source)
        patch_tsc = read_tsc(patch_source, dialect) if dialect else read_tsc(patch_source)
        base_items = base_tsc.instructions()
        patch_items = patch_tsc.instructions()
        base_fixed = [(index, item) for index, item in enumerate(base_items)
                      if item.opcode not in PATCH_INSERT_OPCODES]
        patch_fixed = [(index, item) for index, item in enumerate(patch_items)
                       if item.opcode not in PATCH_INSERT_OPCODES]
        if [item.opcode for _, item in base_fixed] != \
                [item.opcode for _, item in patch_fixed]:
            raise ValueError(
                "%s changes scenario structure; language patches may only "
                "replace text and add subtitle display commands" % patch_source)

        pairs = []
        added = []
        base_previous = patch_previous = -1
        for fixed_index in range(len(base_fixed) + 1):
            base_next = (base_fixed[fixed_index][0]
                         if fixed_index < len(base_fixed) else len(base_items))
            patch_next = (patch_fixed[fixed_index][0]
                          if fixed_index < len(patch_fixed) else len(patch_items))
            base_segment = base_items[base_previous + 1:base_next]
            patch_segment = patch_items[patch_previous + 1:patch_next]
            try:
                matched = align_insertable_segment(base_segment, patch_segment)
            except ValueError as error:
                raise ValueError("%s: %s" % (patch_source, error)) from error
            matched_patch = {patch_index for _, patch_index in matched}
            for base_index, patch_index in matched:
                pairs.append((base_previous + 1 + base_index,
                              patch_previous + 1 + patch_index))
            for patch_index, item in enumerate(patch_segment):
                if patch_index in matched_patch:
                    continue
                next_match = next((base_index for base_index, matched_index in matched
                                   if matched_index > patch_index),
                                  len(base_segment))
                base_index = base_previous + 1 + next_match
                offset = (base_items[base_index].offset
                          if base_index < len(base_items) else base_tsc.code_size)
                added.append((patch_previous + 1 + patch_index, offset, item))
            if fixed_index < len(base_fixed):
                pairs.append((base_next, patch_next))
                base_previous, patch_previous = base_next, patch_next

        added.sort()
        added_fonts = {item.operands[0] for _, _, item in added
                       if item.opcode == 32}
        for _, _, item in added:
            if item.opcode == 36 and (item.operands[0] not in added_fonts or
                                      item.operands[1] != 0):
                raise ValueError(
                    "%s adds a clear command unrelated to an added subtitle" %
                    patch_source)
            if item.opcode == 13 and not added_fonts:
                raise ValueError(
                    "%s adds a wait command without an added subtitle" %
                    patch_source)

        patch_to_base_offsets = {
            patch_items[patch_index].offset: base_items[base_index].offset
            for base_index, patch_index in pairs
        }
        patch_to_base_offsets[patch_tsc.code_size] = base_tsc.code_size
        scene_replacements = {}
        scene_operand_overrides = {}
        for base_index, patch_index in sorted(pairs):
            base_item = base_items[base_index]
            patch_item = patch_items[patch_index]
            if base_item.kinds != patch_item.kinds:
                raise ValueError("%s changes operand layout at %x" %
                                 (patch_source, base_item.offset))
            if changed_instruction_parameters(
                    base_tsc, patch_tsc, base_item, patch_item,
                    patch_to_base_offsets):
                if base_item.opcode not in override_opcodes:
                    raise ValueError(
                        "%s changes unsupported parameters for opcode %d" %
                        (patch_source, base_item.opcode))
                scene_operand_overrides[base_item.offset] = patch_item.operands
            base = instruction_strings(base_tsc, base_items[base_index], menu_transform)
            patch = instruction_strings(patch_tsc, patch_items[patch_index], menu_transform)
            if base.keys() != patch.keys():
                raise ValueError("%s changes translatable command structure" %
                                 patch_source)
            for kind, old in base.items():
                new = patch[kind]
                if old == new:
                    continue
                scene_replacements[(base_items[base_index].offset, kind)] = new

        if scene_replacements:
            replacements[patch_source.name] = scene_replacements
        if scene_operand_overrides:
            operand_overrides[patch_source.name] = scene_operand_overrides
        if added:
            scene_insertions = insertions.setdefault(patch_source.name, {})
            for _, offset, item in added:
                scene_insertions.setdefault(offset, []).append(
                    render_patch_command(patch_tsc, item))
    return replacements, insertions, operand_overrides
