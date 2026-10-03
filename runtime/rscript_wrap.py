"""RScript kinsoku rules, operating on already shaped glyph advances."""

NO_LINE_START = frozenset(
    " '\".,?!)}]"
    "\u3000、。，．？！ー～…）〕］｝〉》」』】’”"
    "っぁぃぅぇぉゃゅょァィゥェォャュョ"
    "»“:;%‰°–—-\u00a0™®"
)
NO_LINE_END = frozenset(
    "‘“（〔［｛〈《「『【゛«„([{№§$€"
)


def glyph_breaks(glyphs, limit):
    """Return indices of line starts. Never mutate advances or discard glyphs."""
    # Keep both properties: e.g. “ belongs to both sets.
    no_start = [chr(g.character) in NO_LINE_START for g in glyphs]
    no_end = [chr(g.character) in NO_LINE_END for g in glyphs]
    starts = []
    start = 0
    width = 0.0
    hanging = False
    for index, glyph in enumerate(glyphs):
        advance = glyph.advance
        if advance <= 0 or width + advance <= limit or index == start:
            # An oversized first glyph must still be consumed.
            width += advance
            continue
        if not hanging and (width < limit or no_start[index]):
            # Forest starts a full glyph while its pen position is still
            # inside the line. It may extend beyond the edge once, just like
            # a forbidden line-start glyph at the exact edge.
            width += advance
            hanging = True
            continue
        if index - 1 > start and no_end[index - 1]:
            # Move exactly one glyph back, never recursively retreat.
            start = index - 1
            starts.append(start)
            width = glyphs[start].advance
            hanging = False
            if width + advance <= limit:
                width += advance
                continue
            if width < limit or no_start[index]:
                width += advance
                hanging = True
                continue
        # A single opening glyph cannot be moved to an empty identical line.
        start = index
        starts.append(start)
        width = advance
        hanging = False
    return starts


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
