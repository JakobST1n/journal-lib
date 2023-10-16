import sys
from dataclasses import dataclass

FORCE_NOCOLOR = False

def set_force_nocolor(value: bool):
    global FORCE_NOCOLOR
    FORCE_NOCOLOR = value

def anesc(code: str):
    return "" if FORCE_NOCOLOR or not sys.stdout.isatty() else f"\u001b[{code}"

def format_amount(amount: str, currency: str | None = None) -> str:
    if currency is None:
        return amount
    if currency in ['NOK']:
        return f"{amount} {currency}"
    if currency in ['$']:
        return f"{currency}{amount}"
    return f"{amount} {currency}"

@dataclass
class JournalEntryTransaction:
    account: str
    currency: str | None
    amount: str | None
    comment: str | None

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
                if (transaction.amount[0] == "-"):
                    amount_code = "31m"
                t += f"  {anesc(amount_code)}{format_amount(transaction.amount, transaction.currency)}{anesc('0m')}"
            if transaction.comment is not None:
                t += f"  {anesc('38m')}{transaction.comment}{anesc('0m')}"
            s += t + f"{anesc('0m')}\n"

        for comment in self.comments:
            s += f"  {anesc('38m')}{comment}{anesc('0m')}\n"
        return s + "\n"

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

