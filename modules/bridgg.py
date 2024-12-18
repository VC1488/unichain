import logging
import aiohttp

from web3 import AsyncWeb3, AsyncHTTPProvider
from config.abi import abi
from helpers.proxies_random import get_random_proxy
from context_var import wallet_context


logger = logging.getLogger(__name__)

async def brid_gg(private_key, rpc, contract_address, amount):
    wallet_context.set(private_key)
    proxy = get_random_proxy()
    web3 = AsyncWeb3(AsyncHTTPProvider(rpc, request_kwargs={"proxy": proxy, "timeout": aiohttp.ClientTimeout(total=180)}))
    contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=abi)

    account = web3.eth.account.from_key(private_key)
    account_address = web3.to_checksum_address(account.address)

    to = account_address
    min_gas_limit = 50000
    extra_data = b'bridgg\n'
    value = web3.to_wei(amount, 'ether')

    nonce = await web3.eth.get_transaction_count(account_address, 'latest')
    gas_price = await web3.eth.gas_price

    txn = await (contract.functions.bridgeETHTo(to, min_gas_limit, extra_data)
                 .build_transaction({
                     'from': account_address,
                     'value': value,
                     'nonce': nonce,
                     'gas': 500000,
                     'gasPrice': gas_price,
                     'chainId': await web3.eth.chain_id,
                 }))

    signed_tx = web3.eth.account.sign_transaction(txn, private_key=private_key)

    try:
        tx_hash = await web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f'Transaction sent with hash: {web3.to_hex(tx_hash)}')
        tx_receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f"Transaction confirmed. Block: {tx_receipt}")
    except Exception as e:
        if 'insufficient funds' in str(e):
            logger.warning(f"insufficient funds for transfer")
        else:
            logger.error(f"Error occurred: {e}")
        raise
