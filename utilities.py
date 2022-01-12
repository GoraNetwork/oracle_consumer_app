from typing import List, Dict, Tuple
from pyteal import *
import base64
from algosdk import account, encoding

def use_oracle(oracle_id: int, data_fields: Dict[str, TealType]) -> Tuple[Dict[str, ScratchVar], Expr]:
    data = {}
    for data_field in data_fields:
        data[data_field] = ScratchVar(data_fields[data_field])

    get_data_seq = []
    for key in data_fields:
        oracle_value_state = App.globalGetEx(Int(oracle_id), Bytes(key))
        get_data_seq.append(Seq([
            oracle_value_state,
            data[key].store(oracle_value_state.value())
        ]))
    get_data = Seq(get_data_seq)

    return (data, get_data)

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

