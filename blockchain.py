class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []


    def new_block(self):
        # Create a new block and add to the chain
        pass

    
    def new_transaction(self, sender, recipient, amount):
        '''
        Creates a new transaction to go into the next block

        :param sender:      <str> Address of the sender
        :param recipient:   <str> Address of the recipient
        :param amount       <int> Amount
        :return             <int> The index of the block that holds transcaction
        '''

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] +1


    @staticmethod
    def hash(block):
        # Hash a block
        pass

    
    @property
    def last_block(self):
        # Returns last block in the chain
        pass