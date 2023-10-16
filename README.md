# Journal-lib
Simple library for working with ledger journal files in python.

This library is mainly compromised of a parser for journal files,
and is intended to extract journal information to use for other processing.
It is mainly not intended to be used for modifying journal files,
as it will not be able to reproduce the journal files the way they looked
before being parsed.

The lexer and parser is powered by [PLY (Python Lex-Yacc)](https://github.com/dabeaz/ply/tree/master).
The sourcecode of PLY is included in this package in the `src/journal_lib/parse/ply/` directory.
Any licenses or copyright on other parts of this project is not applied to these files.
Please look at the header of these files for their copyright information.

## Usage
There are two main methods for parsing a journal.
```
from journal_lib import journal_from_str, journal_from_file

# Parse a journal consisting of 0 or more entries directly from a string
journal = journal_from_str("str")
# Parse a journal consisting of 0 or more entries from a file,
# recursively following all include statements
journal = journal_from_file(Path("personal.journal"))
```

The interface is defined in `src/dataclasses.py`.
The `Journal` object is returned from the mentioned functions.
It contains all the parsed lines (apart from global comments), with classes
for each separable part of the code.
The easiest way to use this is probably to just read those codes. 
These dataclasses generally only have a `__str__` method in addition to their fields.

This library is not fully featured, but it does support a lot of the most common
parts of the ledger journal format.

## Why
There doesn't seem to be any parsing libraries which has a clear datamodel
for its output from parsing.
So I wanted to make something which has the potential to be easily extended.
Since the grammar is built using PLY, it should be relatively straight forward
to add support for missing features, or even make a separate variant of the
lex/parse definitions for other flavours such as hledger.

## License
This doesn't have a license yet. 
Please don't make close-sourced copies of it,
but feel free to use it as you wish as a library,
as long as you make any changes or improvements to the code available to
other people freely (as in speech). 

