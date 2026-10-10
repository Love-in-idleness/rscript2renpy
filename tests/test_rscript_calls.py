#!/usr/bin/env python3
"""Execute the shared call handlers with aliased target/argument registers."""
import ast
from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace


def main():
    source = Path(__file__).resolve().parents[1] / "runtime/02_rscript_cmd.rpy"
    block = source.read_text().split("python early:", 1)[1].split("\n# Decompiled", 1)[0]
    tree = ast.parse(dedent(block))
    handlers = ast.Module(body=[node for node in tree.body
                               if isinstance(node, ast.FunctionDef)
                               and node.name in ("execute_gosub", "execute_insub")],
                          type_ignores=[])
    registers = [0] * 100
    calls = []
    env = dict(_r=registers, store=SimpleNamespace(_macro_params=None),
               renpy=SimpleNamespace(call=calls.append, has_label=lambda name: name == "_local"),
               current_script=lambda: "0050")
    env["rscript_label"] = lambda expr: "_%04d" % eval(expr, env)
    env["rscript_label_local"] = lambda script, expr: script + "_" + str(eval(expr, env))
    exec(compile(handlers, str(source), "exec"), env)
    registers[10] = 1000
    env["execute_gosub"](("_r[10]", ["0"] * 10, None))
    assert calls.pop() == "_1000" and registers[10:20] == [0] * 10
    for handler, target, expected in (("execute_gosub", "1000", "_1000"),
                                      ("execute_insub", "_local", "_local"),
                                      ("execute_insub", "_r[10]", "0050_1000")):
        registers[10:12] = [1000, 2]
        env[handler]((target, ["_r[11]", "_r[10]"], None))
        assert calls.pop() == expected and registers[10:12] == [2, 1000]
    env["store"]._macro_params = ["_r[11]", "_r[10]"]
    registers[10:12] = [1000, 2]
    env["execute_gosub"](("_r[10]", ["0"] * 10, None))
    assert calls.pop() == "_1000" and registers[10:12] == [2, 1000]
    print("OK: gosub/insub targets and operands snapshot before register writes")


if __name__ == "__main__":
    main()
