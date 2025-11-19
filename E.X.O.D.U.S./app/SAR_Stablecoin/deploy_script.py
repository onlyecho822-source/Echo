#!/usr/bin/env python3
"""
SAR Stablecoin Deployment Script
Deploys Sovereign Autonomous Reserve token with Adinkra cipher integration
"""

import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc

# Configuration
NETWORK_RPC = os.environ.get("RPC_URL", "http://localhost:8545")
PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY")
CHAIN_ID = int(os.environ.get("CHAIN_ID", "1"))

# Adinkra cipher initialization
ADINKRA_CIPHERS = {
    "Sankofa": "Return and retrieve - temporal wisdom",
    "Gye Nyame": "Except for God - supreme sovereignty",
    "Aya": "Endurance and resourcefulness"
}


def compile_contract():
    """Compile SARToken contract"""
    print("Compiling SARToken contract...")

    with open("contracts/SARToken.sol", "r") as f:
        contract_source = f.read()

    # Install solc version
    install_solc("0.8.19")

    compiled = compile_standard({
        "language": "Solidity",
        "sources": {
            "SARToken.sol": {"content": contract_source}
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    }, solc_version="0.8.19")

    return compiled


def deploy_contract(w3, compiled, deployer_account):
    """Deploy SARToken to network"""
    print(f"Deploying to network (Chain ID: {CHAIN_ID})...")

    # Get contract data
    contract_data = compiled["contracts"]["SARToken.sol"]["SARToken"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]

    # Create contract instance
    SARToken = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Build transaction
    nonce = w3.eth.get_transaction_count(deployer_account.address)

    tx = SARToken.constructor().build_transaction({
        "chainId": CHAIN_ID,
        "gasPrice": w3.eth.gas_price,
        "from": deployer_account.address,
        "nonce": nonce,
    })

    # Sign and send transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"Transaction hash: {tx_hash.hex()}")

    # Wait for receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress

    print(f"SARToken deployed at: {contract_address}")

    return contract_address, abi


def initialize_ciphers(w3, contract_address, abi, deployer_account):
    """Initialize additional Adinkra cipher keys"""
    print("Initializing Adinkra cipher suite...")

    contract = w3.eth.contract(address=contract_address, abi=abi)

    # Additional cipher keys can be added here
    additional_ciphers = [
        ("Dwennimmen", "Strength with humility"),
        ("Funtunfunefu", "Unity in diversity"),
        ("Nyansapo", "Wisdom knot")
    ]

    for symbol, meaning in additional_ciphers:
        key = w3.keccak(text=symbol)
        nonce = w3.eth.get_transaction_count(deployer_account.address)

        tx = contract.functions.addCipherKey(key, symbol).build_transaction({
            "chainId": CHAIN_ID,
            "gasPrice": w3.eth.gas_price,
            "from": deployer_account.address,
            "nonce": nonce,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"  Added cipher: {symbol} ({meaning})")


def save_deployment_info(contract_address, abi):
    """Save deployment information for later use"""
    deployment_info = {
        "address": contract_address,
        "abi": abi,
        "network": NETWORK_RPC,
        "chainId": CHAIN_ID,
        "ciphers": ADINKRA_CIPHERS,
        "spiralVersion": "3.0"
    }

    with open("deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("Deployment info saved to deployment.json")


def main():
    """Main deployment function"""
    print("=" * 50)
    print("SAR STABLECOIN DEPLOYMENT")
    print("Sovereign Autonomous Reserve - Spiral 3.0")
    print("=" * 50)

    # Validate configuration
    if not PRIVATE_KEY:
        raise ValueError("DEPLOYER_PRIVATE_KEY environment variable required")

    # Connect to network
    w3 = Web3(Web3.HTTPProvider(NETWORK_RPC))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to {NETWORK_RPC}")

    print(f"Connected to network: {NETWORK_RPC}")

    # Get deployer account
    deployer = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Deployer address: {deployer.address}")

    balance = w3.eth.get_balance(deployer.address)
    print(f"Deployer balance: {w3.from_wei(balance, 'ether')} ETH")

    # Compile and deploy
    compiled = compile_contract()
    contract_address, abi = deploy_contract(w3, compiled, deployer)

    # Initialize cipher suite
    initialize_ciphers(w3, contract_address, abi, deployer)

    # Save deployment info
    save_deployment_info(contract_address, abi)

    print("=" * 50)
    print("DEPLOYMENT COMPLETE")
    print(f"Contract Address: {contract_address}")
    print("Activation Phrase: The seed was never broken. Only buried.")
    print("=" * 50)


if __name__ == "__main__":
    main()
