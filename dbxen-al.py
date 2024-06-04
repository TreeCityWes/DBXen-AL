import os
import time
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
    {"inputs":[{"internalType":"uint256","name":"batchNumber","type":"uint256"}],"name":"burnBatch","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"accCycleBatchesBurned","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"userAddress","type":"address"},{"indexed":False,"internalType":"uint256","name":"batchNumber","type":"uint256"}],"name":"Burn","type":"event"},
    {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"accAccruedFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
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
        "constant": False,
        "inputs": [
            {"name": "user", "type":"address"},
            {"name": "amount", "type":"uint256"}
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
    print(Fore.YELLOW + Style.BRIGHT + "2. Detect with Access List")
    print(Fore.YELLOW + Style.BRIGHT + "3. Gather Storage Keys")
    print(Fore.YELLOW + Style.BRIGHT + "4. Create Access List")
    print(Fore.YELLOW + Style.BRIGHT + "5. Approve")
    print(Fore.YELLOW + Style.BRIGHT + "6. Burn with Access List")
    print(Fore.YELLOW + Style.BRIGHT + "7. Tip The Creator")
    print(Fore.YELLOW + Style.BRIGHT + "8. Exit")

def set_max_gas_price():
    global MAX_GAS_PRICE
    max_gas_price = float(input(Fore.CYAN + "Enter the max gas price in gwei: "))
    MAX_GAS_PRICE = w3.to_wei(max_gas_price, 'gwei')
    print(Fore.GREEN + f"Max gas price set to {max_gas_price} gwei")

def detect_with_access_list():
    storage_key = "0x" + keccak(to_bytes(text='accCycleBatchesBurned')).hex()
    print(Fore.GREEN + f"Storage Key for accCycleBatchesBurned: {storage_key}")
    print(Fore.RED + "Access list does not exist or is not used by the contract.")

def gather_storage_keys():
    storage_keys = [
        keccak(to_bytes(text='accCycleBatchesBurned')).hex(),
        keccak(to_bytes(text='accAccruedFees')).hex(),
        keccak(to_bytes(text='rewardPerCycle')).hex(),
        keccak(to_bytes(text='summedCycleStakes')).hex(),
        keccak(to_bytes(text='cycleTotalBatchesBurned')).hex(),
        keccak(to_bytes(text='accRewards')).hex(),
        keccak(to_bytes(text='userMints')).hex(),
        keccak(to_bytes(text='userBurns')).hex()
    ]
    print(Fore.GREEN + f"Storage Keys: {storage_keys}")

def create_access_list():
    dbxen_storage_keys = [
        "0x" + keccak(to_bytes(text='accCycleBatchesBurned')).hex(),
        "0x" + keccak(to_bytes(text='accAccruedFees')).hex(),
        "0x" + keccak(to_bytes(text='rewardPerCycle')).hex(),
        "0x" + keccak(to_bytes(text='summedCycleStakes')).hex(),
        "0x" + keccak(to_bytes(text='cycleTotalBatchesBurned')).hex(),
        "0x" + keccak(to_bytes(text='accRewards')).hex()
    ]

    xen_storage_keys = [
        "0x" + keccak(to_bytes(text='userMints')).hex(),
        "0x" + keccak(to_bytes(text='userBurns')).hex()
    ]

    access_list = [
        {
            "address": DBXEN_CONTRACT_ADDRESS,
            "storageKeys": dbxen_storage_keys
        },
        {
            "address": XEN_CONTRACT_ADDRESS,
            "storageKeys": xen_storage_keys
        }
    ]
    print(Fore.GREEN + f"Storage Keys for Access List: {dbxen_storage_keys + xen_storage_keys}")
    print(Fore.YELLOW + f"Access List: {access_list}")
    return access_list

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
        'value': 0,
        'gas': 0,
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': chain_id,
        'data': approve_function._encode_transaction_data()
    }

    gas_estimate = w3.eth.estimate_gas(tx)
    tx['gas'] = gas_estimate

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

def burn_with_access_list(from_address, batch_number):
    nonce = w3.eth.get_transaction_count(from_address)
    tx_gas_price = int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
    if tx_gas_price > MAX_GAS_PRICE:
        tx_gas_price = MAX_GAS_PRICE
    chain_id = w3.eth.chain_id

    access_list = create_access_list()

    dbxen_contract = w3.eth.contract(address=DBXEN_CONTRACT_ADDRESS, abi=DBXEN_ABI)
    burn_function = dbxen_contract.functions.burnBatch(batch_number)

    try:
        # Estimate gas usage with a safety margin
        start_gas = int(w3.eth.estimate_gas({'to': DBXEN_CONTRACT_ADDRESS, 'from': from_address, 'data': burn_function._encode_transaction_data(), 'accessList': access_list}) * 1.2)

        # Calculate protocol fee
        protocol_fee = calculate_protocol_fee(start_gas, batch_number, tx_gas_price)

        tx = {
            'from': from_address,
            'to': DBXEN_CONTRACT_ADDRESS,
            'value': w3.to_wei(protocol_fee, 'ether'),
            'gas': start_gas,
            'gasPrice': tx_gas_price,
            'nonce': nonce,
            'chainId': chain_id,
            'data': burn_function._encode_transaction_data(),
            'accessList': access_list
        }

        # Debug information
        print(Fore.LIGHTGREEN_EX + f"Start gas: {start_gas}")
        print(Fore.LIGHTGREEN_EX + f"Transaction gas price: {w3.from_wei(tx_gas_price, 'gwei')} gwei")
        print(Fore.LIGHTGREEN_EX + f"Batch number: {batch_number}")
        print(Fore.LIGHTGREEN_EX + f"Protocol fee: {protocol_fee} ETH")

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(Fore.GREEN + f"Transaction sent with hash: {tx_hash.hex()}")
        monitor_transaction(tx_hash)
    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}")
        if 'insufficient allowance' in str(e):
            print(Fore.RED + "Error: Insufficient allowance. Please approve the DBXen contract to burn your XEN tokens.")
        elif 'intrinsic gas too low' in str(e):
            print(Fore.RED + "Error: Intrinsic gas too low. Try increasing the gas limit.")
        elif 'gas price too low' in str(e):
            print(Fore.RED + "Error: Gas price too low. Try increasing the gas price.")
        else:
            print(Fore.RED + "An unexpected error occurred. Please check the details and try again.")

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
        choice = input(Fore.CYAN + "Please choose an option or press 'M' to display menu: ")
        if choice == '1':
            set_max_gas_price()
        elif choice == '2':
            detect_with_access_list()
        elif choice == '3':
            gather_storage_keys()
        elif choice == '4':
            create_access_list()
        elif choice == '5':
            batches = int(input(Fore.CYAN + "Enter the number of batches to approve: "))
            approve_xen_tokens(PUBLIC_KEY, batches)
        elif choice == '6':
            batch_number = int(input(Fore.CYAN + "Enter the number of batches to burn: "))
            burn_with_access_list(PUBLIC_KEY, batch_number)
        elif choice == '7':
            tip_the_creator()
        elif choice == '8':
            break
        elif choice.lower() == 'm':
            print_title()
            print_menu()
        else:
            print(Fore.RED + "Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()
