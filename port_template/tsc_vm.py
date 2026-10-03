"""Shared packed expressions and temporary-register VM lowering."""

OPERATORS = {2: "or", 3: "and", 4: "==", 5: ">=", 6: ">", 7: "<=",
             8: "<", 9: "!=", 10: "+", 11: "-", 12: "*", 13: "//", 14: "%"}


def packed(value: int) -> str:
    depth, raw = divmod(value, 0x10000)
    if not depth:
        return str(raw - 0x10000 if raw & 0x8000 else raw)
    result = str(raw)
    for _ in range(depth):
        result = "_r[%s]" % result
    return result


def vm_source(opcode: int, value: int, left: bool, temps: dict[int, str]) -> str:
    mode = (opcode >> (10 if left else 8)) & 3
    if mode == 0:
        return str(value)
    if mode == 1:
        return temps.get(value, "0")
    if mode == 2:
        result = str(value)
        for _ in range(((opcode >> (4 if left else 0)) & 15) + 1):
            result = "_r[%s]" % result
        return result
    return "0"


def emit_vm(opcode: int, operands: tuple[int, ...], temps: dict[int, str]) -> list[str]:
    family = opcode >> 12
    if family == 15:
        destination, source = operands
        temps[destination] = vm_source(opcode, source, False, temps)
        return []
    temporary, left, right = operands
    lhs = vm_source(opcode, left, True, temps)
    rhs = vm_source(opcode, right, False, temps)
    if family == 1:
        if ((opcode >> 10) & 3) == 2:
            temps[temporary] = rhs
            return ["$ %s = %s" % (lhs, rhs)]
        temps[temporary] = rhs
        return []
    temps[temporary] = "(%s %s %s)" % (lhs, OPERATORS.get(family, "+"), rhs)
    return []
