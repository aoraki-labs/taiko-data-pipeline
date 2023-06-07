import json
import typing
import pickle
from typing import Iterable, Sequence
from eth_typing import Address, BlockNumber
from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware
from web3.types import TxData, TxReceipt, EventData
from hexbytes import HexBytes

from .schema import (
    L2Block,
    L2ContractInfo,
    L2Transaction,
    BridgeL2CallProcessMessage,
    BridgeL2CallSendMessage,
    TokenVaultL2EventERC20Received,
    TokenVaultL2EventERC20Sent,
    ERC20Info,
    mysql_db
)

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import requests

# scan one block and save to db
class BlockScanner():
    def __init__(self):
        self.l2_rpc_endpoint = "https://rpc.test.taiko.xyz"
        self.chain_id = 11155111
        self.w3 = Web3(Web3.HTTPProvider(self.l2_rpc_endpoint))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        # self.taiko_l2_address = "0x0B306BF915C4d645ff596e518fAf3F9669b97016"
        self.taiko_l2_bridge = "0x1000777700000000000000000000000000000004"
        self.taiko_l2_token_vault = "0x1000777700000000000000000000000000000002"
        
        # raw data
        self.block_id: int
        self.tx_list: list[TxData]
        self.receipt_list: list[TxReceipt]

        # db data cache
        self.db_l2_block: dict
        self.db_l2_transaction_list: list[dict]
        self.db_bridge_l2_call_process_message: list[dict]
        self.db_bridge_l2_call_send_message: list[dict]
        self.db_token_vault_l2_event_erc20_sent: list[dict]
        self.db_token_vault_l2_event_erc20_received: list[dict]
        self.db_erc20_info: list[dict]
        self.db_contract_info: list[dict]

        self._init_contract()

    def _init_contract(self):

        l2_taiko_l2_bridge_abi = []
        taiko_l2_bridge_address = self.taiko_l2_bridge[2:]
        taiko_l2_bridge_address = bytes.fromhex(taiko_l2_bridge_address)
        taiko_l2_bridge_address = Address(taiko_l2_bridge_address)
        with open(Path(__file__).parent / "taiko_l2_bridge_abi.json") as f:
            l2_taiko_l2_bridge_abi = json.load(f)
        self.taiko_l2_bridge_contract = self.w3.eth.contract(taiko_l2_bridge_address, abi=l2_taiko_l2_bridge_abi)

        l2_taiko_l2_token_vault_abi = []
        taiko_l2_token_vault_address = self.taiko_l2_token_vault[2:]
        taiko_l2_token_vault_address = bytes.fromhex(taiko_l2_token_vault_address)
        taiko_l2_token_vault_address = Address(taiko_l2_token_vault_address)
        with open(Path(__file__).parent / "taiko_l2_token_vault_abi.json") as f:
            l2_taiko_l2_token_vault_abi = json.load(f)
        self.taiko_l2_token_vault_contract = self.w3.eth.contract(taiko_l2_token_vault_address, abi=l2_taiko_l2_token_vault_abi)


    def set_block_id(self, block_id: int):
        self.block_id = block_id
    
    def fetch_data(self):
        # check: 
        # 1. records in block exists
        # 2. pickles exist
        # 3. num is consistent
        # if all true, ok
        # if not, do the original

        # for update of each table, do not delete, just check if num consistent

        tx_num = L2Block.select(L2Block.txs_num).where(L2Block.block_id == self.block_id).scalar()
        tx_binary = Path(Path(__file__).parent / f"../tx_binaries/l2/{self.block_id}")
        if tx_num and tx_binary.is_file():
            l2_block = L2Block.get(L2Block.block_id == self.block_id)
            self.db_l2_block = {
                "block_id": l2_block.block_id,
                "block_hash": l2_block.block_hash,
                "timestamp": l2_block.timestamp,
                "base_fee_per_gas": l2_block.base_fee_per_gas,
                "gas_used": l2_block.gas_used,
                "txs_num": l2_block.txs_num,
            }
            with open(Path(__file__).parent / f"../tx_binaries/l2/{self.block_id}", 'rb') as f:
                (self.tx_list, self.receipt_list) = pickle.load(f)
            if tx_num == len(self.tx_list) and tx_num == len(self.receipt_list):
                return
        
        block = self.w3.eth.get_block(self.block_id, full_transactions=True)
        txs = block.get("transactions")
        txs = typing.cast(Sequence[TxData], txs)
        
        self.tx_list = list(txs)
        self.receipt_list = []
        for tx in self.tx_list:
            hash = tx.get("hash")
            hash = typing.cast(HexBytes, hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(hash)
            self.receipt_list.append(tx_receipt)
        
        with open(Path(__file__).parent / f"../tx_binaries/l2/{self.block_id}", 'wb') as f:
            pickle.dump((self.tx_list, self.receipt_list), f)

        self.db_l2_block = {
            "block_id": block.get("number"),
            "block_hash": block.get("hash").hex(),
            "parent_hash": block.get("parentHash").hex(),
            "timestamp": block.get("timestamp"),
            "base_fee_per_gas": block.get("baseFeePerGas"),
            "gas_used": block.get("gasUsed"),
            "txs_num": len(self.tx_list),
        }
    
    def save_block(self):
        count = L2Block.select().where(L2Block.block_id == self.block_id).count()
        if count == 0:
            L2Block.create(**self.db_l2_block)
        elif count != 1:
            L2Block.delete().where(L2Block.block_id == self.block_id).execute()
            L2Block.create(**self.db_l2_block)

    def parse_txs(self):
        self.db_l2_transaction_list = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            self.db_l2_transaction_list.append({
                "block_id": tx.get("blockNumber"),
                "tx_hash": tx.get("hash").hex(),
                "tx_from": tx.get("from"),
                "tx_to": tx.get("to"),
                "input": tx.get("input"),
                "value": tx.get("value"),
                "gas_used": receipt.get("gasUsed"),
                "gas_price": receipt.get("effectiveGasPrice"),
                "nonce": tx.get("nonce"),
                "status": receipt.get("status"),
                "transaction_index": receipt.get("transactionIndex"),
                "timestamp": self.db_l2_block.get("timestamp"),
                "contract_address": receipt.get("contractAddress"),
                # "tx_dump": pickle.dumps(tx),
                # "receipt_dump": pickle.dumps(receipt),
            })

    def save_txs(self):
        count = L2Transaction.select().where(L2Transaction.block_id == self.block_id).count()
        if count != len(self.tx_list):
            L2Transaction.delete().where(L2Transaction.block_id == self.block_id).execute()
            L2Transaction.insert_many(self.db_l2_transaction_list).execute()

    def parse_bridge_l2_call_process_message(self):
        self.db_bridge_l2_call_process_message = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l2_bridge_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "processMessage":
                    self.db_bridge_l2_call_process_message.append({
                        "block_id": tx.get("blockNumber"),
                        "tx_hash": tx.get("hash").hex(),
                        "message_id": data["message"]["id"],
                        "message_sender": data["message"]["sender"],
                        "message_src_chain_id": data["message"]["srcChainId"],
                        "message_dest_chain_id": data["message"]["destChainId"],
                        "message_owner": data["message"]["owner"],
                        "message_to": data["message"]["to"],
                        "message_refund_address": data["message"]["refundAddress"],
                        "message_deposit_value": data["message"]["depositValue"],
                        "message_call_value": data["message"]["callValue"],
                        "message_processing_fee": data["message"]["processingFee"],
                        "message_gas_limit": data["message"]["gasLimit"],
                        "message_data": self.w3.to_hex(data["message"]["data"]),
                        "message_memo": data["message"]["memo"],
                        "status": receipt.get("status"),
                    })
            except Exception:
                continue

    def save_bridge_l2_call_process_message(self):
        count = BridgeL2CallProcessMessage.select().where(BridgeL2CallProcessMessage.block_id == self.block_id).count()
        if count != len(self.db_bridge_l2_call_process_message):
            BridgeL2CallProcessMessage.delete().where(BridgeL2CallProcessMessage.block_id == self.block_id).execute()
            BridgeL2CallProcessMessage.insert_many(self.db_bridge_l2_call_process_message).execute()

    def parse_bridge_l2_call_send_message(self):
        self.db_bridge_l2_call_send_message = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l2_bridge_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "sendMessage":
                    self.db_bridge_l2_call_send_message.append({
                        "block_id": tx.get("blockNumber"),
                        "tx_hash": tx.get("hash").hex(),
                        "message_id": data["message"]["id"],
                        "message_sender": data["message"]["sender"],
                        "message_src_chain_id": data["message"]["srcChainId"],
                        "message_dest_chain_id": data["message"]["destChainId"],
                        "message_owner": data["message"]["owner"],
                        "message_to": data["message"]["to"],
                        "message_refund_address": data["message"]["refundAddress"],
                        "message_deposit_value": data["message"]["depositValue"],
                        "message_call_value": data["message"]["callValue"],
                        "message_processing_fee": data["message"]["processingFee"],
                        "message_gas_limit": data["message"]["gasLimit"],
                        "message_data": self.w3.to_hex(data["message"]["data"]),
                        "message_memo": data["message"]["memo"],
                        "status": receipt.get("status"),
                    })
            except Exception:
                continue

    def save_bridge_l2_call_send_message(self):
        count = BridgeL2CallSendMessage.select().where(BridgeL2CallSendMessage.block_id == self.block_id).count()
        if count != len(self.db_bridge_l2_call_send_message):
            BridgeL2CallSendMessage.delete().where(BridgeL2CallSendMessage.block_id == self.block_id).execute()
            BridgeL2CallSendMessage.insert_many(self.db_bridge_l2_call_send_message).execute()

    def parse_token_vault_l2_event_erc20_sent(self):
        self.db_token_vault_l2_event_erc20_sent = []
        for receipt in self.receipt_list:
            # tx_to = receipt.get("to")
            # if tx_to != self.taiko_l2_bridge:  # todo: check if its complete
            #     continue
            events: Iterable[EventData] = self.taiko_l2_token_vault_contract.events.ERC20Sent().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_token_vault:
                    continue
                self.db_token_vault_l2_event_erc20_sent.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                    "tx_from": event.get("args").get("from"),
                    "tx_to": event.get("args").get("to"),
                    "dest_chain_id": event.get("args").get("destChainId"),
                    "token": event.get("args").get("token"),
                    "amount": event.get("args").get("amount"),
                })

    def save_token_vault_l2_event_erc20_sent(self):
        count = TokenVaultL2EventERC20Sent.select().where(TokenVaultL2EventERC20Sent.block_id == self.block_id).count()
        if count != len(self.db_token_vault_l2_event_erc20_sent):
            TokenVaultL2EventERC20Sent.delete().where(TokenVaultL2EventERC20Sent.block_id == self.block_id).execute()
            TokenVaultL2EventERC20Sent.insert_many(self.db_token_vault_l2_event_erc20_sent).execute()


    def parse_token_vault_l2_event_erc20_received(self):
        self.db_token_vault_l2_event_erc20_received = []
        for receipt in self.receipt_list:
            # tx_to = receipt.get("to")
            # if tx_to != self.taiko_l2_bridge:  # todo: check if its complete
            #     continue
            events: Iterable[EventData] = self.taiko_l2_token_vault_contract.events.ERC20Received().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_token_vault:
                    continue
                self.db_token_vault_l2_event_erc20_received.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                    "tx_from": event.get("args").get("from"),
                    "tx_to": event.get("args").get("to"),
                    "src_chain_id": event.get("args").get("srcChainId"),
                    "token": event.get("args").get("token"),
                    "amount": event.get("args").get("amount"),
                })

    def save_token_vault_l2_event_erc20_received(self):
        count = TokenVaultL2EventERC20Received.select().where(TokenVaultL2EventERC20Received.block_id == self.block_id).count()
        if count != len(self.db_token_vault_l2_event_erc20_received):
            TokenVaultL2EventERC20Received.delete().where(TokenVaultL2EventERC20Received.block_id == self.block_id).execute()
            TokenVaultL2EventERC20Received.insert_many(self.db_token_vault_l2_event_erc20_received).execute()

    def get_all_tokens_info(self):
        self.db_erc20_info = []
        result = mysql_db.execute_sql("""
            with token_raw as (
                select token from token_vault_l2_event_erc20_received
                union
                select token from token_vault_l2_event_erc20_sent
            )

            select tr.token
            from erc20_info ei
            right join token_raw tr on tr.token = ei.address and ei.chain_id = {0}
            where ei.address is null
        """.format(self.chain_id)).fetchall()
        print(result)

        if not result:
            return

        erc20_abi = []
        with open(Path(__file__).parent / "erc20_abi.json") as f:
            erc20_abi = json.load(f)
        
        for tup in result:
            address = self.w3.to_checksum_address(tup[0])
            erc20_contract = self.w3.eth.contract(address=address, abi=erc20_abi)
            self.db_erc20_info.append({
                "chain_id": self.chain_id,
                "address": address,
                "name": erc20_contract.functions.name().call(),
                "symbol": erc20_contract.functions.symbol().call(),
                "decimal": erc20_contract.functions.decimals().call()
            })
    
    def save_all_tokens_info(self):
        if self.db_erc20_info:
            ERC20Info.insert_many(self.db_erc20_info).execute()
    

