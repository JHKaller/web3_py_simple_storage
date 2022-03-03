from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
# get bytecode
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to local blockchain
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))  # local blockchain
chain_id = 1337
my_address = "0x5EFAE126AE357Da5B5e3AC7C52B073706de5bD91"
private_key = os.getenv("PRIVATE_KEY")

# for connecting to infura ethereum rinkeby testnet
# w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/fab85e5649974097899220c9d73bfb04")) #infura eth blockchain
# chain_id = 4
# my_address = "NAN"
# private_key = os.getenv("PRIVATE_KEY_TESTNET")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction count (not the NONCE we have learned about before)
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

# 2. Sign a transaction

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 3. Send this signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


# Working wih the contract, you need:
# Contract Adrress
# Contract ABI
# Call --> No change to the Blockchain, similar to view. You can call a payable function but its just a simulation.
# Transact --> State change to the Blockchain, similar to payable
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Lets get the iniial value of what we wan to change (favorite Number)
print(simple_storage.functions.retrieve().call())

# Build
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
# Sign
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

# Send
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
# Wait for transaction to finish
tx_store_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())
