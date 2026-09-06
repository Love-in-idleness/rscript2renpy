python early:

    def parse_undef(lex):
        return (lex.rest(),)

    def parse_undef_block(lex):
        rest = lex.require(".*:")
        lex.expect_eol()
        lex.expect_block("undef_block")

        child = lex.subblock_lexer().renpy_block()

        return {"rest": rest, "child": child }

    def execute_undef(o):
        pass

    def lint_undef(o):
        pass
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
