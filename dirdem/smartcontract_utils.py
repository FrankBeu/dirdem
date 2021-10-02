from vyper.cli import vyper_compile
from web3 import Web3


# web3.py instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))


def deploy_contract(contract_interface):
    # Instantiate and deploy contract
    contract = w3.eth.contract(
        abi=contract_interface["abi"], bytecode=contract_interface["bytecode"]
    )
    # Get transaction hash from deployed contract
    tx_hash = contract.constructor().transact({'from': w3.eth.accounts[1]})

    # Get tx receipt to get contract address
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt["contractAddress"]


def deploy_n_transact(file_path):
    output_formats = ["bytecode", "abi"]
    contract = vyper_compile.compile_files(file_path, output_formats)[file_path[0]]
    contract_address = deploy_contract(contract)
    return contract_address, contract["abi"]
