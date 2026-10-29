"""RScript kinsoku rules, operating on already shaped glyph advances."""

import json
import re


def ruby_markup(text):
    """Convert CodeX span and single-character readings, after style controls."""
    return re.sub(r"\|([^\[\]|]+)\[([^\[\]]+)\]|([^{}\[\]|\n])\[([^\[\]]+)\]",
                  lambda m: "{rb}%s{/rb}{rt}%s{/rt}" % (
                      (m[1], m[2]) if m[1] is not None else (m[3], m[4])), text)

def parse_kinsoku(text):
    """Read the same version-1 rule format as LiarsoftTool's runtime."""
    def unique_fields(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate kinsoku key: %s" % key)
            result[key] = value
        return result

    data = json.loads(text, object_pairs_hook=unique_fields)
    if (not isinstance(data, dict) or
            set(data) != {"version", "no_line_start", "no_line_end"} or
            type(data["version"]) is not int or data["version"] != 1):
        raise ValueError("kinsoku requires version 1 and both character sets")
    values = [data[key] for key in ("no_line_start", "no_line_end")]
    if any(not isinstance(value, str) for value in values):
        raise ValueError("kinsoku character sets must be strings")
    if any(ord(char) == 0 or 0xd800 <= ord(char) <= 0xdfff or ord(char) > 0xffff
           for value in values for char in value):
        raise ValueError("kinsoku rule characters must be non-NUL BMP characters")
    rules = tuple(frozenset(value) for value in values)
    if rules[0] & rules[1]:
        raise ValueError("kinsoku character sets overlap")
    return rules


def glyph_breaks(glyphs, limit, rules, ruby_atomic=True):
    """Return indices of line starts. Never mutate advances or discard glyphs."""
    units = []
    index = 0
    while index < len(glyphs):
        first = last = glyphs[index]
        start = index
        advance = first.advance
        index += 1
        if getattr(first, "ruby", 0) == 1 and ruby_atomic:
            # Native ruby flags: 1 = base, 2/3 = annotation above it.
            # Keep the pair indivisible; annotation does not advance the pen.
            while index < len(glyphs) and getattr(glyphs[index], "ruby", 0) == 1:
                last = glyphs[index]
                advance += last.advance
                index += 1
            while index < len(glyphs) and getattr(glyphs[index], "ruby", 0) >= 2:
                index += 1
        elif getattr(first, "ruby", 0) >= 2:
            continue
        units.append((start, advance, chr(first.character), chr(last.character)))
    no_start = [first in rules[0] for _, _, first, _ in units]
    no_end = [last in rules[1] for _, _, _, last in units]
    starts = []
    start = 0
    width = 0.0
    hanging = False
    boundary = 0
    boundary_width = 0.0
    for index, (_, advance, _, _) in enumerate(units):
        if index > start and not no_end[index - 1] and not no_start[index]:
            boundary, boundary_width = index, width
        if advance <= 0 or width + advance <= limit or index == start:
            # An oversized first glyph must still be consumed.
            width += advance
            continue
        if no_start[index] or (not hanging and width < limit):
            # Keep an entire punctuation run on its preceding line.
            width += advance
            hanging = True
            continue
        if boundary > start:
            # Move the whole opening-bracket run to the last legal boundary.
            start = boundary
            starts.append(start)
            width -= boundary_width
        # An indivisible run may exceed the limit, but must still progress.
        width += advance
        hanging = width > limit
    return [units[index][0] for index in starts]


def sync_ruby_times(glyphs):
    """Reveal readings with their body cells, without adding typewriter time."""
    index = 0
    while index < len(glyphs):
        before = index
        body, reading = [], []
        while index < len(glyphs) and glyphs[index].ruby == 1:
            body.append(glyphs[index])
            index += 1
        while index < len(glyphs) and glyphs[index].ruby == 2:
            reading.append(glyphs[index])
            index += 1
        if not body or not reading:
            if index == before:
                index += 1
            continue
        start = 0
        while start < len(body):
            end = start + 1
            while end < len(body) and body[end].y == body[start].y:
                end += 1
            count = (len(reading) * (end - start) + len(body) - start - 1) // (len(body) - start)
            row, reading = reading[:count], reading[count:]
            for position, glyph in enumerate(row):
                glyph.time = body[start + position * (end - start) // count].time
            start = end


def place_native_ruby(glyphs, offset, advances=None):
    """46afa0: distribute short readings; centre long ones; split by body rows.

    Glyph.y is a baseline, whereas CodeX positions glyph cells. Ascent converts
    between them; widths are final advances, never ink bounding boxes.
    """
    advances = advances or {}
    index = 0
    while index < len(glyphs):
        before = index
        body, reading = [], []
        while index < len(glyphs) and glyphs[index].ruby == 1:
            body.append(glyphs[index])
            index += 1
        while index < len(glyphs) and glyphs[index].ruby == 2:
            reading.append(glyphs[index])
            index += 1
        if not body or not reading:
            if index == before:
                index += 1
            continue
        start = 0
        while start < len(body):
            end = start + 1
            while end < len(body) and body[end].y == body[start].y:
                end += 1
            # Native recursion rounds up the current row's proportional share.
            count = (len(reading) * (end - start) + len(body) - start - 1) // (len(body) - start)
            row, reading = reading[:count], reading[count:]
            if row:
                first, last = body[start], body[end - 1]
                span = last.x + advances.get(id(last), last.advance) - first.x
                width = sum(g.advance for g in row)
                cell = span // len(row)
                x = first.x - (width - span) // 2 if width > span else first.x + cell // 2
                for glyph in row:
                    glyph.x = int(x if width > span else x - glyph.advance // 2)
                    glyph.y = round(first.y - first.ascent + glyph.ascent - offset)
                    x += glyph.advance if width > span else cell
            start = end


def normalize_boundaries(tokens, text_type, paragraph_type, displayable_type):
    """Coalesce explicit breaks at one visible-glyph boundary.

    Leading/trailing boundaries do not create blank lines. Tags retain their
    exact order, including those between repeated breaks. Spaces are visible.
    """
    result = []
    visible = False
    pending = None
    for kind, value in tokens:
        if kind == paragraph_type:
            if visible and pending is None:
                pending = len(result)
                result.append((kind, value))
            continue
        result.append((kind, value))
        if (kind == text_type and value) or kind == displayable_type:
            visible = True
            pending = None
    if pending is not None:
        del result[pending]
    return result
