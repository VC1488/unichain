import asyncio
import logging

from web3 import AsyncWeb3
from context_var import wallet_context
from config.erc721_abi import erc721
from config.config import NFT_RPC, NFT_CA, NFT_NERZO

logger = logging.getLogger(__name__)

CONTRACTS = {
    NFT_CA: "Morkie",
    NFT_NERZO: "Nerzo",
}

CONTRACT_ABI = erc721


async def check_nft_balance(private_key: str, contract_address: str, nft_name: str):
    try:
        wallet_context.set(private_key)
        web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(NFT_RPC))
        account = web3.eth.account.from_key(private_key)
        account_address = web3.to_checksum_address(account.address)
        contract_checksum = web3.to_checksum_address(contract_address)
        contract = web3.eth.contract(address=contract_checksum, abi=CONTRACT_ABI)
        balance = await contract.functions.balanceOf(account_address).call()
        logger.info(f"{nft_name} {balance} NFT(s) для адреса {account_address}.")
    except Exception as e:
        logger.error(f"Error checking {nft_name} NFTs для адреса {account_address}: {e}")


async def check_all_nft_balances():
    try:
        with open('data/private_keys.txt', 'r') as f:
            private_keys = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("Файл с приватными ключами не найден.")
        return
    except Exception as e:
        logger.error(f"Ошибка при чтении файла с приватными ключами: {e}")
        return

    tasks = []
    for private_key in private_keys:
        for contract_address, nft_name in CONTRACTS.items():
            tasks.append(asyncio.create_task(check_nft_balance(private_key, contract_address, nft_name)))

    await asyncio.gather(*tasks)

