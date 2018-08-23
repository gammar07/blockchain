import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

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


    def proof_of_work(self, last_proof):
        '''
        Simple proof of work algorithm:
        - find p' such that hash(pp') contains 4 leading 0s, where p is the previous proof,
        and p' is the new proof

        :param last_proof: <int>
        :return: <int>
        '''

        proof = 0
        while self.vaild_proof(last_proof, proof) is False:
            proof +=1

        return proof

    
    @staticmethod
    def vaild_proof(last_proof, proof):
        '''
        validates the proof: does hash(last_proof, proof) contain 4 leading 0?

        :param last_proof: <int> previous proof
        :param proof: <int> current proof
        :return: <bool> True if correct, false if not
        '''

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        
        return guess_hash[:4] == '0000'


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


    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node eg 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def valid_chain(self, chain):
        """
        determine of a given blockchain is valid

        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            #Check that the proof of work is correct
            if not self.vaild_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index +=1

        return True


    def resolve_conflicts(self):
        """ Consensus algoritm, resolves conflicts be replacing our chain with the longest one
        on the network.

        :return: <bool> True if chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # Only look for chain longer than our chain
        max_length = len(self.chain)

        # Grab the chains
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json().['length']
                chain = response.json()['chain']

                # Compare lenth of chains
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

            # Replace our chain if we discovered new, valid chain longer than ours
            if new_chain:
                self.chain = new_chain
                return True

            return False
        

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof of work to get the next proof

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Award for finding proof
    # Sender is '0' to signify it has been mined
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    # Forge the new bock by addint it to a chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    

    #Check that the fields are in the POST data
    required = ['sender', 'recipient', 'amount']
    
    if not all (k in values for k in required):
        return 'Missing values', 400
    

    # Create new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction wil be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    