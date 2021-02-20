import subprocess
import json
from constants import *
import os 
from dotenv import load_dotenv 
from bit import wif_to_key, PrivateKeyTestnet
from web3 import Web3 , Account
from web3.middleware import geth_poa_middleware
from getpass import getpass
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI

load_dotenv()
menmonic = os.getenv('menmonic')


def derive_wallets(coin):
    command = f'./derive -g --mnemonic="{menmonic}" --coin={coin} --numderive=3 --cols=path,address,privkey,pubkey --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

coins = {ETH: derive_wallets(ETH), BTCTEST:derive_wallets(BTCTEST)}


def privKeyToAccount(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

#privKeyToAccount(ETH, coins[ETH][0]['privkey'])

def create_raw_tx(coin, account, recipient, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas({"from": account.address, "to": recipient, "value": amount})
        return {
                "from": account.address,
                "to": recipient,
                "value": amount,
                "gasPrice": w3.eth.gasPrice + 20 ,
                "gas": gasEstimate,
                "nonce": w3.eth.getTransactionCount(account.address),
            }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])


def send_tx(coin, account, recipient, amount):
    tx = create_raw_tx(coin, account, recipient, amount)
    signed_tx = account.sign_transaction(tx)
    if coin == ETH:
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

#send_tx(BTCTEST,privKeyToAccount(BTCTEST), coins[BTCTEST][1]['privkey']), "4C769876DFC5d89e52fa97687801608478532179", 0.0001)

 