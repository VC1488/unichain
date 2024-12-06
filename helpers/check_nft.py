import asyncio
import logging

from web3 import AsyncWeb3
from context_var import wallet_context
from config.erc721_abi import erc721
from config.config import NFT_RPC


logger = logging.getLogger(__name__)

CONTRACT_ADDRESS = '0x99F4146B950Ec5B8C6Bc1Aa6f6C9b14b6ADc6256'
CONTRACT_ABI = erc721


async def check_nft_balance(private_key: str):
    try:
        wallet_context.set(private_key)
        web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(NFT_RPC))
        account = web3.eth.account.from_key(private_key)
        account_address = web3.to_checksum_address(account.address)
        contract_address = web3.to_checksum_address(CONTRACT_ADDRESS)
        contract = web3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
        checksum_address = web3.to_checksum_address(account_address)
        balance = await contract.functions.balanceOf(checksum_address).call()
        logger.info(f"{balance} NFT.")


    except Exception as e:
        logger.error(f"Error checking nfts: {e}")


async def check_all_nft_balances():
    with open('data/private_keys.txt', 'r') as f:
        private_keys = [line.strip() for line in f if line.strip()]

    tasks = []
    for private_key in private_keys:
        tasks.append(asyncio.create_task(check_nft_balance(private_key)))

    await asyncio.gather(*tasks)
