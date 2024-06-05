DBXen Access List Creation Tool
Overview
The DBXen Access List Creation Tool is designed to help users burn XEN tokens more efficiently by leveraging access lists. This tool empowers everyone to burn XEN by creating access lists, making the process accessible and leveling the playing field in the XEN ecosystem.

Features
Approve XEN tokens for burning
Create access lists by burning a batch of XEN tokens
Burn multiple batches using saved access lists to reduce gas fees
Recalculate protocol fees dynamically based on the updated gas fees
User-friendly interface with color-coded outputs
Prerequisites
Python 3.x
web3 library
dotenv library
colorama library
Installation
Clone the repository:

sh
Copy code
git clone https://github.com/yourusername/DBXen-Access-List-Creation-Tool.git
cd DBXen-Access-List-Creation-Tool
Create and activate a virtual environment (optional but recommended):

sh
Copy code
python -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
Install the required Python libraries:

sh
Copy code
pip install web3 python-dotenv colorama
Create a .env file in the root directory of the project and add the following:

env
Copy code
PRIVATE_KEY=your_private_key
PUBLIC_KEY=your_public_key
RPC_URL=your_rpc_url
Usage
Run the script:

sh
Copy code
python dxn-al.py
Follow the on-screen instructions to:

Set the max gas price
Check if an access list exists
Approve XEN tokens
Burn 1 batch to create an access list
Burn batches using the access list
Tip the creator
Example
Upon running the script, you will see a menu with options to perform different actions. Here’s an example of what the menu looks like:

plaintext
Copy code
=========================================================
  DBXen Access List Creation Tool
  Created by TreeCityWes.eth for the Xen Ecosystem
  https://buymeacoffee.com/treecitywes
=========================================================
Public Key: <your_public_key>
Current Gas Price: <current_gas_price> gwei
Max Gas Price Setting: <max_gas_price> gwei
ETH Holdings: <eth_holdings> ETH
XEN Holdings: <xen_holdings> XEN
Batches Available to Burn: <batches_available>
=========================================================
This tool empowers everyone to burn XEN by leveraging access lists. 
By using this utility, you can easily create access lists and execute burns, 
making the process accessible to all and leveling the playing field in the XEN ecosystem.
=========================================================

1. Set Max Gas Price
2. Check if Access List Exists
3. Approve XEN Tokens
4. Burn 1 Batch to Create Access List
5. Burn Batches Using Access List
6. Tip The Creator
7. Exit

Please choose an option or press 'M' to display menu:
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License.

Acknowledgments
Created by TreeCityWes.eth for the XEN Ecosystem
Support the creator: Buy Me a Coffee
