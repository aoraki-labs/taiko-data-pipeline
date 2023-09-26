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
    ERC1155VaultL2EventBridgedTokenDeployed,
    ERC1155VaultL2EventTokenReceived,
    ERC1155VaultL2EventTokenReleased,
    ERC1155VaultL2EventTokenSent,
    ERC20VaultL2EventBridgedTokenDeployed,
    ERC20VaultL2EventTokenReceived,
    ERC20VaultL2EventTokenReleased,
    ERC20VaultL2EventTokenSent,
    ERC721VaultL2EventBridgedTokenDeployed,
    ERC721VaultL2EventTokenReceived,
    ERC721VaultL2EventTokenReleased,
    ERC721VaultL2EventTokenSent,
    L2Block,
    L2Transaction,
    BridgeL2CallProcessMessage,
    BridgeL2CallSendMessage,
    ERC20Info,
    mysql_db
)

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import requests
# import os
# cwd = os.getcwd()
# print(f"3333 {cwd}")

# scan one block and save to db
class BlockScanner():
    def __init__(self):
        self.cache_dir = "../tx_binaries/a5/l2"
        self.l2_rpc_endpoint = "https://rpc.jolnir.taiko.xyz/"
        self.chain_id = 167007
        self.w3 = Web3(Web3.HTTPProvider(self.l2_rpc_endpoint))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.taiko_l2_bridge = "0x1000777700000000000000000000000000000004"
        self.taiko_l2_erc20_vault_address = "0x1000777700000000000000000000000000000002"
        self.taiko_l2_erc721_vault_address = "0x1000777700000000000000000000000000000008"
        self.taiko_l2_erc1155_vault_address = "0x1000777700000000000000000000000000000009"
        
        # raw data
        self.block_id: int
        self.tx_list: list[TxData]
        self.receipt_list: list[TxReceipt]

        # db data cache
        self.db_l2_block: dict
        self.db_l2_transaction_list: list[dict]
        self.db_bridge_l2_call_process_message: list[dict]
        self.db_bridge_l2_call_send_message: list[dict]
        self.db_erc20_vault_l2_event_bridged_token_deployed: list[dict]
        self.db_erc20_vault_l2_event_token_sent: list[dict]
        self.db_erc20_vault_l2_event_token_released: list[dict]
        self.db_erc20_vault_l2_event_token_received: list[dict]
        self.db_erc721_vault_l2_event_bridged_token_deployed: list[dict]
        self.db_erc721_vault_l2_event_token_sent: list[dict]
        self.db_erc721_vault_l2_event_token_released: list[dict]
        self.db_erc721_vault_l2_event_token_received: list[dict]
        self.db_erc1155_vault_l2_event_bridged_token_deployed: list[dict]
        self.db_erc1155_vault_l2_event_token_sent: list[dict]
        self.db_erc1155_vault_l2_event_token_released: list[dict]
        self.db_erc1155_vault_l2_event_token_received: list[dict]
        self.db_erc20_info: list[dict]
        # self.db_contract_info: list[dict]

        self._init_contract()

    def _init_contract(self):

        l2_taiko_l2_bridge_abi = []
        taiko_l2_bridge_address = self.taiko_l2_bridge[2:]
        taiko_l2_bridge_address = bytes.fromhex(taiko_l2_bridge_address)
        taiko_l2_bridge_address = Address(taiko_l2_bridge_address)
        with open(Path(__file__).parent / "taiko_l2_bridge_abi.json") as f:
            l2_taiko_l2_bridge_abi = json.load(f)
        self.taiko_l2_bridge_contract = self.w3.eth.contract(taiko_l2_bridge_address, abi=l2_taiko_l2_bridge_abi)
        
        l2_taiko_l2_erc20_vault_abi = []
        taiko_l2_erc20_vault_address = self.taiko_l2_erc20_vault_address[2:]
        taiko_l2_erc20_vault_address = bytes.fromhex(taiko_l2_erc20_vault_address)
        taiko_l2_erc20_vault_address = Address(taiko_l2_erc20_vault_address)
        with open(Path(__file__).parent / "taiko_l2_erc20_vault_abi.json") as f:
            l2_taiko_l2_erc20_vault_abi = json.load(f)
        self.taiko_l2_erc20_vault_contract = self.w3.eth.contract(taiko_l2_erc20_vault_address, abi=l2_taiko_l2_erc20_vault_abi)

        l2_taiko_l2_erc721_vault_abi = []
        taiko_l2_erc721_vault_address = self.taiko_l2_erc721_vault_address[2:]
        taiko_l2_erc721_vault_address = bytes.fromhex(taiko_l2_erc721_vault_address)
        taiko_l2_erc721_vault_address = Address(taiko_l2_erc721_vault_address)
        with open(Path(__file__).parent / "taiko_l2_erc721_vault_abi.json") as f:
            l2_taiko_l2_erc721_vault_abi = json.load(f)
        self.taiko_l2_erc721_vault_contract = self.w3.eth.contract(taiko_l2_erc721_vault_address, abi=l2_taiko_l2_erc721_vault_abi)

        l2_taiko_l2_erc1155_vault_abi = []
        taiko_l2_erc1155_vault_address = self.taiko_l2_erc1155_vault_address[2:]
        taiko_l2_erc1155_vault_address = bytes.fromhex(taiko_l2_erc1155_vault_address)
        taiko_l2_erc1155_vault_address = Address(taiko_l2_erc1155_vault_address)
        with open(Path(__file__).parent / "taiko_l2_erc1155_vault_abi.json") as f:
            l2_taiko_l2_erc1155_vault_abi = json.load(f)
        self.taiko_l2_erc1155_vault_contract = self.w3.eth.contract(taiko_l2_erc1155_vault_address, abi=l2_taiko_l2_erc1155_vault_abi)



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
        tx_binary = Path(Path(__file__).parent / f"{self.cache_dir}/{self.block_id}")
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
            with open(Path(__file__).parent / f"{self.cache_dir}/{self.block_id}", 'rb') as f:
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
        
        with open(Path(__file__).parent / f"{self.cache_dir}/{self.block_id}", 'wb') as f:
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
                        "message_from": data["message"]["from"],
                        "message_src_chain_id": data["message"]["srcChainId"],
                        "message_dest_chain_id": data["message"]["destChainId"],
                        "message_user": data["message"]["user"],
                        "message_to": data["message"]["to"],
                        "message_refund_to": data["message"]["refundTo"],
                        "message_value": data["message"]["value"],
                        "message_fee": data["message"]["fee"],
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
                        "message_from": data["message"]["from"],
                        "message_src_chain_id": data["message"]["srcChainId"],
                        "message_dest_chain_id": data["message"]["destChainId"],
                        "message_user": data["message"]["user"],
                        "message_to": data["message"]["to"],
                        "message_refund_to": data["message"]["refundTo"],
                        "message_value": data["message"]["value"],
                        "message_fee": data["message"]["fee"],
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

    def parse_erc20_vault_l2_event_bridged_token_deployed(self):
        self.db_erc20_vault_l2_event_bridged_token_deployed = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc20_vault_contract.events.BridgedTokenDeployed().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc20_vault_address:
                    continue
                self.db_erc20_vault_l2_event_bridged_token_deployed.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "log_index": event.get("logIndex"),
                    "src_chain_id": event.get("args").get("srcChainId"),
                    "ctoken": event.get("args").get("ctoken"),
                    "btoken": event.get("args").get("btoken"),
                    "ctoken_symbol": event.get("args").get("ctokenSymbol"),
                    "ctoken_name": event.get("args").get("ctokenName"),
                    "ctoken_decimal": event.get("args").get("ctokenDecimal"),
                })

    def save_erc20_vault_l2_event_bridged_token_deployed(self):
        count = ERC20VaultL2EventBridgedTokenDeployed.select().where(ERC20VaultL2EventBridgedTokenDeployed.block_id == self.block_id).count()
        if count != len(self.db_erc20_vault_l2_event_bridged_token_deployed):
            ERC20VaultL2EventBridgedTokenDeployed.delete().where(ERC20VaultL2EventBridgedTokenDeployed.block_id == self.block_id).execute()
            ERC20VaultL2EventBridgedTokenDeployed.insert_many(self.db_erc20_vault_l2_event_bridged_token_deployed).execute()

    def parse_erc20_vault_l2_event_token_sent(self):
        self.db_erc20_vault_l2_event_token_sent = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc20_vault_contract.events.TokenSent().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc20_vault_address:
                    continue
                self.db_erc20_vault_l2_event_token_sent.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "log_index": event.get("logIndex"),
                    "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                    "tx_from": event.get("args").get("from"),
                    "tx_to": event.get("args").get("to"),
                    "dest_chain_id": event.get("args").get("destChainId"),
                    "token": event.get("args").get("token"),
                    "amount": event.get("args").get("amount"),
                })

    def save_erc20_vault_l2_event_token_sent(self):
        count = ERC20VaultL2EventTokenSent.select().where(ERC20VaultL2EventTokenSent.block_id == self.block_id).count()
        if count != len(self.db_erc20_vault_l2_event_token_sent):
            ERC20VaultL2EventTokenSent.delete().where(ERC20VaultL2EventTokenSent.block_id == self.block_id).execute()
            ERC20VaultL2EventTokenSent.insert_many(self.db_erc20_vault_l2_event_token_sent).execute()

    def parse_erc20_vault_l2_event_token_released(self):
        self.db_erc20_vault_l2_event_token_released = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc20_vault_contract.events.TokenReleased().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc20_vault_address:
                    continue
                self.db_erc20_vault_l2_event_token_released.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "log_index": event.get("logIndex"),
                    "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                    "tx_from": event.get("args").get("from"),
                    "token": event.get("args").get("token"),
                    "amount": event.get("args").get("amount"),
                })

    def save_erc20_vault_l2_event_token_released(self):
        count = ERC20VaultL2EventTokenReleased.select().where(ERC20VaultL2EventTokenReleased.block_id == self.block_id).count()
        if count != len(self.db_erc20_vault_l2_event_token_released):
            ERC20VaultL2EventTokenReleased.delete().where(ERC20VaultL2EventTokenReleased.block_id == self.block_id).execute()
            ERC20VaultL2EventTokenReleased.insert_many(self.db_erc20_vault_l2_event_token_released).execute()

    def parse_erc20_vault_l2_event_token_received(self):
        self.db_erc20_vault_l2_event_token_received = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc20_vault_contract.events.TokenReceived().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc20_vault_address:
                    continue
                self.db_erc20_vault_l2_event_token_received.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "log_index": event.get("logIndex"),
                    "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                    "tx_from": event.get("args").get("from"),
                    "tx_to": event.get("args").get("to"),
                    "src_chain_id": event.get("args").get("srcChainId"),
                    "token": event.get("args").get("token"),
                    "amount": event.get("args").get("amount"),
                })

    def save_erc20_vault_l2_event_token_received(self):
        count = ERC20VaultL2EventTokenReceived.select().where(ERC20VaultL2EventTokenReceived.block_id == self.block_id).count()
        if count != len(self.db_erc20_vault_l2_event_token_received):
            ERC20VaultL2EventTokenReceived.delete().where(ERC20VaultL2EventTokenReceived.block_id == self.block_id).execute()
            ERC20VaultL2EventTokenReceived.insert_many(self.db_erc20_vault_l2_event_token_received).execute()

    def parse_erc721_vault_l2_event_bridged_token_deployed(self):
        self.db_erc721_vault_l2_event_bridged_token_deployed = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc721_vault_contract.events.BridgedTokenDeployed().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc721_vault_address:
                    continue
                self.db_erc721_vault_l2_event_bridged_token_deployed.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "log_index": event.get("logIndex"),
                    "src_chain_id": event.get("args").get("srcChainId"),
                    "ctoken": event.get("args").get("ctoken"),
                    "btoken": event.get("args").get("btoken"),
                    "ctoken_symbol": event.get("args").get("ctokenSymbol"),
                    "ctoken_name": event.get("args").get("ctokenName"),
                })

    def save_erc721_vault_l2_event_bridged_token_deployed(self):
        count = ERC721VaultL2EventBridgedTokenDeployed.select().where(ERC721VaultL2EventBridgedTokenDeployed.block_id == self.block_id).count()
        if count != len(self.db_erc721_vault_l2_event_bridged_token_deployed):
            ERC721VaultL2EventBridgedTokenDeployed.delete().where(ERC721VaultL2EventBridgedTokenDeployed.block_id == self.block_id).execute()
            ERC721VaultL2EventBridgedTokenDeployed.insert_many(self.db_erc721_vault_l2_event_bridged_token_deployed).execute()

    def parse_erc721_vault_l2_event_token_sent(self):
        self.db_erc721_vault_l2_event_token_sent = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc721_vault_contract.events.TokenSent().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc721_vault_address:
                    continue
                token_ids = event.get("args").get("tokenIds")
                amounts = event.get("args").get("amounts")
                if len(token_ids) != len(amounts):
                    continue
                for i in range(len(token_ids)):
                    self.db_erc721_vault_l2_event_token_sent.append({
                        "block_id": event.get("blockNumber"),
                        "tx_hash": event.get("transactionHash").hex(),
                        "log_index": event.get("logIndex"),
                        "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                        "tx_from": event.get("args").get("from"),
                        "tx_to": event.get("args").get("to"),
                        "dest_chain_id": event.get("args").get("destChainId"),
                        "token": event.get("args").get("token"),
                        "token_id": token_ids[i],
                        "amount": amounts[i],
                    })

    def save_erc721_vault_l2_event_token_sent(self):
        count = ERC721VaultL2EventTokenSent.select().where(ERC721VaultL2EventTokenSent.block_id == self.block_id).count()
        if count != len(self.db_erc721_vault_l2_event_token_sent):
            ERC721VaultL2EventTokenSent.delete().where(ERC721VaultL2EventTokenSent.block_id == self.block_id).execute()
            ERC721VaultL2EventTokenSent.insert_many(self.db_erc721_vault_l2_event_token_sent).execute()

    def parse_erc721_vault_l2_event_token_released(self):
        self.db_erc721_vault_l2_event_token_released = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc721_vault_contract.events.TokenReleased().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc721_vault_address:
                    continue
                token_ids = event.get("args").get("tokenIds")
                amounts = event.get("args").get("amounts")
                if len(token_ids) != len(amounts):
                    continue
                for i in range(len(token_ids)):
                    self.db_erc721_vault_l2_event_token_released.append({
                        "block_id": event.get("blockNumber"),
                        "tx_hash": event.get("transactionHash").hex(),
                        "log_index": event.get("logIndex"),
                        "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                        "tx_from": event.get("args").get("from"),
                        "token": event.get("args").get("token"),
                        "token_id": token_ids[i],
                        "amount": amounts[i],
                    })

    def save_erc721_vault_l2_event_token_released(self):
        count = ERC721VaultL2EventTokenReleased.select().where(ERC721VaultL2EventTokenReleased.block_id == self.block_id).count()
        if count != len(self.db_erc721_vault_l2_event_token_released):
            ERC721VaultL2EventTokenReleased.delete().where(ERC721VaultL2EventTokenReleased.block_id == self.block_id).execute()
            ERC721VaultL2EventTokenReleased.insert_many(self.db_erc721_vault_l2_event_token_released).execute()

    def parse_erc721_vault_l2_event_token_received(self):
        self.db_erc721_vault_l2_event_token_received = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc721_vault_contract.events.TokenReceived().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc721_vault_address:
                    continue
                token_ids = event.get("args").get("tokenIds")
                amounts = event.get("args").get("amounts")
                if len(token_ids) != len(amounts):
                    continue
                for i in range(len(token_ids)):
                    self.db_erc721_vault_l2_event_token_received.append({
                        "block_id": event.get("blockNumber"),
                        "tx_hash": event.get("transactionHash").hex(),
                        "log_index": event.get("logIndex"),
                        "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                        "tx_from": event.get("args").get("from"),
                        "tx_to": event.get("args").get("to"),
                        "src_chain_id": event.get("args").get("srcChainId"),
                        "token": event.get("args").get("token"),
                        "token_id": token_ids[i],
                        "amount": amounts[i],
                    })

    def save_erc721_vault_l2_event_token_received(self):
        count = ERC721VaultL2EventTokenReceived.select().where(ERC721VaultL2EventTokenReceived.block_id == self.block_id).count()
        if count != len(self.db_erc721_vault_l2_event_token_received):
            ERC721VaultL2EventTokenReceived.delete().where(ERC721VaultL2EventTokenReceived.block_id == self.block_id).execute()
            ERC721VaultL2EventTokenReceived.insert_many(self.db_erc721_vault_l2_event_token_received).execute()

    def parse_erc1155_vault_l2_event_bridged_token_deployed(self):
        self.db_erc1155_vault_l2_event_bridged_token_deployed = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc1155_vault_contract.events.BridgedTokenDeployed().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc1155_vault_address:
                    continue
                self.db_erc1155_vault_l2_event_bridged_token_deployed.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "log_index": event.get("logIndex"),
                    "src_chain_id": event.get("args").get("srcChainId"),
                    "ctoken": event.get("args").get("ctoken"),
                    "btoken": event.get("args").get("btoken"),
                    "ctoken_symbol": event.get("args").get("ctokenSymbol"),
                    "ctoken_name": event.get("args").get("ctokenName"),
                    "ctoken_decimal": event.get("args").get("ctokenDecimal"),
                })

    def save_erc1155_vault_l2_event_bridged_token_deployed(self):
        count = ERC1155VaultL2EventBridgedTokenDeployed.select().where(ERC1155VaultL2EventBridgedTokenDeployed.block_id == self.block_id).count()
        if count != len(self.db_erc1155_vault_l2_event_bridged_token_deployed):
            ERC1155VaultL2EventBridgedTokenDeployed.delete().where(ERC1155VaultL2EventBridgedTokenDeployed.block_id == self.block_id).execute()
            ERC1155VaultL2EventBridgedTokenDeployed.insert_many(self.db_erc1155_vault_l2_event_bridged_token_deployed).execute()

    def parse_erc1155_vault_l2_event_token_sent(self):
        self.db_erc1155_vault_l2_event_token_sent = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc1155_vault_contract.events.TokenSent().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc1155_vault_address:
                    continue
                token_ids = event.get("args").get("tokenIds")
                amounts = event.get("args").get("amounts")
                if len(token_ids) != len(amounts):
                    continue
                for i in range(len(token_ids)):
                    self.db_erc1155_vault_l2_event_token_sent.append({
                        "block_id": event.get("blockNumber"),
                        "tx_hash": event.get("transactionHash").hex(),
                        "log_index": event.get("logIndex"),
                        "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                        "tx_from": event.get("args").get("from"),
                        "tx_to": event.get("args").get("to"),
                        "dest_chain_id": event.get("args").get("destChainId"),
                        "token": event.get("args").get("token"),
                        "token_id": token_ids[i],
                        "amount": amounts[i],
                    })

    def save_erc1155_vault_l2_event_token_sent(self):
        count = ERC1155VaultL2EventTokenSent.select().where(ERC1155VaultL2EventTokenSent.block_id == self.block_id).count()
        if count != len(self.db_erc1155_vault_l2_event_token_sent):
            ERC1155VaultL2EventTokenSent.delete().where(ERC1155VaultL2EventTokenSent.block_id == self.block_id).execute()
            ERC1155VaultL2EventTokenSent.insert_many(self.db_erc1155_vault_l2_event_token_sent).execute()

    def parse_erc1155_vault_l2_event_token_released(self):
        self.db_erc1155_vault_l2_event_token_released = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc1155_vault_contract.events.TokenReleased().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc1155_vault_address:
                    continue
                token_ids = event.get("args").get("tokenIds")
                amounts = event.get("args").get("amounts")
                if len(token_ids) != len(amounts):
                    continue
                for i in range(len(token_ids)):
                    self.db_erc1155_vault_l2_event_token_released.append({
                        "block_id": event.get("blockNumber"),
                        "tx_hash": event.get("transactionHash").hex(),
                        "log_index": event.get("logIndex"),
                        "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                        "tx_from": event.get("args").get("from"),
                        "token": event.get("args").get("token"),
                        "token_id": token_ids[i],
                        "amount": amounts[i],
                    })

    def save_erc1155_vault_l2_event_token_released(self):
        count = ERC1155VaultL2EventTokenReleased.select().where(ERC1155VaultL2EventTokenReleased.block_id == self.block_id).count()
        if count != len(self.db_erc1155_vault_l2_event_token_released):
            ERC1155VaultL2EventTokenReleased.delete().where(ERC1155VaultL2EventTokenReleased.block_id == self.block_id).execute()
            ERC1155VaultL2EventTokenReleased.insert_many(self.db_erc1155_vault_l2_event_token_released).execute()

    def parse_erc1155_vault_l2_event_token_received(self):
        self.db_erc1155_vault_l2_event_token_received = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_l2_erc1155_vault_contract.events.TokenReceived().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l2_erc1155_vault_address:
                    continue
                token_ids = event.get("args").get("tokenIds")
                amounts = event.get("args").get("amounts")
                if len(token_ids) != len(amounts):
                    continue
                for i in range(len(token_ids)):
                    self.db_erc1155_vault_l2_event_token_received.append({
                        "block_id": event.get("blockNumber"),
                        "tx_hash": event.get("transactionHash").hex(),
                        "log_index": event.get("logIndex"),
                        "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                        "tx_from": event.get("args").get("from"),
                        "tx_to": event.get("args").get("to"),
                        "src_chain_id": event.get("args").get("srcChainId"),
                        "token": event.get("args").get("token"),
                        "token_id": token_ids[i],
                        "amount": amounts[i],
                    })

    def save_erc1155_vault_l2_event_token_received(self):
        count = ERC1155VaultL2EventTokenReceived.select().where(ERC1155VaultL2EventTokenReceived.block_id == self.block_id).count()
        if count != len(self.db_erc1155_vault_l2_event_token_received):
            ERC1155VaultL2EventTokenReceived.delete().where(ERC1155VaultL2EventTokenReceived.block_id == self.block_id).execute()
            ERC1155VaultL2EventTokenReceived.insert_many(self.db_erc1155_vault_l2_event_token_received).execute()

    def get_all_tokens_info(self):
        self.db_erc20_info = []
        result = mysql_db.execute_sql("""
            with token_raw as (
                select token from erc20_vault_l2_event_token_received
                union
                select token from erc20_vault_l2_event_token_sent
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
    
