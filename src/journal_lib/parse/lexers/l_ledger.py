from journal_lib.parse.lexwrapper import LexWrapper

class JournalLexer(LexWrapper):
    states = (
        ('sHEADER', 'exclusive'),        # Entry header parsing state
        ('sHEADEREFF', 'exclusive'),     # Entry header effective date parsing state
        ('sENTRY', 'exclusive'),         # Entry parsing state
        ('sBLOCKCOMMENT', 'exclusive'),  # Block comment parsing state
        ('sACCOUNT', 'exclusive'),       # Account definition parsing state
        ('sCOMMODITY', 'exclusive'),     # Commodity definition parsing state
    )

    reserved = {
        "account": 'KW_ACCOUNT',
        "commodity": 'KW_COMMODITY'
    }

    tokens = (
        'TEXT',
        'AMOUNT',
        'CURRENCY',
        'COMMENT',
        'INLINE_COMMENT',
        'DATE',
        'ENTRY_STATUS',
        'ENTRY_EFFECTIVE_DATE_SEPARATOR',
        'COMMODITY_NOTE',
        'COMMODITY_FORMAT',
        'COMMODITY_NOMARKET',
        'COMMODITY_DEFAULT',
    ) + tuple(reserved.values())

    t_ANY_ignore = ' \t'

    literals = '\n'

    # Rules for the 'initial' state

    def t_INITIAL_DATE(self, t):
        r'\d{4}(-|\/)\d{2}(-|\/)\d{2}'
        self._state_begin('sHEADER', t)
        return t

    def t_INITIAL_eof(self, t):
        pass

    def t_INITIAL_COMMENT(self, t):
        r'(;|\#|\%|\||\*).+\n'
        pass

    def t_INITIAL_BLOCKCOMMENT(self, t):
        r'comment'
        self._state_begin('sBLOCKCOMMENT', t)

    def t_INITIAL_KEYWORD(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value,'KW')
        if t.type == "KW_ACCOUNT":
            self._state_begin('sACCOUNT', t)
        if t.type == "KW_COMMODITY":
            self._state_begin('sCOMMODITY', t)
        return t

    # Rules for the 'sBLOCKCOMMENT' state

    def t_sBLOCKCOMMENT_end(self, t):
        r'end\scomment'
        t.lexer.lineno += t.value.count('\n')
        self._state_begin('INITIAL', t)

    def t_sBLOCKCOMMENT_content(self, t):
        r'.+?\n'

    def t_sBLOCKCOMMENT_error(self, t):
        r.lexer.skip(1)

    # Rules for the 'sACCOUNT' state

    def t_sACCOUNT_TEXT(self, t):
        r'("[^"]+")|([^\n;]+)'
        if t.value.startswith('"') and t.value.endswith('"'):
            t.value = t.value[1:-1]
        t.value = t.value.rstrip()
        return t

    def t_sACCOUNT_COMMENT(self, t):
        r'(;)[^\n]*'
        return t

    def t_sACCOUNT_newline(self, t):
        r'\n'
        self._state_begin('INITIAL', t)

    # Rules for the 'sCOMMODITY' state

    def t_sCOMMODITY_KW(self, t):
        r'(note|format|nomarket|default)'
        if t.value == "note":
            t.type = "COMMODITY_NOTE"
        elif t.value == "format":
            t.type = "COMMODITY_FORMAT"
        elif t.value == "nomarket":
            t.type = "COMMODITY_NOMARKET"
        elif t.value == "default":
            t.type = "COMMODITY_DEFAULT"

        return t

    def t_sCOMMODITY_TEXT(self, t):
        r'[^\n]+'
        return t

    def t_sCOMMODITY_newline(self, t):
        r'\n(?=(\s*\n|\s*$|[^\s]))'
        self._state_begin('INITIAL', t)

    # Rules for the 'sheader' state

    def t_sHEADER_ENTRY_STATUS(self, t):
        r'(\*|!)'
        return t

    def t_sHEADER_ENTRY_EFFECTIVE_DATE_SEPARATOR(self, t):
        r'='
        self._state_begin('sHEADEREFF', t)
        return t

    def t_sHEADER_TEXT(self, t):
        r'[^\n]+'
        if ((t.value.startswith('"') and t.value.endswith('"'))
            or (t.value.startswith("'") and t.value.endswith("'"))):
            t.value = t.value[1:-1] 
        return t

    def t_sHEADER_newline(self, t):
        r'\n'
        self._state_begin('sENTRY', t)

    # Rules for the  'sheader_effective_date' state

    def t_sHEADEREFF_DATE(self, t):
        r'\d{4}(-|\/)\d{2}(-|\/)\d{2}'
        self._state_begin('sHEADER', t)
        return t

    # Rules for the 'sentry' state

    def t_sENTRY_DATE(self, t):
        r'\d{4}(-|\/)\d{2}(-|\/)\d{2}'
        return t

    def t_sENTRY_CURRENCY(self, t):
        r'\$|NOK'
        return t

    def t_sENTRY_AMOUNT(self, t):
        r'(-)?(\d|\,)+(\.\d{2})?'
        return t

    def t_sENTRY_COMMENT(self, t):
        r';[^\n]*'
        # Check if the comment is at the start of a line (considering whitespaces)
        line_start = t.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
        pre_comment = t.lexer.lexdata[line_start:t.lexpos]
        
        # If the comment is at the start of a line, it's a standalone comment
        if pre_comment.isspace() or pre_comment == "":
            t.type = "COMMENT"
        else:
            t.type = "INLINE_COMMENT"
        return t

    def t_sENTRY_TEXT(self, t):
        r'[^\n;]+?(?=\s{2,}|$|;)'
        if t.value.startswith('"') and t.value.endswith('"'):
            t.value = t.value[1:-1]
        t.value = t.value.rstrip()
        return t

    def t_sENTRY_newline(self, t):
        r'\n\n'
        self._state_begin('INITIAL', t)

    def t_sENTRY_eof(self, t):
        self._state_begin('INITIAL', t)

    # Common rules

    def t_ANY_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(self, t):
        self._hl_token(t)
        t.lexer.skip(1)