# try parse block
# print parse result
# write code to save db(delete first)

# how to get failed call names
# check receipt and tx hash consistent
# write another method, run from the starting block to check if there's errors

# store log data
# parse input of call

# block_scanner = BlockScanner()
# block_scanner.init_contract()
# block_scanner.set_block_id(3150938)
# block_scanner.fetch_data()
# block_scanner.parse_block()
# block_scanner.parse_txs()
# block_scanner.parse_l1_call_propose_block()
# block_scanner.parse_l1_call_prove_block()
# block_scanner.parse_l1_event_block_committed()
# block_scanner.parse_l1_event_block_proposed()
# block_scanner.parse_l1_event_block_proven()
# block_scanner.parse_l1_event_block_verified()
# block_scanner.parse_l1_event_header_synced()
# block_scanner.get_reward_balance()
# block_scanner.save_l1_call_propose_block()
# block_scanner.save_l1_call_prove_block()
# block_scanner.save_l1_event_header_synced()
# block_scanner.save_l1_event_block_verified()
# block_scanner.save_l1_event_block_proven()
# block_scanner.save_l1_event_block_proposed()
# block_scanner.save_l1_event_block_committed()
# block_scanner.save_reward_balance()
# block_scanner.save_txs()
# block_scanner.save_block()
# print(block_scanner.db_l1_block)
# print("======================= db_l1_transaction_list")
# if block_scanner.db_l1_transaction_list:
#     print(block_scanner.db_l1_transaction_list)
# print("======================= db_l1_event_block_committed")
# if block_scanner.db_l1_event_block_committed:
#     print(block_scanner.db_l1_event_block_committed[0])
# print("======================= db_l1_event_block_proposed")
# if block_scanner.db_l1_event_block_proposed:
#     print(block_scanner.db_l1_event_block_proposed[0])
# print("======================= db_l1_event_block_proven")
# if block_scanner.db_l1_event_block_proven:
#     print(len(block_scanner.db_l1_event_block_proven))
#     print(block_scanner.db_l1_event_block_proven[0])
# print("======================= db_l1_event_block_verified")
# if block_scanner.db_l1_event_block_verified:
#     print(block_scanner.db_l1_event_block_verified[0])
# print("======================= db_l1_event_header_synced")
# if block_scanner.db_l1_event_header_synced:
#     print(block_scanner.db_l1_event_header_synced[0])
# print("=======================")