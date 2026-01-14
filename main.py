from datetime import date
from typing import Optional

import typer

from cores.ledger import Ledger
from cores.structure import Transaction

app = typer.Typer(help="Simple bookkeeping CLI.")
ledger = Ledger("data.db")

ALLOWED_TYPES = {"income", "expense"}


def _parse_date(value: Optional[str], label: str) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter(f"{label} must be YYYY-MM-DD.") from exc


def _normalize_type(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in ALLOWED_TYPES:
        raise typer.BadParameter("Type must be 'income' or 'expense'.")
    return normalized


def _print_transactions(transactions: list[Transaction]) -> None:
    header = (
        f"{'ID':>4}  {'DATE':<10}  {'TYPE':<7}  {'AMOUNT':>10}  "
        f"{'CATEGORY':<12}  NOTE"
    )
    typer.echo(header)
    typer.echo("-" * len(header))
    for tx in transactions:
        note = tx.note or ""
        typer.echo(
            f"{tx.id:>4}  {tx.date.isoformat():<10}  {tx.type:<7}  "
            f"{tx.amount:>10.2f}  {tx.category:<12}  {note}"
        )


@app.command("add")
def add_transaction(
    amount: float = typer.Option(..., prompt=True, help="Transaction amount."),
    tx_type: str = typer.Option(
        ..., "--type", "-t", prompt=True, help="income or expense."
    ),
    category: str = typer.Option(
        "general", "--category", "-c", prompt=True, help="Category name."
    ),
    note: str = typer.Option("", "--note", "-n", prompt=False, help="Optional note."),
    tx_date: Optional[str] = typer.Option(
        None, "--date", "-d", help="Date in YYYY-MM-DD (defaults to today)."
    ),
) -> None:
    if amount <= 0:
        raise typer.BadParameter("Amount must be positive.")
    normalized_type = _normalize_type(tx_type)
    parsed_date = _parse_date(tx_date, "Date") or date.today()

    tx = Transaction(
        id=None,
        amount=amount,
        type=normalized_type,
        category=category.strip() or "general",
        note=note.strip(),
        date=parsed_date,
    )
    ledger.add(tx)
    typer.echo("Transaction added.")


@app.command("list")
def list_transactions(
    tx_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by type (income/expense)."
    ),
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="Filter by category."
    ),
    start_date: Optional[str] = typer.Option(
        None, "--from", help="Start date (YYYY-MM-DD)."
    ),
    end_date: Optional[str] = typer.Option(
        None, "--to", help="End date (YYYY-MM-DD)."
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Limit number of rows."
    ),
) -> None:
    normalized_type = _normalize_type(tx_type) if tx_type else None
    parsed_start = _parse_date(start_date, "Start date")
    parsed_end = _parse_date(end_date, "End date")

    transactions = ledger.list(
        tx_type=normalized_type,
        category=category,
        start_date=parsed_start,
        end_date=parsed_end,
        limit=limit,
    )
    if not transactions:
        typer.echo("No transactions found.")
        return
    _print_transactions(transactions)


@app.command("summary")
def summary(
    start_date: Optional[str] = typer.Option(
        None, "--from", help="Start date (YYYY-MM-DD)."
    ),
    end_date: Optional[str] = typer.Option(
        None, "--to", help="End date (YYYY-MM-DD)."
    ),
) -> None:
    parsed_start = _parse_date(start_date, "Start date")
    parsed_end = _parse_date(end_date, "End date")
    totals = ledger.summary(parsed_start, parsed_end)
    typer.echo(f"Income : {totals['income']:.2f}")
    typer.echo(f"Expense: {totals['expense']:.2f}")
    typer.echo(f"Balance: {totals['balance']:.2f}")

    categories = totals["categories"]
    if categories:
        typer.echo("")
        typer.echo("By category:")
        for category in sorted(categories):
            stats = categories[category]
            typer.echo(
                f"- {category}: +{stats['income']:.2f} "
                f"-{stats['expense']:.2f} = {stats['balance']:.2f}"
            )


@app.command("delete")
def delete_transaction(tx_id: int) -> None:
    success = ledger.delete(tx_id)
    if success:
        typer.echo(f"Transaction with id {tx_id} deleted.")
    else:
        typer.echo(f"Transaction with id {tx_id} not found.")


if __name__ == "__main__":
    app()
