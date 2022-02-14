from pyteal import *
from .helpers.use_oracle import *

def approval_program(ORACLE_INDEX, ALGO_PRICE_ORACLE, ALGO_PRICE_KEY):

    # validate the oracle appId matches the one stored in the index contract
    index_oracle_id = App.globalGetEx(Int(ORACLE_INDEX), Bytes(ALGO_PRICE_KEY))
    validate_oracle_id = Assert(
        And(Seq([
            index_oracle_id,
            index_oracle_id.value() == Int(ALGO_PRICE_ORACLE)
        ]))
    )

    # second argument required, specify what subset of data you want to receive
    (algo_price_data, get_algo_price_data) = use_oracle(ALGO_PRICE_ORACLE, {
        'price': TealType.uint64,
        'decimals': TealType.uint64
    })

    handle_noop = Seq([
        validate_oracle_id,
        get_algo_price_data,
        App.globalPut(Bytes("algo/usd"), algo_price_data['price'].load()),
        App.globalPut(Bytes("decimals"), algo_price_data['decimals'].load()),
        Approve()
    ])

    handle_optin = Seq([
        Reject()
    ])

    handle_closeout = Seq([
        Reject()
    ])

    handle_updateapp = Err()

    handle_deleteapp = Approve()

    handle_creation = Seq([
        Approve()
    ])

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp]
    )
    return compileTeal(program, Mode.Application, version=5)
