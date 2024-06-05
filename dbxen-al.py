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

# Initialize web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# DBXen contract address and ABI
DBXEN_CONTRACT_ADDRESS = '0xF5c80c305803280B587F8cabBcCdC4d9BF522AbD'
DBXEN_ABI = [
    {"inputs":[{"internalType":"uint256","name":"batchNumber","type":"uint256"}],"name":"burnBatch","outputs":[],"stateMutability":"payable","type":"function"}
]

# XEN token contract address and ABI for approval and burn function
XEN_CONTRACT_ADDRESS = '0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8'
XEN_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type":"address"},
            {"name": "_value", "type":"uint256"}
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
        "constant": True,
        "inputs": [
            {"name": "address", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [
            {"name": "", "type": "uint256"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Global variables
GAS_PRICE_MULTIPLIER = 1  # Multiplier to ensure the gas price is slightly above the current network price
MAX_GAS_PRICE = w3.to_wei('10.0', 'gwei')  # Default max gas price
GAS_PRICE = w3.eth.gas_price  # Current gas price

ACCESS_LIST_FILE = "access_list.pkl"

def get_eth_balance(address):
    balance = w3.eth.get_balance(address)
    return w3.from_wei(balance, 'ether')

def get_xen_balance(address):
    xen_contract = w3.eth.contract(address=XEN_CONTRACT_ADDRESS, abi=XEN_ABI)
    balance = xen_contract.functions.balanceOf(address).call()
    return w3.from_wei(balance, 'ether')

def get_batches():
    xen_balance = get_xen_balance(PUBLIC_KEY)
    batch_size = 2500000  # Assuming each batch is 2,500,000 XEN
    return int(xen_balance // batch_size)

def print_title():
    global GAS_PRICE
    GAS_PRICE = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
    eth_balance = get_eth_balance(PUBLIC_KEY)
    xen_balance = get_xen_balance(PUBLIC_KEY)
    batches_available = get_batches()
    
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    print(Fore.YELLOW + Style.BRIGHT + "  DBXen Access List Creation Tool")
    print(Fore.YELLOW + Style.BRIGHT + "  Created by TreeCityWes.eth for the Xen Ecosystem")
    print(Fore.YELLOW + Style.BRIGHT + "  https://buymeacoffee.com/treecitywes")
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    print(Fore.GREEN + Style.BRIGHT + "Public Key: " + Fore.YELLOW + f"{PUBLIC_KEY}")
    print(Fore.GREEN + Style.BRIGHT + "Current Gas Price: " + Fore.YELLOW + f"{w3.from_wei(GAS_PRICE, 'gwei')} gwei")
    print(Fore.GREEN + Style.BRIGHT + "Max Gas Price Setting: " + Fore.YELLOW + f"{w3.from_wei(MAX_GAS_PRICE, 'gwei')} gwei")
    print(Fore.GREEN + Style.BRIGHT + "ETH Holdings: " + Fore.YELLOW + f"{eth_balance} ETH")
    print(Fore.GREEN + Style.BRIGHT + "XEN Holdings: " + Fore.YELLOW + f"{xen_balance} XEN")
    print(Fore.GREEN + Style.BRIGHT + "Batches Available to Burn: " + Fore.YELLOW + f"{batches_available}")
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    print(Fore.GREEN + Style.BRIGHT + "\nThis tool empowers everyone to burn XEN by leveraging access lists. \nBy using this utility, you can easily create access lists and execute burns, \nmaking the process accessible to all and leveling the playing field in the XEN ecosystem.")
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")

def print_menu():
    print(Fore.YELLOW + Style.BRIGHT + "1. Set Max Gas Price")
    print(Fore.YELLOW + Style.BRIGHT + "2. Check if Access List Exists")
    print(Fore.YELLOW + Style.BRIGHT + "3. Approve XEN Tokens")
    print(Fore.YELLOW + Style.BRIGHT + "4. Burn 1 Batch to Create Access List")
    print(Fore.YELLOW + Style.BRIGHT + "5. Burn Batches Using Access List")
    print(Fore.YELLOW + Style.BRIGHT + "6. Tip The Creator")
    print(Fore.YELLOW + Style.BRIGHT + "7. Exit")

def set_max_gas_price():
    global MAX_GAS_PRICE
    try:
        max_gas_price = float(input(Fore.CYAN + "Enter the max gas price in gwei: "))
        MAX_GAS_PRICE = w3.to_wei(max_gas_price, 'gwei')
        print(Fore.GREEN + f"Max gas price set to {max_gas_price} gwei")
    except Exception as e:
        print(Fore.RED + f"Error setting max gas price: {e}")

def check_access_list():
    try:
        if os.path.exists(ACCESS_LIST_FILE) and os.path.getsize(ACCESS_LIST_FILE) > 0:
            with open(ACCESS_LIST_FILE, 'rb') as f:
                access_list = pickle.load(f)
            print(Fore.GREEN + f"Access List exists: {access_list}")
        else:
            print(Fore.RED + "Access List does not exist.")
    except EOFError:
        print(Fore.RED + "Access List file is empty.")
    except Exception as e:
        print(Fore.RED + f"Error checking Access List: {e}")

def approve_xen_tokens(from_address, batches):
    nonce = w3.eth.get_transaction_count(from_address)
    gas_price = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
    chain_id = w3.eth.chain_id

    xen_contract = w3.eth.contract(address=XEN_CONTRACT_ADDRESS, abi=XEN_ABI)
    approval_amount = batches * 2_500_000 * 10**18
    approve_function = xen_contract.functions.approve(DBXEN_CONTRACT_ADDRESS, approval_amount)

    tx = {
        'from': from_address,
        'to': XEN_CONTRACT_ADDRESS,
        'value': '0x0',
        'gas': '0x0',
        'gasPrice': hex(gas_price),
        'nonce': hex(nonce),
        'chainId': hex(chain_id),
        'data': approve_function._encode_transaction_data()
    }

    gas_estimate = w3.eth.estimate_gas(tx)
    tx['gas'] = hex(gas_estimate)

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(Fore.GREEN + f"Approval transaction sent with hash: {tx_hash.hex()}")
    monitor_transaction(tx_hash)

def calculate_protocol_fee(start_gas, batch_number, gas_price):
    MAX_BPS = 100000
    discount = batch_number * (MAX_BPS - 5 * batch_number)
    protocol_fee = ((start_gas + 39400) * gas_price * discount) / MAX_BPS
    protocol_fee_eth = w3.from_wei(int(protocol_fee), 'ether')
    print(Fore.LIGHTGREEN_EX + f"Discount Calculation: {batch_number} * ({MAX_BPS} - 5 * {batch_number}) = {discount}")
    print(Fore.LIGHTGREEN_EX + f"Protocol Fee Calculation: (({start_gas} + 39400) * {gas_price} * {discount}) / {MAX_BPS} = {protocol_fee_eth} ETH")
    return protocol_fee_eth

def create_access_list():
    nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(PUBLIC_KEY))
    tx_gas_price = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
    if tx_gas_price > MAX_GAS_PRICE:
        tx_gas_price = MAX_GAS_PRICE
    elif tx_gas_price < MAX_GAS_PRICE / 2:
        tx_gas_price = int(MAX_GAS_PRICE * 1.1)  # Set to higher priority if below half of max gas price
    chain_id = w3.eth.chain_id

    contract = w3.eth.contract(address=DBXEN_CONTRACT_ADDRESS, abi=DBXEN_ABI)
    burn_function = contract.functions.burnBatch(1)  # Burn 1 batch to create the access list

    start_gas = int(w3.eth.estimate_gas({
        'to': DBXEN_CONTRACT_ADDRESS,
        'from': PUBLIC_KEY,
        'data': burn_function._encode_transaction_data()
    }) * 1.2)

    protocol_fee = calculate_protocol_fee(start_gas, 1, tx_gas_price)

    print(Fore.LIGHTGREEN_EX + f"Start Gas: {start_gas}")
    print(Fore.LIGHTGREEN_EX + f"Gas Price: {tx_gas_price}")
    print(Fore.LIGHTGREEN_EX + f"Protocol Fee: {protocol_fee}")

    tx = {
        'from': PUBLIC_KEY,
        'to': DBXEN_CONTRACT_ADDRESS,
        'value': hex(int(w3.to_wei(protocol_fee, 'ether'))),
        'gas': hex(start_gas),
        'gasPrice': hex(tx_gas_price),
        'nonce': hex(nonce),
        'chainId': hex(chain_id),
        'data': burn_function._encode_transaction_data()
    }

    try:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(Fore.GREEN + f"Burn transaction sent with hash: {tx_hash.hex()}")
        monitor_transaction(tx_hash)

        # After confirming the transaction, create the access list
        access_list_response = w3.provider.make_request("eth_createAccessList", [tx, "latest"])
        if 'result' not in access_list_response:
            print(Fore.RED + f"Error in response: {access_list_response}")
            return
        
        with open(ACCESS_LIST_FILE, 'wb') as f:
            pickle.dump(access_list_response['result']['accessList'], f)
        print(Fore.GREEN + "Access List created and saved.")
    except Exception as e:
        print(Fore.RED + f"Error creating Access List: {e}")

def burn_batch(batches, use_access_list=False):
    try:
        nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(PUBLIC_KEY))
        tx_gas_price = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
        if tx_gas_price > MAX_GAS_PRICE:
            tx_gas_price = MAX_GAS_PRICE
        elif tx_gas_price < MAX_GAS_PRICE / 2:
            tx_gas_price = int(MAX_GAS_PRICE * 1.1)  # Set to higher priority if below half of max gas price
        chain_id = w3.eth.chain_id

        contract = w3.eth.contract(address=DBXEN_CONTRACT_ADDRESS, abi=DBXEN_ABI)
        burn_function = contract.functions.burnBatch(batches)

        start_gas = int(w3.eth.estimate_gas({
            'to': DBXEN_CONTRACT_ADDRESS, 
            'from': PUBLIC_KEY, 
            'data': burn_function._encode_transaction_data()
        }) * 1.2)

        # Calculate protocol fee with the new gas estimate from access list
        if use_access_list and os.path.exists(ACCESS_LIST_FILE) and os.path.getsize(ACCESS_LIST_FILE) > 0:
            with open(ACCESS_LIST_FILE, 'rb') as f:
                access_list = pickle.load(f)
            access_list_gas = sum([access['storageKey'] for access in access_list])  # Example sum, adjust as needed
            start_gas = max(start_gas, access_list_gas)  # Use higher gas estimate
            print(Fore.GREEN + "Using saved Access List.")

        protocol_fee = calculate_protocol_fee(start_gas, batches, tx_gas_price)

        print(Fore.LIGHTGREEN_EX + f"Start Gas: {start_gas}")
        print(Fore.LIGHTGREEN_EX + f"Gas Price: {tx_gas_price}")
        print(Fore.LIGHTGREEN_EX + f"Protocol Fee: {protocol_fee}")

        tx = {
            'from': PUBLIC_KEY,
            'to': DBXEN_CONTRACT_ADDRESS,
            'value': hex(int(w3.to_wei(protocol_fee, 'ether'))),
            'gas': hex(start_gas),
            'gasPrice': hex(tx_gas_price),
            'nonce': hex(nonce),
            'chainId': hex(chain_id),
            'data': burn_function._encode_transaction_data()
        }

        if use_access_list and os.path.exists(ACCESS_LIST_FILE) and os.path.getsize(ACCESS_LIST_FILE) > 0:
            with open(ACCESS_LIST_FILE, 'rb') as f:
                access_list = pickle.load(f)
            tx['accessList'] = access_list
            print(Fore.GREEN + "Using saved Access List.")

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(Fore.GREEN + f"Transaction sent with hash: {tx_hash.hex()}")
        monitor_transaction(tx_hash)
    except Exception as e:
        print(Fore.RED + f"Error burning batch: {e}")

def tip_the_creator():
    try:
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
            'value': hex(tip_amount_wei),
            'gas': hex(21000),
            'gasPrice': hex(gas_price),
            'nonce': hex(nonce),
            'chainId': hex(chain_id)
        }

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(Fore.GREEN + f"Tip transaction sent with hash: {tx_hash.hex()}")
        monitor_transaction(tx_hash)
    except Exception as e:
        print(Fore.RED + f"Error tipping the creator: {e}")

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

def main_menu():
    print_title()
    print_menu()
    while True:
        try:
            choice = input(Fore.CYAN + "Please choose an option or press 'M' to display menu: ")
            if choice == '1':
                set_max_gas_price()
            elif choice == '2':
                check_access_list()
            elif choice == '3':
                batches = int(input(Fore.CYAN + "Enter the number of batches to approve: "))
                approve_xen_tokens(PUBLIC_KEY, batches)
            elif choice == '4':
                create_access_list()
            elif choice == '5':
                batches = int(input(Fore.CYAN + "Enter the number of batches to burn: "))
                burn_batch(batches, use_access_list=True)
            elif choice == '6':
                tip_the_creator()
            elif choice == '7':
                break
            elif choice.lower() == 'm':
                print_title()
                print_menu()
            else:
                print(Fore.RED + "Invalid choice. Please select a valid option.")
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main_menu()
