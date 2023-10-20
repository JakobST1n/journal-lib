from pathlib import Path
from journal_lib.dataclasses import Journal
from journal_lib.parse import JournalParser, JournalLexer, preprocess_includes


def journal_from_str(data: str, debug: bool = False) -> Journal:
    """Read a string of Journal entries into a Journal object"""
    if debug:
        print("= Building lexer ===========")
    lexer = JournalLexer(debug=debug)
    if debug:
        print("= Building parser ==========")
    parser = JournalParser(debug=debug)
    if debug:
        print("= PARSE ====================")
    journal = parser.parse(data, lexer=lexer)
    if debug:
        print("= JOURNAL ==================")
    return journal


def journal_from_file(filename: Path, debug: bool = False) -> Journal:
    """Read a journal file into a Journal object"""
    journal_raw = preprocess_includes(filename)
    return journal_from_str(journal_raw, debug=debug)


def test():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-f", "--file", help="The journal file to read")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Print more debug information from lexing and parsing",
    )
    args = parser.parse_args()

    if args.file is not None:
        print(journal_from_file(Path(args.file), debug=args.debug))

    else:
        # Just a test string which includes most of the supported features of the parser
        data = """
account Expenses:account one
account Assets:Cash            ; type:X

commodity APPL

commodity USD
    note Us dollars
    format 1000.00 NOK
    nomarket
    default

2023-10-14=2023-10-14 * "Groceries"
    ; entry comment
    Expenses:account one  $50.00  ; post comment
    Assets:Cash           -50 NOK
    Assets:Cash           50 NOK
    ; entry comment

; global comment

comment
this is a block comment
end comment

2023/10/14 ! papers
    Expenses:account one  $50.00
    Assets:Cash          
    """
        print(journal_from_str(data, debug=args.debug))
