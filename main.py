from datetime import date

import typer

from cores.ledger import Ledger
from cores.structure import datastruct

app = typer.Typer()
ledger = Ledger("data.db")

@app.command()
def add_transaction():
    amount = float(input("Enter amount: "))
    type = input("Enter type (income/expense): ")
    category = input("Enter category: ")
    note = input("Enter note: ")
    date_input = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
    if date_input:
        tx_date = date.fromisoformat(date_input)
    else:
        tx_date = date.today()
    tx = datastruct(id=None, amount=amount, type=type, category=category, note=note, date=tx_date)
    ledger.add(tx)

@app.command()
def list_transactions():
    transactions = ledger.list()
    for tx in transactions:
        print(tx)

@app.command()
def delete_transaction(tx_id: int):
    success = ledger.delete(tx_id)
    if success:
        print(f"Transaction with id {tx_id} deleted.")
    else:
        print(f"Transaction with id {tx_id} not found.")

if __name__ == "__main__":
    app()
