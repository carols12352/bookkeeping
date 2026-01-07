import typer
from typing import Optional
from cores.ledger import Ledger
from cores.structure import datastruct
from datetime import date

app = typer.Typer()
ledger = Ledger()

@app.command()
def add_transaction():
    id = input("Enter transaction ID: ")
    amount = float(input("Enter amount: "))
    type = input("Enter type (income/expense): ")
    category = input("Enter category: ")
    note = input("Enter note: ")
    date_input = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
    if date_input:
        tx_date = date.fromisoformat(date_input)
    tx_date = date or date.today()
    tx = datastruct(id=id, amount=amount, type=type, category=category, note=note, date=tx_date)
    ledger.add(tx)

@app.command()
def list_transactions():
    transactions = ledger.list()
    for tx in transactions:
        print(tx)

@app.command()
def delete_transaction(id: int):
    success = ledger.delete(id)
    if success:
        print(f"Transaction with id {id} deleted.")
    else:
        print(f"Transaction with id {id} not found.")

if __name__ == "__main__":
    app()