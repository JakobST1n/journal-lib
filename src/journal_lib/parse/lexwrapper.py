from .ply import lex
import sys


class LexWrapper(object):
    state_trail = ["INITIAL"]

    def _state_begin(self, state: str, t=None):
        """Convenient wrapper for the lexer.begin, which makes it possible to track state changes."""
        self.lexer.begin(state)
        self.state_trail.append(self.lexer.current_state())

        if len(self.state_trail) > 5:
            self.state_trail = self.state_trail[-5:]

        if self.debug:
            d = f"{' ':{self.max_token_name_length+2}}{self.state_trail[-2]} -> {self.state_trail[-1]}"
            if t is not None:
                d += ', recognized [{}] "{}"'.format(
                    t.type, t.value.replace("\n", "\\n")
                )
            self.debuglog.info(d)

    def __init__(self, debug: bool = False):
        """Initialize a new JournalLexer"""
        self.build(debug=debug)
        self.debug = debug
        if self.debug:
            self.debuglog = lex.PlyLogger(sys.stderr)
        self.max_token_name_length = max(len(x) + 1 for x in self.tokens)

    def build(self, **kwargs):
        """Reinitialize the lexer module (this is called on __init__)"""
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, s: str):
        """Wrapper for the lex input function"""
        self.lexer.input(s)

    def token(self):
        """Wrapper for the lex token function, can print debug information to stdout if debug is enabled"""
        tok = self.lexer.token()
        if self.debug and tok:
            self.debuglog.info(
                '[{:<{width}} ({}:{}) "{}"'.format(
                    tok.type + "]",
                    tok.lineno,
                    tok.lexpos,
                    tok.value.replace("\n", "\\n"),
                    width=self.max_token_name_length,
                )
            )
        return tok

    def print_tokens(self, data):
        """Simple debugging function which will trigger a tokenization of all the data provided"""
        self.input(data)
        _debug = self.debug
        self.debug = True
        while True:
            self.lexer.token()
        self.debug = _debug

    def _hl_token(self, t):
        try:
            linestart = t.lexer.lexdata.rfind("\n", 0, t.lexpos) + 1
            lineend = t.lexer.lexdata.find("\n", t.lexpos)
            markpos = t.lexpos - linestart
            lineno = t.lexer.lexdata[0 : linestart + 1].count("\n")
            print(
                f"Illegal character at '{t.value[0]}' on line {lineno}, position {markpos}"
            )
            print(f"    {t.lexer.lexdata[linestart:lineend]}")
            print(f"    {' ' * markpos}^")
        except Exception as e:
            print(f"Illegal character '{p.value}'")
            print(
                f"Additionally a error occuren when showing the position of the illegal character\n{e}"
            )

    @property
    def lexdata(self):
        if hasattr(self, "lexer"):
            return self.lexer.lexdata
        return None
