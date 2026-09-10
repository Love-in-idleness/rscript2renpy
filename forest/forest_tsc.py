"""Reader for the current command-based Forest TSC format."""

from dataclasses import dataclass
from pathlib import Path


E = "E"


@dataclass(frozen=True)
class Instruction:
    offset: int
    opcode: int
    kinds: tuple[str, ...]
    operands: tuple[int, ...]
    size: int


@dataclass(frozen=True)
class ForestTsc:
    path: Path
    code_size: int
    strings: tuple[str, ...]
    data_blocks: tuple[tuple[int, ...], ...]
    decoded_instructions: tuple[Instruction, ...]
    encoding: str

    def string(self, index: int) -> str:
        return self.strings[index]

    def data(self, index: int) -> tuple[int, ...]:
        return self.data_blocks[index]

    def instructions(self) -> list[Instruction]:
        return list(self.decoded_instructions)


# Forest uses the legacy-28/early dialect. These are the commands present in
# its scripts, with the operand layouts used by LiarsoftTool's current TSC
# compiler. H/S/D are integer widths; E is an RScript packed expression.
COMMANDS = {
    "end": (8, ""), "rnd": (9, "H"), "hit": (10, ""),
    "hitc": (11, ""), "jump": (12, "E"), "wait": (13, "E"),
    "select": (14, "H" + "D" * 11 + "E" * 3), "gosub": (15, "E"),
    "return": (16, "E"), "data": (18, "ED"), "gload": (20, "EE"),
    "gcls": (21, ""), "gmove": (22, "EEEE"), "quake": (23, "EE"),
    "flash": (24, "EE"), "queue": (26, ""), "action": (27, ""),
    "update": (28, "EEE"), "zupdate": (29, "EE"),
    "load": (30, "EEEEEE"), "font": (32, "EEEEED"),
    "move": (33, "EEEEE"), "movi": (34, "EEEEE"),
    "phase": (35, "EE"), "cls": (36, "EE"), "enabl": (37, "EE"),
    "locmode": (38, "EEE"), "draw": (39, "EEE"),
    "depth": (40, "EE"), "group": (41, "EE"), "tbox": (42, "EE"),
    "effect": (43, "EE"), "effectdep": (44, "E"),
    "tone": (45, "EE"), "tonedep": (46, "E"),
    "locgrid": (47, "EE"), "face": (48, "EE"), "mode": (49, "EE"),
    "backup": (50, ""), "resume": (51, ""), "stop": (52, ""),
    "autobackup": (53, "E"), "makesave": (55, ""),
    "sysmode": (56, "EEEEE"), "logflash": (57, ""),
    "endscene": (58, ""), "swap": (59, "EEEE"),
    "bgm_on": (60, "EE"), "bgm_off": (61, "E"), "se": (62, "E"),
    "se_on": (63, "EEE"), "se_off": (64, "E"), "movie": (65, "E"),
    "voice": (66, "EEEE"), "voice_off": (67, "E"),
    "se_wait": (68, ""), "voice_wait": (69, ""),
    "setclk": (70, "EEEE"), "setclksys": (71, "EEEE"),
    "resetclk": (72, "E"), "click": (73, "EE"),
    "autoreset": (74, "E"), "setlink": (75, "EEEE"),
    "setclksub": (77, "EEEE"), "TCL": (80, "E"),
    "TXT": (81, "EEEEDDE"), "TXA": (82, "EEEEDE"), "txcls": (83, "E"),
    "tboxloc": (90, "EEE"), "texloc": (91, "EEEEE"),
    "tboxback": (92, "EE"), "cmploc": (93, "EE"),
    "tboxcmp": (94, "E"), "texcolor": (95, "EE"),
    "texsize": (96, "EE"), "texfont": (97, "EE"),
    "texmode": (98, "EE"), "texindent": (99, "EEE"),
    "waitloc": (100, "EEE"), "faceloc": (101, "EE"),
    "tclsmode": (102, "E"), "waitlod": (103, "EE"),
    "waitcol": (104, "EEEE"), "facedep": (105, "E"),
    "namloc": (106, "EEEEE"), "texpich": (107, "EEE"),
    "texruby": (108, "EEEE"), "getloc": (110, "EEE"),
    "muldev": (111, "EEE"), "root": (112, "E"),
    "pow": (113, "EE"), "getflag": (114, "EE"),
    "menuon": (115, "EE"), "menuset": (116, "EE"),
    "menuget": (117, "EE"), "fontsize": (120, "EE"),
    "folder": (121, "ED"), "numload": (130, "EEEE"),
    "numreng": (131, "EEEEE"), "numenable": (132, "EE"),
    "numloc": (134, "EEE"), "numset": (135, "EEEEE"),
    "num": (136, "EEE"), "gmenuon": (140, "EE"),
    "gmenuset": (141, "EE"), "gmenuget": (142, "EE"),
    "strset": (150, "ED"), "stradd": (151, "ED"),
    "numstr": (152, "EE"), "strnum": (153, "EE"),
    "strcpy": (154, "EE"), "strcat": (155, "EE"),
}


