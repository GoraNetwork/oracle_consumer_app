from algosdk import account, encoding, mnemonic
from algosdk.future import transaction
from utilities import wait_for_confirmation
from algosdk.logic import get_application_address
from dotenv import load_dotenv
import os
load_dotenv()

def create_app(
    algod_client,
    creator_address,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema ):
    #creator default address
    #declare on_complete as no_op
    on_complete = transaction.OnComplete.NoOpOC.real
    #build transaction
    params = algod_client.suggested_params()
    
    #create unsigned Application Create Txn
    unsigned_txn = transaction.ApplicationCreateTxn(
        creator_address,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema
    )
    #sign txn
    signed_txn = unsigned_txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    #submit transaction
    algod_client.send_transaction(signed_txn)

    #wait for confirmation
    pmtx = wait_for_confirmation(algod_client, tx_id, 5)
    #display results
    transaction_response = algod_client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("created new appid : {}".format(app_id))
    return app_id

def call_app(
    algod_client,
    app_id,
    sender_private_key,
    index_app_id,
    oracle_app_id
    ):
    #build transaction
    params = algod_client.suggested_params()
    sender = account.address_from_private_key(sender_private_key)
    app_address = get_application_address(app_id)

    update_price_call = transaction.ApplicationCallTxn(
        sender = sender,
        sp = params,
        index = app_id,
        on_complete = transaction.OnComplete.NoOpOC,
        foreign_apps=[index_app_id, oracle_app_id]
    )
    update_price_call_signed_txn = update_price_call.sign(sender_private_key)
    update_price_call_signed_txn_id = update_price_call_signed_txn.get_txid()
    tx_id = algod_client.send_transaction( update_price_call_signed_txn)
    tx = wait_for_confirmation(algod_client, tx_id, 5)
    print('price has been updated to global state. Here is your transaction ID: ', tx_id)
    return tx_id

# delete application
def delete_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client,  tx_id, 5)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Thank your for using the price oracle. Your app has now been deleted. Deleted app-id:", transaction_response["txn"]["txn"]["apid"])

