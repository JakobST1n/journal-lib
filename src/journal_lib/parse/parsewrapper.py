from .ply import yacc

class ParseWrapper(object):

    def __init__(self, tokens = None, debug: bool = False):
        if tokens is not None:
            self.tokens = tokens
        self.debug = debug
        self.build(debug=debug)

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, *args, **kwargs):
        return self.parser.parse(*args, **kwargs)

    def _hl_token(self, p):
        try:
            linestart = p.lexer.lexdata.rfind("\n", 0, p.lexpos) + 1
            lineend = p.lexer.lexdata.find("\n", p.lexpos)
            markpos = p.lexpos - linestart
            marklen = len(str(p.value))
            lineno = p.lexer.lexdata[0:linestart+1].count("\n")
            print(f"Syntax error at '{p.value}' on line {lineno}, position {markpos}")
            print(f"    {p.lexer.lexdata[linestart:lineend]}")
            print(f"    {' ' * markpos}{'^' * marklen}")
        except Exception as e:
            print(f"An error occured when showing the position of token {p}\n{e}")

