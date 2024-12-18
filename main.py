import asyncio
import logging
import os
import sys
from datetime import datetime

from context_var import wallet_context
from colorlog import ColoredFormatter

from bridge_processor import bridge_processor_wallet
from helpers.check_balance import check_all_balances
from helpers.check_nft import check_all_nft_balances
from nft.nft_processor import processor_nft_mint
from randomize_swaps import swap_balances

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def setup_logger():
    logging.getLogger('asyncio').setLevel(logging.INFO)

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(log_dir, f'log_{start_time}.log')

    file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)-6s | %(wallet_context)s | %(message)s",
        datefmt='%m-%d %H:%M',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red'
        }
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.wallet_context = wallet_context.get()
        return record

    logging.setLogRecordFactory(record_factory)


async def main():


    choice = input("1. Bridge\n2. Mint NFTs\n3. Check Balance\n4. Check NFTs\n5. Random Swaps\n").strip()
    if choice == '1':
        await bridge_processor_wallet()
    elif choice == '2':
        await processor_nft_mint()
    elif choice == '3':
        await check_all_balances()
    elif choice == '4':
        await check_all_nft_balances()
    elif choice == '5':
        await swap_balances()
    else:
        return

if __name__ == '__main__':
    setup_logger()
    asyncio.run(main())
