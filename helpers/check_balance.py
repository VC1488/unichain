import asyncio
import logging

from web3 import AsyncWeb3
from eth_account import Account
from context_var import wallet_context
from config.config import networks

logger = logging.getLogger(__name__)

async def check_balance(private_key: str, network_name: str, network_rpc: str):
    wallet_context.set(private_key)
    web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(network_rpc))
    account = Account.from_key(private_key)
    balance_wei = await web3.eth.get_balance(account.address)
    balance_eth = web3.from_wei(balance_wei, 'ether')
    logger.info(f"Chain: {network_name}, Balance: {balance_eth} ETH")

async def check_all_balances():
    with open('data/private_keys.txt', 'r') as f:
        private_keys = [line.strip() for line in f if line.strip()]

    tasks = []
    for pk in private_keys:
        for name, net_data in networks.items():
            tasks.append(asyncio.create_task(check_balance(pk, name, net_data['rpc'])))

    await asyncio.gather(*tasks)
