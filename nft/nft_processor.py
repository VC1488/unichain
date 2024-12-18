import asyncio
import logging

from helpers.retry import retry_async
from nft.mint_nerzo_nft import mint_nerzo_nft
from nft.mint_morkie_nft import mint_nft
from context_var import wallet_context


logger = logging.getLogger(__name__)

async def process_wallet(private_key, semaphore):
    wallet_context.set(private_key)
    async with semaphore:
        try:
            await retry_async(mint_nft, private_key)
            await retry_async(mint_nerzo_nft, private_key)
        except Exception as e:
            logger.error(f"Error processing wallet {private_key}: {e}")


async def processor_nft_mint():
    with open('data/private_keys.txt', 'r') as f:
        private_keys = [line.strip() for line in f if line.strip()]

    semaphore = asyncio.Semaphore(5)
    tasks = []

    for idx, private_key in enumerate(private_keys):
        task = asyncio.create_task(process_wallet(private_key, semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)
    logger.info("All nfts minted.")
