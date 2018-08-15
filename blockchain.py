class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []


    def new_block(self):
        # Create a new block and add to the chain
        pass

    
    def new_transaction(self):
        # Add a new transaction to the list
        pass


    @staticmethod
    def hash(block):
        # Hash a block
        pass

    
    @property
    def last_block(self):
        # Returns last block in the chain
        pass