from datetime import datetime

from journal_lib.parse.parsewrapper import ParseWrapper
from journal_lib.parse.lexers.l_ledger import JournalLexer
from journal_lib.dataclasses import (
    Journal,
    JournalEntry,
    JournalEntryTransaction,
    JournalAccountDef,
    JournalCommodityDef,
)


class JournalParser(ParseWrapper):
    tokens = JournalLexer.tokens

    def p_journal(self, p):
        """journal : elements"""
        p[0] = Journal.from_elements(p[1])

        if self.debug:
            for x in p[1]:
                print(repr(x))

    def p_elements(self, p):
        """elements : elements element
                    | element"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_element_entry(self, p):
        """element : DATE effective_date status TEXT transactions"""
        p[0] = JournalEntry(
            date=p[1],
            effective_date=p[2],
            cleared=p[3]["cleared"],
            pending=p[3]["pending"],
            title=p[4],
            transactions=p[5]["transactions"],
            comments=p[5]["comments"],
        )

    def p_element_account(self, p):
        """element : KW_ACCOUNT TEXT COMMENT
                   | KW_ACCOUNT TEXT"""
        p[0] = JournalAccountDef(account=p[2], comment=p[3] if len(p) > 3 else None)

    def p_element_commodity(self, p):
        """element : KW_COMMODITY TEXT commodity_attributes"""
        p[0] = JournalCommodityDef(commodity=p[2], **p[3])

    def p_commodity_attributes(self, p):
        """commodity_attributes : COMMODITY_FORMAT TEXT commodity_attributes
                                | COMMODITY_NOTE TEXT commodity_attributes
                                | COMMODITY_NOMARKET commodity_attributes
                                | COMMODITY_DEFAULT commodity_attributes
                                | empty
        """
        p[0] = {}
        if p[1] == "format":
            p[0]["format"] = p[2]
        elif p[1] == "note":
            p[0]["note"] = p[2]
        elif p[1] == "nomarket":
            p[0]["nomarket"] = True
        elif p[1] == "default":
            p[0]["default"] = True
        if len(p) > 3 and p[3]:
            p[0].update(p[3])

    def p_effective_date(self, p):
        """effective_date : ENTRY_EFFECTIVE_DATE_SEPARATOR DATE
                          | empty"""
        p[0] = p[2] if p[1] else None

    def p_status(self, p):
        """status : ENTRY_STATUS
                  | empty"""
        p[0] = (
            {"cleared": p[1] == "*", "pending": p[1] == "!"}
            if p[1]
            else {"cleared": False, "pending": False}
        )

    def p_empty(self, p):
        """empty :"""
        pass

    def p_transactions(self, p):
        """transactions : transactions transaction"""
        p[0] = {
            "comments": p[1]["comments"],
            "transactions": p[1]["transactions"] + [p[2]],
        }

    def p_comments(self, p):
        """transactions : transactions COMMENT"""
        p[0] = {
            "comments": p[1]["comments"] + [p[2]],
            "transactions": p[1]["transactions"],
        }

    def p_transactions_single(self, p):
        """transactions : transaction"""
        p[0] = {"comments": [], "transactions": [p[1]]}

    def p_transactions_comment_single(self, p):
        """transactions : COMMENT"""
        p[0] = {"comments": [p[1]], "transactions": []}

    def p_amount_prefixed(self, p):
        """amount : COMMODITY AMOUNT"""
        p[0] = {"currency": p[1], "amount": p[2]}

    def p_amount_suffixed(self, p):
        """amount : AMOUNT COMMODITY"""
        p[0] = {"currency": p[2], "amount": p[1]}

    def p_transaction_with_amount(self, p):
        """transaction : TEXT amount INLINE_COMMENT
                       | TEXT amount"""

        p[0] = JournalEntryTransaction(
            account=p[1],
            currency=p[2]["currency"],
            amount=p[2]["amount"],
            comment=p[3] if len(p) > 3 else None,
        )

    def p_transaction_without_amount(self, p):
        """transaction : TEXT INLINE_COMMENT
                       | TEXT"""
        p[0] = JournalEntryTransaction(
            account=p[1],
            currency=None,
            amount=None,
            comment=p[2] if len(p) > 2 else None,
        )

    def p_error(self, p):
        if p:
            self._hl_token(p)
        else:
            print("Syntax error at EOF")
