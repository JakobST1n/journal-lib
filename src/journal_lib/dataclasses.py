import sys
from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime

FORCE_NOCOLOR = False
DATE_FORMAT = "%Y-%m-%d"


def set_force_nocolor(value: bool):
    global FORCE_NOCOLOR
    FORCE_NOCOLOR = value


def anesc(code: str):
    return "" if FORCE_NOCOLOR or not sys.stdout.isatty() else f"\u001b[{code}"


def format_amount(amount: str, currency: str | None = None) -> str:
    if currency is None:
        return amount
    if currency in ["NOK"]:
        return f"{amount} {currency}"
    if currency in ["$"]:
        return f"{currency}{amount}"
    return f"{amount} {currency}"


@dataclass
class JournalEntryTransaction:
    account: str
    currency: str | None
    amount: str | None
    comment: str | None
    sign: int = field(init=False)
    amount_value: int = field(init=False)

    def __post_init__(self):
        if self.amount is not None:
            if self.amount.startswith("-"):
                self.sign = -1
            else:
                self.sign = 1

            self.amount_value = Decimal(self.amount.lstrip("-+"))
        else:
            self.sign = 1

    def key(self):
        return (self.account, abs(Decimal(self.amount)), self.currency)


@dataclass
class JournalEntry:
    date: str
    cleared: bool
    pending: bool
    title: str
    effective_date: str | None
    transactions: list[JournalEntryTransaction]
    comments: list[str]

    def __str__(self):
        s = f"{anesc('34m')}{self.date}{anesc('0m')}"
        if self.effective_date is not None:
            s += f"={anesc('36m')}{self.effective_date}{anesc('0m')}"
        if self.cleared:
            s += f" {anesc('31m')}*{anesc('0m')}"
        if self.pending:
            s += f" {anesc('31m')}!{anesc('0m')}"
        s += f"  {anesc('36m')}{self.title}{anesc('0m')}\n"

        max_account_len = max(len(x.account) for x in self.transactions)
        for transaction in self.transactions:
            t = f"  {anesc('33m')}{transaction.account:{max_account_len}}{anesc('0m')}"
            if transaction.amount is not None:
                amount_code = "32m"
                if transaction.amount[0] == "-":
                    amount_code = "31m"
                else:
                    t += " "
                t += f"  {anesc(amount_code)}{format_amount(transaction.amount, transaction.currency)}{anesc('0m')}"
            if transaction.comment is not None:
                t += f"  {anesc('38m')}{transaction.comment}{anesc('0m')}"
            s += t + f"{anesc('0m')}\n"

        for comment in self.comments:
            s += f"  ; {anesc('38m')}{comment}{anesc('0m')}\n"
        return s + "\n"

    def __lt__(self, other):
        return self.date < other.date

    def get_comment_by_label(self, label: str):
        return next(
            (
                comment[len(label) + 2 :]
                for comment in self.comments
                if comment.startswith(label)
            ),
            None,
        )

    @property
    def from_dump_account(self):
        # Extract the first comment that starts with "FROM_DUMP_ACCOUNT", if any
        return self.get_comment_by_label("FROM_DUMP_ACCOUNT")

    @property
    def class_info(self):
        # Extract the first comment that starts with "FROM_DUMP_ACCOUNT", if any
        return self.get_comment_by_label("CLASS_INFO")

    def potential_transfer(self, other, date_skew=3):
        date_diff = abs((self.date - other.date).days)
        if date_diff > date_skew:
            return False
        return True

    def likely_transfer(self, other, date_skew=3):
        self_date = datetime.strptime(self.date, DATE_FORMAT)
        other_date = datetime.strptime(other.date, DATE_FORMAT)
        date_diff = abs((self_date - other_date).days)
        if date_diff > date_skew:
            return False

        # Check for inverse matching transactions
        for self_trans in self.transactions:
            inverse_match_found = False
            for other_trans in other.transactions:
                if (
                    self_trans.account != other_trans.account
                    and self_trans.amount_value == other_trans.amount_value
                    and self_trans.currency == other_trans.currency
                    and self_trans.sign != other_trans.sign
                ):
                    inverse_match_found = True
                    break

            if not inverse_match_found:
                return False

        if self.from_dump_account == other.from_dump_account:
            return False

        return True


@dataclass
class JournalAccountDef:
    account: str
    comment: str | None

    def __str__(self):
        s = f"{anesc('38m')}account {anesc('33m')}{self.account}{anesc('0m')}"
        if self.comment is not None:
            s += f" {anesc('38m')}{self.comment}{anesc('0m')}"
        return s + "\n"


@dataclass
class JournalCommodityDef:
    commodity: str
    format: str | None = None
    note: str | None = None
    nomarket: bool = False
    default: bool = False

    def __str__(self):
        s = f"{anesc('38m')}commodity {anesc('33m')}{self.commodity}{anesc('0m')}\n"
        for attr in ["format", "note", "nomarket", "default"]:
            if hasattr(self, attr) and getattr(self, attr) is not None:
                if isinstance(getattr(self, attr), bool) and not getattr(self, attr):
                    continue
                s += f"    {anesc('38m')}{attr}{anesc('0m')}"
                if isinstance(getattr(self, attr), str):
                    s += f" {anesc('36m')}{getattr(self, attr)}{anesc('0m')}"
                s += "\n"
        return s


@dataclass
class Journal:
    entries: list[JournalEntry]
    accounts: list[JournalAccountDef]
    commodities: list[JournalCommodityDef]

    def __str__(self):
        s = ""

        for account in self.accounts:
            s += f"{account}"
        s += "\n"

        for commodity in self.commodities:
            s += f"{commodity}"
        s += "\n"

        for entry in self.entries:
            s += f"{entry}"

        return s

    @staticmethod
    def from_elements(elements: list[str | JournalEntry]):
        entries = []
        accounts = []
        commodities = []

        for element in elements:
            if isinstance(element, JournalEntry):
                entries.append(element)
            elif isinstance(element, JournalAccountDef):
                accounts.append(element)
            elif isinstance(element, JournalCommodityDef):
                commodities.append(element)
            else:
                print(f"INVALID ELEMENT {element}")

        return Journal(entries=entries, accounts=accounts, commodities=commodities)
