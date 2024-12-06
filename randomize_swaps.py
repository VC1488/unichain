import asyncio
import logging
import random

from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_account import Account
from context_var import wallet_context
from config.config import networks
from modules.super_bridge import super_bridge
from modules.bridgg import brid_gg
from helpers.retry import retry_async
from config.config import amount

logger = logging.getLogger(__name__)


async def check_balance(private_key: str):
    wallet_context.set(private_key)
    balances = {}
    account = Account.from_key(private_key).address

    tasks = []
    for network_name, net_data in networks.items():
        web3 = AsyncWeb3(AsyncHTTPProvider(net_data['rpc']))
        task = asyncio.create_task(get_balance(private_key, web3, account, network_name))
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, dict):
            balances.update(result)

    return balances


async def get_balance(private_key, web3, address, network_name):
    wallet_context.set(private_key)
    try:
        balance_wei = await web3.eth.get_balance(address)
        balance_eth = web3.from_wei(balance_wei, 'ether')
        return {network_name: balance_eth}
    except Exception as e:
        logger.error(f"Error getting balance for {network_name}: {e}")
        return {}


async def swap_balances():
    try:
        with open('data/private_keys.txt', 'r') as f:
            private_keys = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("Файл 'data/private_keys.txt' не найден.")
        return

    semaphore = asyncio.Semaphore(5)
    tasks = []

    for pk in private_keys:
        task = asyncio.create_task(handle_wallet_swap(pk, semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)

    logger.info("All swaps completed")


async def handle_wallet_swap(private_key, semaphore):
    wallet_context.set(private_key)
    async with semaphore:
        try:
            balances = await check_balance(private_key)
            available_networks = [net for net, bal in balances.items() if bal > 0.0001]

            if not available_networks:
                logger.info(f"No available networks with balance for wallet {private_key}")
                return

            from_network = random.choice(available_networks)
            from_balance = balances[from_network]

            if from_network == "sepolia":
                to_network_options = list(networks.keys())
            else:
                to_network_options = ["sepolia"]

            to_network_options = [net for net in to_network_options if net != from_network]

            if not to_network_options:
                logger.info(f"No valid target networks for from_network {from_network} for wallet {private_key}")
                return

            to_network = random.choice(to_network_options)
            logger.info(f"Bridge: {amount} ETH from {from_network} to {to_network}")

            await retry_async(
                super_bridge,
                private_key,
                rpc=networks[from_network]['rpc'],
                contract_address=networks[from_network]['contract'],
                amount=amount,
            )

            logger.info(f"Bridge from {from_network} to {to_network} was successful.")

            await asyncio.sleep(10)

            await retry_async(
                brid_gg,
                private_key,
                rpc=networks[to_network]['rpc'],
                contract_address=networks[to_network]['contract'],
                amount=amount,
            )

            logger.info(f"Reverse bridge from {to_network} to {from_network} was successful.")

        except Exception as e:
            logger.error(f"Error during random swaps for wallet {private_key}: {e}")
