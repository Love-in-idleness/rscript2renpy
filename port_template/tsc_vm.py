"""Shared packed expressions and temporary-register VM lowering."""

OPERATORS = {2: "or", 3: "and", 4: "==", 5: ">=", 6: ">", 7: "<=",
             8: "<", 9: "!=", 10: "+", 11: "-", 12: "*", 13: "//", 14: "%"}


def packed(value: int, *, word16=False) -> str:
    depth, raw = divmod(value, 0x10000)
    if not depth:
        return str(raw - 0x10000 if raw & 0x8000 else raw)
    result = str(raw)
    for _ in range(depth):
        result = "_r[%s]" % result
    return "rscript_signed16(%s)" % result if word16 else result


def vm_source(opcode: int, value: int, left: bool, temps: dict[int, str], snapshot=False) -> str:
    mode = (opcode >> (10 if left else 8)) & 3
    if mode == 0:
        return str(value)
    if mode == 1:
        if snapshot:
            return "rscript_vm_temps.get(%d, 0)" % value
        return temps.get(value, "0")
    if mode == 2:
        result = str(value)
        for _ in range(((opcode >> (4 if left else 0)) & 15) + 1):
            result = "_r[%s]" % result
        return result
    return "0"


def emit_vm(opcode: int, operands: tuple[int, ...], temps: dict[int, str], *, snapshot=False, word16=False) -> list[str]:
    family = opcode >> 12
    if family == 15:
        destination, source = operands
        temps[destination] = vm_source(opcode, source, False, temps, snapshot)
        if word16:
            temps[destination] = "(%s & 65535)" % temps[destination]
        if snapshot:
            return ["$ rscript_vm_temps[%d] = %s" % (destination, temps[destination])]
        return []
    temporary, left, right = operands
    lhs = vm_source(opcode, left, True, temps, snapshot)
    rhs = vm_source(opcode, right, False, temps, snapshot)
    if family == 1:
        if word16:
            rhs = "(%s & 65535)" % rhs
        if ((opcode >> 10) & 3) == 2:
            temps[temporary] = rhs
            if snapshot:
                return ["$ rscript_vm_temps[%d] = %s" % (temporary, rhs),
                        "$ %s = rscript_vm_temps[%d]" % (lhs, temporary)]
            return ["$ %s = %s" % (lhs, rhs)]
        temps[temporary] = rhs
        if snapshot:
            return ["$ rscript_vm_temps[%d] = %s" % (temporary, rhs)]
        return []
    if word16 and family in (5, 6, 7, 8):
        lhs, rhs = "rscript_signed16(%s)" % lhs, "rscript_signed16(%s)" % rhs
    if word16 and family in (13, 14):
        expression = "rscript_div16(%s, %s, %r)" % (lhs, rhs, family == 14)
    elif word16 and family in (2, 3):
        expression = "int(bool(%s) %s bool(%s))" % (lhs, OPERATORS[family], rhs)
    elif word16 and family in (4, 9):
        expression = "((%s & 65535) %s (%s & 65535))" % (lhs, OPERATORS[family], rhs)
    else:
        expression = "(%s %s %s)" % (lhs, OPERATORS.get(family, "+"), rhs)
    temps[temporary] = "(%s & 65535)" % expression if word16 else expression
    if snapshot:
        return ["$ rscript_vm_temps[%d] = %s" % (temporary, temps[temporary])]
    return []
