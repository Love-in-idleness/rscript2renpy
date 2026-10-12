#!/usr/bin/env python3
"""Subtitle matching keeps earliest opcode order without recursion limits."""

from itertools import combinations, product
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from tsc_patches import align_insertable_segment, language_patch_data
from rscript_tsc import read_tsc


def instructions(opcodes):
    return [SimpleNamespace(opcode=opcode) for opcode in opcodes]


def main():
    sequences = [values for size in range(4)
                 for values in product((13, 32, 36), repeat=size)]
    for base in sequences:
        for patch in sequences:
            # Enumerate all subsequences; the first valid one is the old tie-breaking rule.
            expected = next((tuple(enumerate(indices))
                             for indices in combinations(range(len(patch)), len(base))
                             if tuple(patch[index] for index in indices) == base), None)
            try:
                actual = align_insertable_segment(instructions(base), instructions(patch))
            except ValueError as error:
                assert expected is None, (base, patch, expected)
                assert str(error) == "language patch removes an existing display command"
            else:
                assert actual == expected, (base, patch, actual, expected)

    count = 10000
    matched = align_insertable_segment(instructions([13] * count),
                                      instructions([32, 13] * count))
    assert matched == tuple((index, index * 2 + 1) for index in range(count))
    assert align_insertable_segment([], instructions([32] * count)) == ()
    try:
        align_insertable_segment(instructions([13]), instructions([32] * count))
    except ValueError:
        pass
    else:
        raise AssertionError("missing display command accepted in long segment")

    with TemporaryDirectory() as temporary:
        base = Path(temporary) / "base"
        patch = Path(temporary) / "patch"
        base.mkdir()
        patch.mkdir()
        header = ";@gsc-byte-format legacy-28\n;@gsc-schema early\n"
        count = 1100
        source = base / "0000.tsc"
        source.write_text(header + "*wait 10\n" * count + "*end\n", encoding="utf-8")
        (patch / source.name).write_text(
            header + '*font 20 0 0 0 0 "subtitle"\n*wait 10\n' * count +
            '*font 20 0 0 0 0 "before end"\n*end\n' +
            '*font 20 0 0 0 0 "after end"\n', encoding="utf-8")
        texts, insertions, overrides = language_patch_data(base, patch)
        assert texts == {} and overrides == {}
        original = read_tsc(source)
        offsets = [item.offset for item in original.instructions()] + [original.code_size]
        assert list(insertions[source.name]) == offsets
        assert [commands[0] for commands in insertions[source.name].values()] == (
            ["_oload 20 0 0 0 0 'subtitle'"] * count +
            ["_oload 20 0 0 0 0 'before end'", "_oload 20 0 0 0 0 'after end'"])
    print("OK: exhaustive subtitle alignment, long segments and stable insertion targets")


if __name__ == "__main__":
    main()
