import datetime
from config import wif, adrs
import pydantic_modules
import bit
from db import *


@db_session
def create_wallet(user: pydantic_modules.User = None, private_key: str = None, testnet: bool = False):
    if not testnet:  # проверка не тестовый ли мы делаем кошелёе
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
    flush()  # сохраняем объект в бд, чтобы получить его id
    return user


@db_session
def create_transaction(
        sender: User,
        amount_btc_without_fee: float,
        receiver_address: str,
        fee: float | None = None,
        testnet: bool = False
):
    """
    :param amount_btc_without_fee: количество биткоинов исключая комиссию, значение в сатоши
    :param receiver_address: адрес получателя, строка с адресом
    :param amount_btc_with_fee: количество биткоинов включая комиссию, значение в сатоши
    :param fee: абсолютная комиссия, исчисляем в сатоши - необязательно.
    :param testnet: в тестовой ли сети мы работаем
    :return: Transaction object
    """
    # загружаем в переменную wallet_of_sender кошелёк отправителя
    # если в тестовой сети, загружаем тестовый кошелёк
    wallet_of_sender = bit.Key(sender.wallet.private_key) if not testnet else bit.PrivateKeyTestnet(
        sender.wallet.private_key)
    sender.wallet.balance = wallet_of_sender.get_balance()  # получаем баланс кошелька
    if not fee:
        fee = bit.network.fees.get_fee() * 1000  # получаем стоимость транзакции sat/B и умножаем на 1000
    amount_btc_with_fee = amount_btc_without_fee + fee
    if amount_btc_without_fee + fee > sender.wallet.balance:
        return f'Too low balance: {sender.wallet.balance}'

    # подготовка кортежа перед транзакцией
    output = [(receiver_address, amount_btc_without_fee, 'satoshi')]

    # отправляем транзакцию и получаем её хеш
    tx_hash = wallet_of_sender.send(output, fee, absolute_fee=True)

    # создаем объект транзакции и сохраняем его в БД
    transaction = Transaction(sender=sender,
                              sender_wallet=sender.wallet,
                              fee=fee,
                              sender_address=sender.wallet.address,
                              receiver_address=receiver_address,
                              amount_btc_with_fee=amount_btc_with_fee,
                              amount_btc_without_fee=amount_btc_without_fee,
                              date_of_transaction=datetime.now(),
                              tx_hash=tx_hash)


@db_session
def update_wallet_balance(wallet: pydantic_modules.Wallet):
    # проверяем тестовая сеть или нет
    testnet = True if wallet.private_key.startswith('c') else False
    # получаем объект из Bit для работы с биткоинами
    bit_wallet = bit.Key(wallet.private_key) if not testnet else bit.PrivateKeyTestnet(wallet.private_key)
    wallet.balance = bit_wallet.get_balance()
    return wallet

@db_session
def update_all_wallets():
    # используя генераторное выражение выбираю все кошельки
    for wallet in Wallet.select()[:]:
        #обновление баланса
        update_wallet_balance(wallet)
        #проверяем всё ли получилось
        print(wallet.address, wallet.balance)
    return True

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
