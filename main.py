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
"""
# config for sandbox
algod_server = "http://localhost"
algod_port = "4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_auth_header = "X-Algo-API-Token"

headers = {
    algod_auth_header: algod_token
}

algod_endpoint = algod_server

if (algod_port != ""):
    algod_endpoint = "{algod_server}:{algod_port}".format(algod_server=algod_server, algod_port=str(algod_port))

algod_client = algod.AlgodClient(
    algod_token,
    algod_endpoint,
    headers=headers
)
"""

algod_address = "https://testnet.algoexplorerapi.io"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

ORACLE_INDEX_ID = 70820731
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
        # pass in index appId, oracle appId and desired price pair key
        approval_program_teal = approval_program(ORACLE_INDEX_ID, ALGO_ORACLE_APP_ID, "algo/usd")
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
      ORACLE_INDEX_ID,
      ALGO_ORACLE_APP_ID
    )

created_app_id = setup_create_app()
setup_call_app(created_app_id)
delete_app(algod_client, os.environ.get('secret_key'),  created_app_id)