from structure import datastruct
class Ledger:
    def __init__(self):
        self.transactions = []
    
    def add(self, tx: datastruct):
        self.transactions.append(tx)
    
    def list(self):
        return self.transactions
    
    def delete(self, index: int):
        del self.transactions[index]
