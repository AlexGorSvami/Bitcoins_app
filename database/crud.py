import datetime
from config import wif, adrs
import pydantic_modules
import bit
from db import *

@db_session
def create_wallet(user: pydantic_modules.User = None, private_key: str = None, testnet: bool = False):
    if not testnet: # проверка не тестовый ли мы делаем кошелёе
        raw_wallet = bit.Key() if not private_key else bit.Key(private_key)
    else:
        raw_wallet = bit.PrivateKeyTestnet() if not private_key else bit.PrivateKeyTestnet(private_key)
    if user:
        wallet = Wallet(user=user, private_key=raw_wallet.to_wif(), address=raw_wallet.addres)
    else:
        wallet = Wallet(private_key=raw_wallet.to_wif(), address=raw_wallet.address)
    flush()
    return wallet

@db_session
def create_user(tg_id: int, nick: str = None):
    if nick:
        user = User(tg_ID=tg_id, nick=nick, create_date=datetime.now(), wallet=create_wallet())
    else:
        user = User(tg_ID=tg_id, create_date=datetime.now(), wallet=create_wallet())
    flush()
    return user
















# wallet = bit.Key()
# wallet = bit.PrivateKeyTestnet(wif)
# print(f'Balance: {wallet.get_balance()}')
# print(f'Address: {wallet.address}')
# print(f'Private key: {wallet.to_wif()}')
# print(f'All transactions: {wallet.get_transactions()}')
#
# output = [('muh9DYMTWXfPEd9zPnfvCS1yX8hPLbkE9e', 2, 'btc')]
# transaction = wallet.send(output)
# print(transaction)