STRING_OPERANDS = {
    14: {1, 7, 8, 9, 10, 11}, 32: {5}, 81: {4, 5}, 82: {4},
    121: {1}, 150: {1}, 151: {1},
}


def _tokens(line: str, line_no: int) -> list[tuple[str, bool]]:
    """Tokenize one source line using LiarsoftTool's quoting rules."""
    result = []
    pos = 0
    while pos < len(line):
        while pos < len(line) and line[pos].isspace():
            pos += 1
        if pos == len(line) or line[pos] == ";":
            break
        if line[pos] != '"':
            start = pos
            while (pos < len(line) and not line[pos].isspace() and
                   line[pos] != ";"):
                pos += 1
            result.append((line[start:pos], False))
            continue
        pos += 1
        value = []
        while pos < len(line) and line[pos] != '"':
            char = line[pos]
            pos += 1
            if char != "\\":
                value.append(char)
                continue
            if pos == len(line):
                raise ValueError("line %d: incomplete string escape" % line_no)
            escaped = line[pos]
            pos += 1
            escapes = {"n": "\n", "r": "\r", "t": "\t",
                       "\\": "\\", '"': '"'}
            if escaped not in escapes:
                raise ValueError("line %d: unsupported string escape" % line_no)
            value.append(escapes[escaped])
        if pos == len(line):
            raise ValueError("line %d: unterminated string" % line_no)
        pos += 1
        result.append(("".join(value), True))
    return result


def _number(token: str, kind: str, line_no: int) -> int:
    depth = 0
    if kind == E:
        depth = len(token) - len(token.lstrip("@"))
        token = token[depth:]
    try:
        value = int(token, 0)
    except ValueError as error:
        raise ValueError("line %d: invalid numeric operand" % line_no) from error
    if kind == E:
        if depth > 0xffff or (not depth and not -32768 <= value <= 32767) or \
                (depth and not 0 <= value <= 65535):
            raise ValueError("line %d: expression operand is out of range" % line_no)
        return depth * 0x10000 | (value & 0xffff)
    low, high = (-32768, 32767) if kind == "S" else \
        (0, 0xffff if kind == "H" else 0xffffffff)
    if not low <= value <= high:
        raise ValueError("line %d: numeric operand is out of range" % line_no)
    return value


