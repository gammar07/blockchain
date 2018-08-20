import hashlib
import json
from time import time


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)


    def new_block(self, proof, previous_hash=None):
        '''
        Create a new block and add to the chain

        :param proof: <int> The proof given by the proof of work algoritm
        :param previous_hash: (optional) <str> hash of the previous block
        :return: <dict> New block
        '''

        block = {
            'index' : len(self.chain) +1,
            'timestamp' : time(),
            'transactions' : self.current_transactions,
            'proof': proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1])
        }
        
        # Reset transasctions
        self.current_transactions = []

        self.chain.append(block)
        return block

    
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
        '''
        Creates a SHA-256 hash of a Block
        :param block <dict> block
        return <str>
        '''

        #Make sure dictionary is ordered to avoid inconsistant hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    
    @property
    def last_block(self):
        # Returns last block in the chain
        return self.chain[-1]