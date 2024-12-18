import aiohttp
import logging

from web3 import AsyncWeb3, AsyncHTTPProvider
from config.config import NFT_RPC, NFT_NERZO
from context_var import wallet_context
from helpers.proxies_random import get_random_proxy

logger = logging.getLogger()

async def mint_nerzo_nft(private_key):
    wallet_context.set(private_key)
    proxy = get_random_proxy()
    web3 = AsyncWeb3(AsyncHTTPProvider(NFT_RPC, request_kwargs={"proxy": proxy, "timeout": aiohttp.ClientTimeout(total=180)}))

    account = web3.eth.account.from_key(private_key)
    account_address = web3.to_checksum_address(account.address)
    contract_address = NFT_NERZO

    data =  f"0x84bb1e42000000000000000000000000{account_address.lower()[2:]}0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000080ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

    nonce = await web3.eth.get_transaction_count(account_address)
    gas_price = await web3.eth.gas_price

    tx = {
        'to': web3.to_checksum_address('0xFDE3b685898576Bb263cFE585D9ca49Aa848fC65'),
        'value': 0,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': gas_price,
        'data': data,
        'chainId': 1301
    }

    signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)

    try:
        tx_hash = await web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f'Transaction sent with hash: {web3.to_hex(tx_hash)}')
        tx_receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f"Transaction confirmed. Block: {tx_receipt}")
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        raise