def read_tsc(path: str | Path) -> ForestTsc:
    """Read current LiarsoftTool command TSC; old metadata dumps are rejected."""
    path = Path(path)
    byte_format = None
    encoding = None
    schema = None
    labels = {}
    sources = []
    data_blocks = []
    offset = 0

    for line_no, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith(";@gsc-structure-") or line.startswith(";@gsc-raw-"):
            raise ValueError(
                f"{path}: obsolete TSC format; regenerate it with current LiarsoftTool")
        if line.startswith(";@gsc-byte-format "):
            if byte_format is not None:
                raise ValueError(f"{path}: duplicate TSC byte format")
            byte_format = line.removeprefix(";@gsc-byte-format ")
            continue
        if line.startswith(";@gsc-text-encoding "):
            if encoding is not None:
                raise ValueError(f"{path}: duplicate TSC text encoding")
            encoding = line.removeprefix(";@gsc-text-encoding ")
            continue
        if line.startswith(";@gsc-schema "):
            if schema is not None:
                raise ValueError(f"{path}: duplicate TSC schema")
            schema = line.removeprefix(";@gsc-schema ")
            continue

        tokens = _tokens(line, line_no)
        if not tokens:
            continue
        first = tokens[0][0]
        if first.startswith(":"):
            if len(tokens) != 1 or len(first) == 1:
                raise ValueError(f"{path}: line {line_no}: malformed label")
            if first[1:] in labels:
                raise ValueError(f"{path}: line {line_no}: duplicate label")
            labels[first[1:]] = offset
            continue
        if not first.startswith("*"):
            raise ValueError(f"{path}: line {line_no}: expected command or label")
        if byte_format != "legacy-28" or schema != "early":
            raise ValueError(
                f"{path}: Forest requires current legacy-28/early command TSC")
        name = first[1:]
        if name == "datablock":
            if len(tokens) < 3:
                raise ValueError(f"{path}: line {line_no}: malformed datablock")
            index = _number(tokens[1][0], "D", line_no)
            count = _number(tokens[2][0], "D", line_no)
            if index != len(data_blocks) or len(tokens) != count + 3:
                raise ValueError(f"{path}: line {line_no}: malformed datablock")
            data_blocks.append(tuple(_number(token, "S", line_no)
                                     for token, quoted in tokens[3:]
                                     if not quoted))
            if len(data_blocks[-1]) != count:
                raise ValueError(f"{path}: line {line_no}: quoted datablock value")
            continue
        if name == "vm":
            if len(tokens) < 2:
                raise ValueError(f"{path}: line {line_no}: missing VM opcode")
            opcode = _number(tokens[1][0], "H", line_no)
            if not opcode & 0xf000:
                raise ValueError(f"{path}: line {line_no}: invalid VM opcode")
            kinds = "HH" if opcode & 0xf000 == 0xf000 else "HHH"
            operand_tokens = tokens[2:]
        elif name in ("jz", "jnz", "goto"):
            opcode = {"jz": 3, "jnz": 4, "goto": 5}[name]
            kinds = "D"
            operand_tokens = tokens[1:]
        else:
            try:
                opcode, kinds = COMMANDS[name]
            except KeyError as error:
                raise ValueError(
                    f"{path}: line {line_no}: unsupported Forest command {name}") from error
            operand_tokens = tokens[1:]
        if len(operand_tokens) != len(kinds):
            raise ValueError(f"{path}: line {line_no}: wrong operand count for {name}")
        sources.append((line_no, offset, opcode, kinds, operand_tokens))
        offset += 2 + sum(2 if kind in "HS" else 4 for kind in kinds)

    if byte_format != "legacy-28" or schema != "early":
        raise ValueError(f"{path}: Forest requires current legacy-28/early command TSC")
    if not encoding:
        raise ValueError(f"{path}: missing TSC text encoding")

    strings = [""]
    string_indices = {"": 0}
    instructions = []
    for line_no, item_offset, opcode, kinds, operand_tokens in sources:
        operands = []
        for index, ((token, quoted), kind) in enumerate(zip(operand_tokens, kinds)):
            if index in STRING_OPERANDS.get(opcode, set()):
                if not quoted:
                    raise ValueError(f"{path}: line {line_no}: string operand must be quoted")
                if token not in string_indices:
                    string_indices[token] = len(strings)
                    strings.append(token)
                operands.append(string_indices[token])
            elif opcode in (3, 4, 5) or (opcode == 14 and 2 <= index <= 6):
                if quoted or token not in labels:
                    raise ValueError(f"{path}: line {line_no}: unknown label {token}")
                operands.append(labels[token])
            else:
                if quoted:
                    raise ValueError(f"{path}: line {line_no}: numeric operand cannot be quoted")
                operands.append(_number(token, kind, line_no))
        size = 2 + sum(2 if kind in "HS" else 4 for kind in kinds)
        instructions.append(Instruction(item_offset, opcode, tuple(kinds),
                                        tuple(operands), size))

    return ForestTsc(path, offset, tuple(strings), tuple(data_blocks),
                     tuple(instructions), encoding)
