import os
import time
import pickle
from web3 import Web3
from eth_utils import to_bytes, keccak
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
RPC_URL = os.getenv('RPC_URL')
ACCESS_LIST_FILE = 'access_list.pkl'

# Initialize web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# DBXen contract address and ABI
DBXEN_CONTRACT_ADDRESS = '0xF5c80c305803280B587F8cabBcCdC4d9BF522AbD'
DBXEN_ABI = '[{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"batchNumber\",\"type\":\"uint256\"}],\"name\":\"burnBatch\",\"outputs\":[],\"stateMutability\":\"payable\",\"type\":\"function\"}]'

# XEN token contract address and ABI for approval and burn function
XEN_CONTRACT_ADDRESS = '0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8'
XEN_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [
            {"name": "", "type": "bool"}
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "user", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "burn",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Global variables
GAS_PRICE_MULTIPLIER = 1.2  # Multiplier to ensure the gas price is slightly above the current network price
MAX_GAS_PRICE = w3.to_wei('7.0', 'gwei')  # Default max gas price
GAS_PRICE = w3.eth.gas_price  # Current gas price
ACCESS_LIST = None  # Store the generated access list here

def print_title():
    global GAS_PRICE
    GAS_PRICE = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    print(Fore.YELLOW + Style.BRIGHT + "  DBXen Access List Creation Tool")
    print(Fore.YELLOW + Style.BRIGHT + "  Created by TreeCityWes.eth for the Xen Ecosystem")
    print(Fore.YELLOW + Style.BRIGHT + "  https://buymeacoffee.com/treecitywes")
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Public Key: {PUBLIC_KEY}")
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Current Gas Price: {w3.from_wei(GAS_PRICE, 'gwei')} gwei")
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Max Gas Price Setting: {w3.from_wei(MAX_GAS_PRICE, 'gwei')} gwei")
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nThis tool empowers everyone to burn XEN by leveraging access lists. \nBy using this utility, you can easily create access lists and execute burns, \nmaking the process accessible to all and leveling the playing field in the XEN ecosystem.")
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")

def print_menu():
    print(Fore.YELLOW + Style.BRIGHT + "1. Set Max Gas Price")
    print(Fore.YELLOW + Style.BRIGHT + "2. Gather Access List (Burn 1 Batch)")
    print(Fore.YELLOW + Style.BRIGHT + "3. Burn with Access List")
    print(Fore.YELLOW + Style.BRIGHT + "4. Tip The Creator")
    print(Fore.YELLOW + Style.BRIGHT + "5. Exit")

def set_max_gas_price():
    global MAX_GAS_PRICE
    max_gas_price = float(input(Fore.CYAN + "Enter the max gas price in gwei: "))
    MAX_GAS_PRICE = w3.to_wei(max_gas_price, 'gwei')
    print(Fore.GREEN + f"Max gas price set to {max_gas_price} gwei")

def save_access_list(access_list):
    with open(ACCESS_LIST_FILE, 'wb') as file:
        pickle.dump(access_list, file)
    print(Fore.GREEN + "Access list saved to file.")

def load_access_list():
    global ACCESS_LIST
    if os.path.exists(ACCESS_LIST_FILE):
        with open(ACCESS_LIST_FILE, 'rb') as file:
            ACCESS_LIST = pickle.load(file)
        print(Fore.GREEN + "Previous access list detected and loaded.")
        return True
    return False

def gather_access_list():
    global ACCESS_LIST
    xen_storage_keys = [
        keccak(to_bytes(text='userMints')).hex(),
        keccak(to_bytes(text='userBurns')).hex()
    ]
    dbxen_storage_keys = [
        keccak(to_bytes(text='accCycleBatchesBurned')).hex(),
        keccak(to_bytes(text='accAccruedFees')).hex(),
        keccak(to_bytes(text='rewardPerCycle')).hex(),
        keccak(to_bytes(text='summedCycleStakes')).hex(),
        keccak(to_bytes(text='cycleTotalBatchesBurned')).hex(),
        keccak(to_bytes(text='accRewards')).hex()
    ]

    ACCESS_LIST = [
        {
            "address": XEN_CONTRACT_ADDRESS,
            "storageKeys": xen_storage_keys
        },
        {
            "address": DBXEN_CONTRACT_ADDRESS,
            "storageKeys": dbxen_storage_keys
        }
    ]
    save_access_list(ACCESS_LIST)
    print(Fore.GREEN + "Access list created and stored.")
    print(Fore.YELLOW + f"Access List: {ACCESS_LIST}")

def burn_batch(from_address, batch_number, use_access_list=False):
    nonce = w3.eth.get_transaction_count(from_address)
    gas_price = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
    chain_id = w3.eth.chain_id

    contract = w3.eth.contract(address=DBXEN_CONTRACT_ADDRESS, abi=DBXEN_ABI)
    burn_function = contract.functions.burnBatch(batch_number)

    tx = {
        'from': from_address,
        'value': int(0.289 * 10**18),  # Change this value according to your daily burn requirements
        'nonce': nonce,
        'maxFeePerGas': int(5.9 * 1e9),  # gwei limit
        'maxPriorityFeePerGas': int(0.13 * 1e9),  # tip
        'type': 2,
        'gas': 125000,
        'data': burn_function._encode_transaction_data()
    }

    if use_access_list and ACCESS_LIST:
        tx['accessList'] = ACCESS_LIST

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(Fore.GREEN + f"Transaction sent with hash: {tx_hash.hex()}")
    monitor_transaction(tx_hash)

def monitor_transaction(tx_hash):
    print(Fore.YELLOW + f"Monitoring transaction {tx_hash.hex()} for completion...")
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt and receipt.status == 1:
                print(Fore.GREEN + f"Transaction {tx_hash.hex()} confirmed in block {receipt['blockNumber']}")
                break
        except Exception as e:
            print(Fore.YELLOW + f"Transaction {tx_hash.hex()} is still pending or error occurred: {str(e)}")
            time.sleep(5)

def tip_the_creator():
    tip_amount = float(input(Fore.CYAN + "Enter the amount of ETH to tip the creator: "))
    tip_amount_wei = w3.to_wei(tip_amount, 'ether')
    nonce = w3.eth.get_transaction_count(PUBLIC_KEY)
    gas_price = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
    chain_id = w3.eth.chain_id

    # Resolve ENS name to Ethereum address
    creator_address = w3.ens.address('TreeCityWes.eth')
    if not creator_address:
        print(Fore.RED + "Error: Failed to resolve ENS name.")
        return

    tx = {
        'from': PUBLIC_KEY,
        'to': creator_address,
        'value': tip_amount_wei,
        'gas': 21000,
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': chain_id
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(Fore.GREEN + f"Tip transaction sent with hash: {tx_hash.hex()}")
    monitor_transaction(tx_hash)

def main_menu():
    print_title()
    if load_access_list():
        print(Fore.GREEN + "Previous access list detected. No need to burn to create a new access list.")
    print_menu()
    while True:
        choice = input(Fore.CYAN + "Please choose an option or press 'M' to display menu: ")
        if choice == '1':
            set_max_gas_price()
        elif choice == '2':
            if ACCESS_LIST is None:
                burn_batch(PUBLIC_KEY, 1)  # Burn one batch to gather access list
                gather_access_list()
            else:
                print(Fore.YELLOW + "Access list already exists. No need to burn to create a new one.")
        elif choice == '3':
            batch_number = int(input(Fore.CYAN + "Enter the number of batches to burn: "))
            burn_batch(PUBLIC_KEY, batch_number, use_access_list=True)
        elif choice == '4':
            tip_the_creator()
        elif choice == '5':
            break
        elif choice.lower() == 'm':
            print_title()
            print_menu()
        else:
            print(Fore.RED + "Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()
