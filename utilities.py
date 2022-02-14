from typing import List, Dict, Tuple
import base64
from algosdk import account, encoding

def wait_for_confirmation(client, transaction_id, timeout):
  start_round = client.status()["last-round"] + 1
  current_round = start_round

  while current_round < start_round + timeout:
    try:
      pending_txn = client.pending_transaction_info(transaction_id)
    except Exception:
      return
    if pending_txn.get("confirmed-round", 0) > 0:
      return pending_txn
    elif pending_txn["pool-error"]:
      raise Exception('pool error: {}'.format(pending_txn["pool-error"]))
    client.status_after_block(current_round)
    current_round += 1
  raise Exception('pending tx not ffound in timeout rounds, timout value = : {}'.format(timeout))

def compile_program(algod_client, source_code):
  compile_response = algod_client.compile(source_code)
  return base64.b64decode(compile_response['result'])

