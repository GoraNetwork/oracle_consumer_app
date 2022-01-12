from algosdk.v2client import algod
from algosdk import account, encoding, mnemonic
from algosdk.future import transaction
from operations import create_app, call_app, delete_app
from utilities import compile_program
from assets.consumer_approval import approval_program
from assets.consumer_clear import clear_state_program
from dotenv import load_dotenv
import os
load_dotenv()


algod_address = "https://testnet.algoexplorerapi.io"
algod_token = ""
headers={'User-Agent': 'DoYouLoveMe?'}
algod_client = algod.AlgodClient(algod_token, algod_address, headers)
ALGO_ORACLE_APP_ID = 53083112


def setup_create_app():

    #declare application storage
    local_ints = 4
    global_ints = 4
    local_bytes = 4
    global_bytes = 4

    #define schema 
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    with open("./approval.teal", "w") as f:
        approval_program_teal = approval_program(ALGO_ORACLE_APP_ID)
        f.write(approval_program_teal)

    with open("./clear.teal", "w") as f:
        clear_state_program_teal = clear_state_program()
        f.write(clear_state_program_teal)
    
    approval_program_compiled = compile_program(algod_client, approval_program_teal)
    clear_state_program_compiled = compile_program(algod_client, clear_state_program_teal)


    #deploy application
    app_id = create_app(
        algod_client,
        os.environ.get('creator_address'),
        os.environ.get('secret_key'),
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema
    )
    return app_id

def setup_call_app(app_id):
    call_app(
      algod_client,
      app_id,
      os.environ.get('sender_secret_key'),
    )

created_app_id = setup_create_app()
setup_call_app(created_app_id)
delete_app(algod_client, os.environ.get('secret_key'),  created_app_id)