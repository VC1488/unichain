import asyncio
import logging

from context_var import wallet_context
from helpers.retry import retry_async
from modules.bridgg import brid_gg
from modules.super_bridge import super_bridge
from config.config import networks, amount

logger = logging.getLogger(__name__)


async def process_wallet(private_key, semaphore, bridge_func, from_network_key):
    wallet_context.set(private_key)
    async with semaphore:
        try:
            await retry_async(
                bridge_func,
                private_key,
                rpc=networks[from_network_key]['rpc'],
                contract_address=networks[from_network_key]['contract'],
                amount=amount,
            )
        except Exception as e:
            logger.error(f"Error processing wallet {private_key}: {e}")


async def bridge_processor_wallet():
    choice = input("1. Superbridge transfer\n2. BridGG transfer\n")

    if choice == "1":
        bridge_func = super_bridge
    elif choice == "2":
        bridge_func = brid_gg
    else:
        return

    network_map = {
        "1": "sepolia",
        "2": "unichain_sepolia",
        "3": "base_sepolia",
        "4": "op_sepolia"
    }

    choose_from_network = input(
        'Sender network:\n1. Sepolia\n2. Unichain\n3. BaseSepolia\n4. OptimismSepolia\n')

    if choose_from_network not in network_map:
        return

    from_network_key = network_map[choose_from_network]

    if from_network_key == "sepolia":
        to_network_options = network_map.copy()
    else:
        to_network_options = {"1": "sepolia"}

    for key, value in to_network_options.items():
        if value == "sepolia":
            display_name = "Sepolia"
        elif value == "unichain_sepolia":
            display_name = "Unichain Sepolia"
        elif value == "base_sepolia":
            display_name = "Base Sepolia"
        elif value == "op_sepolia":
            display_name = "Optimism Sepolia"
        else:
            display_name = value
        print(f"{key}. {display_name}")

    choose_to_network = input()

    if choose_to_network not in to_network_options:
        return

    try:
        with open('data/private_keys.txt', 'r') as f:
            private_keys = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("Файл 'data/private_keys.txt' не найден.")
        return

    semaphore = asyncio.Semaphore(5)
    tasks = []

    for private_key in private_keys:
        task = asyncio.create_task(
            process_wallet(private_key, semaphore, bridge_func, from_network_key))
        tasks.append(task)

    await asyncio.gather(*tasks)

    logger.info("All swaps completed.")

