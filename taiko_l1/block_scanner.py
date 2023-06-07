import os
import json
import typing
import pickle
from typing import Iterable, Sequence
from eth_typing import Address, BlockNumber
from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware
from web3.types import BlockData, TxData, TxReceipt, EventData
from hexbytes import HexBytes
from web3.contract.contract import Contract

from .schema import (
    BridgeL1CallProcessMessage,
    BridgeL1CallSendMessage,
    TaikoL1EventBlockVerified,
    TaikoL1EventCrossChainSynced,
    TaikoL1EventBlockProposed,
    TaikoL1EventBlockProven,
    TaikoL1EventEthDeposited,
    TaikoL1CallProposeBlock,
    TaikoL1CallProveBlock,
    TaikoL1CallVerifyBlocks,
    TaikoL1CallDepositTaikoToken,
    TaikoL1CallWithdrawTaikoToken,
    TaikoTokenL1EventMint,
    TaikoTokenL1EventBurn,
    TaikoTokenL1EventTransfer,
    # TaikoBridgeL1EventMessageStatusChanged,
    # TaikoBridgeL1EventMessageSent,
    L1Block,
    L1Transaction,
    
    TokenVaultL1EventERC20Received,
    TokenVaultL1EventERC20Sent,
    ERC20Info,
    mysql_db
)

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

# import os
# cwd = os.getcwd()
# print(f"3333 {cwd}")

# scan one block and save to db
class BlockScanner():
    def __init__(self):
        self.l1_rpc_endpoint = "https://sepolia.infura.io/v3/e0e066733e0e066733e0e0"
        self.chain_id = 167005
        self.w3 = Web3(Web3.HTTPProvider(self.l1_rpc_endpoint))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.taiko_l1_address = "0x6375394335f34848b850114b66A49D6F47f2cdA8"
        self.taiko_token_l1_address = "0xE52952B8063d0AE6Bd35E894866d8148976ce645"
        # self.taiko_l1_address_manager = "0x6669f7B6DD295233C9F9482b5c7271E0cE5Aac4f"
        self.taiko_l1_bridge = "0x7D992599E1B8b4508Ba6E2Ba97893b4C36C23A28"
        # self.taiko_l1_signal_service = "0x07130410064Ab5C32486CC36904fb219ae97156F"
        self.taiko_l1_token_vault = "0xD70506580B5F65e68ed0dbA7B4Ae507641C48197"
        self.taiko_addresses = set([
            self.taiko_l1_address,
            self.taiko_token_l1_address,
            # self.taiko_l1_address_manager,
            self.taiko_l1_bridge,
            # self.taiko_l1_signal_service,
            self.taiko_l1_token_vault,
            # for contract creation
            None
        ])
        self.taiko_l1_contract: Contract
        self.taiko_token_l1_contract: Contract
        self.taiko_l1_bridge_contract: Contract
        self.taiko_l1_token_vault_contract: Contract
        
        # raw data
        self.block_id: int
        # self.block: BlockData
        # self.db_l1_block_delete_save_flag = True # delete old block records before save
        self.tx_list: list[TxData]
        self.receipt_list: list[TxReceipt]
        # self.db_l1_transaction_list_delete_save_flag = True  # delete old tx records before save

        # db data cache
        self.db_l1_block: dict
        self.db_l1_transaction_list: list[dict]
        self.db_l1_call_propose_block: list[dict]
        self.db_l1_call_prove_block: list[dict]
        self.db_l1_call_verify_blocks: list[dict]
        self.db_l1_call_deposit_taiko_token: list[dict]
        self.db_l1_call_withdraw_taiko_token: list[dict]
        self.db_l1_event_block_verified: list[dict]
        self.db_l1_event_cross_chain_synced: list[dict]
        self.db_l1_event_block_proposed: list[dict]
        self.db_l1_event_block_proven: list[dict]
        self.db_l1_event_eth_deposited: list[dict]
        self.db_taiko_token_event_mint: list[dict]
        self.db_taiko_token_event_burn: list[dict]
        self.db_taiko_token_event_transfer: list[dict]
        self.db_bridge_l1_call_process_message: list[dict]
        self.db_bridge_l1_call_send_message: list[dict]
        self.db_token_vault_l1_event_erc20_sent: list[dict]
        self.db_token_vault_l1_event_erc20_received: list[dict]
        self.db_erc20_info: list[dict]

        self._init_contract()

    def _init_contract(self):
        taiko_l1_address = self.taiko_l1_address[2:]
        taiko_l1_address = bytes.fromhex(taiko_l1_address)
        taiko_l1_address = Address(taiko_l1_address)
        l1_taiko_l1_abi = []
        with open(Path(__file__).parent / "taiko_l1_abi.json") as f:
            l1_taiko_l1_abi = json.load(f)
        self.taiko_l1_contract = self.w3.eth.contract(taiko_l1_address, abi=l1_taiko_l1_abi)

        taiko_token_l1_address = self.taiko_token_l1_address[2:]
        taiko_token_l1_address = bytes.fromhex(taiko_token_l1_address)
        taiko_token_l1_address = Address(taiko_token_l1_address)
        l1_taiko_token_l1_abi = []
        with open(Path(__file__).parent / "taiko_token_l1_abi.json") as f:
            l1_taiko_token_l1_abi = json.load(f)
        self.taiko_token_l1_contract = self.w3.eth.contract(taiko_token_l1_address, abi=l1_taiko_token_l1_abi)

        l1_taiko_l1_bridge_abi = []
        taiko_l1_bridge_address = self.taiko_l1_bridge[2:]
        taiko_l1_bridge_address = bytes.fromhex(taiko_l1_bridge_address)
        taiko_l1_bridge_address = Address(taiko_l1_bridge_address)
        with open(Path(__file__).parent / "taiko_l1_bridge_abi.json") as f:
            l1_taiko_l1_bridge_abi = json.load(f)
        self.taiko_l1_bridge_contract = self.w3.eth.contract(taiko_l1_bridge_address, abi=l1_taiko_l1_bridge_abi)

        l1_taiko_l1_token_vault_abi = []
        taiko_l1_token_vault_address = self.taiko_l1_token_vault[2:]
        taiko_l1_token_vault_address = bytes.fromhex(taiko_l1_token_vault_address)
        taiko_l1_token_vault_address = Address(taiko_l1_token_vault_address)
        with open(Path(__file__).parent / "taiko_l1_token_vault_abi.json") as f:
            l1_taiko_l1_token_vault_abi = json.load(f)
        self.taiko_l1_token_vault_contract = self.w3.eth.contract(taiko_l1_token_vault_address, abi=l1_taiko_l1_token_vault_abi)


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

        tx_num = L1Block.select(L1Block.taiko_txs_num).where(L1Block.block_id == self.block_id).scalar()
        tx_binary = Path(Path(__file__).parent / f"../tx_binaries/l1/{self.block_id}")
        if tx_num and tx_binary.is_file():
            l1_block = L1Block.get(L1Block.block_id == self.block_id)
            self.db_l1_block = {
                "block_id": l1_block.block_id,
                "block_hash": l1_block.block_hash,
                "timestamp": l1_block.timestamp,
                "taiko_txs_num": l1_block.taiko_txs_num,
            }
            with open(Path(__file__).parent / f"../tx_binaries/l1/{self.block_id}", 'rb') as f:
                (self.tx_list, self.receipt_list) = pickle.load(f)
            if tx_num == len(self.tx_list) and tx_num == len(self.receipt_list):
                return
        
        block = self.w3.eth.get_block(self.block_id, full_transactions=True)
        txs = block.get("transactions")
        txs = typing.cast(Sequence[TxData], txs)
        
        self.tx_list = [tx for tx in txs if tx.get("to") in self.taiko_addresses]
        self.receipt_list = []
        for tx in self.tx_list:
            hash = tx.get("hash")
            hash = typing.cast(HexBytes, hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(hash)
            self.receipt_list.append(tx_receipt)
        
        with open(Path(__file__).parent / f"../tx_binaries/l1/{self.block_id}", 'wb') as f:
            pickle.dump((self.tx_list, self.receipt_list), f)
        
        self.db_l1_block = {
            "block_id": block.get("number"),
            "block_hash": block.get("hash").hex(),
            "parent_hash": block.get("parentHash").hex(),
            "timestamp": block.get("timestamp"),
            "taiko_txs_num": len(self.tx_list),
        }

    # def fetch_data(self):
    #     if L1Block.select().where(L1Block.block_id == self.block_id).count():
    #         block_dump = L1Block.get(L1Block.block_id == self.block_id).block_dump
    #         self.block = pickle.loads(block_dump)
    #         self.db_l1_block_delete_save_flag = False
    #         print("self.db_l1_block_delete_save_flag = False")
    #     else:
    #         self.block = self.w3.eth.get_block(self.block_id, full_transactions=True)
    #         self.db_l1_block_delete_save_flag = True
    #         print("self.db_l1_block_delete_save_flag = True")
    #     txs = self.block.get("transactions")
    #     txs = typing.cast(Sequence[TxData], txs)
    #     # tx_list = list(txs)
    #     self.tx_list = [tx for tx in txs if tx.get("to") in self.taiko_addresses]
    #     self.receipt_list = []
    #     if L1Transaction.select().where(L1Transaction.block_id == self.block_id).count() == len(self.tx_list):
    #         l1_transactions = L1Transaction.select().where(L1Transaction.block_id == self.block_id).order_by(L1Transaction.transaction_index)
    #         for l1_reansaction in l1_transactions:
    #             self.receipt_list.append(pickle.loads(l1_reansaction.receipt_dump))
    #         for tx, receipt in zip(self.tx_list, self.receipt_list):
    #             assert tx.get("hash") == receipt.get("transactionHash")
    #         self.db_l1_transaction_list_delete_save_flag = False
    #         print("self.db_l1_transaction_list_delete_save_flag = False")
    #     else:
    #         for tx in self.tx_list:
    #             hash = tx.get("hash")
    #             hash = typing.cast(HexBytes, hash)
    #             tx_receipt = self.w3.eth.get_transaction_receipt(hash)
    #             self.receipt_list.append(tx_receipt)
    #         self.db_l1_transaction_list_delete_save_flag = True
    #         print("self.db_l1_transaction_list_delete_save_flag = True")
            
    # def parse_block(self):
    #     self.db_l1_block = {
    #         "block_id": self.block.get("number"),
    #         "block_hash": self.block.get("hash").hex(),
    #         "parent_hash": self.block.get("parentHash").hex(),
    #         "timestamp": self.block.get("timestamp"),
    #         "taiko_txs_num": len(self.tx_list),
    #         # "block_dump": pickle.dumps(self.block)
    #     }
    
    def save_block(self):
        count = L1Block.select().where(L1Block.block_id == self.block_id).count()
        if count == 0:
            L1Block.create(**self.db_l1_block)
        elif count != 1:
            L1Block.delete().where(L1Block.block_id == self.block_id).execute()
            L1Block.create(**self.db_l1_block)

    def parse_txs(self):
        self.db_l1_transaction_list = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            self.db_l1_transaction_list.append({
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
                "timestamp": self.db_l1_block.get("timestamp"),
                # "tx_dump": pickle.dumps(tx),
                # "receipt_dump": pickle.dumps(receipt),
            })

    def save_txs(self):
        count = L1Transaction.select().where(L1Transaction.block_id == self.block_id).count()
        if count != len(self.tx_list):
            L1Transaction.delete().where(L1Transaction.block_id == self.block_id).execute()
            L1Transaction.insert_many(self.db_l1_transaction_list).execute()

    def parse_l1_call_propose_block(self):
        self.db_l1_call_propose_block = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, _) = self.taiko_l1_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "proposeBlock":
                    self.db_l1_call_propose_block.append({
                        "block_id": tx.get("blockNumber"),
                        "tx_hash": tx.get("hash").hex(),
                        "status": receipt.get("status"),
                    })
            except Exception:
                continue

    def save_l1_call_propose_block(self):
        count = TaikoL1CallProposeBlock.select().where(TaikoL1CallProposeBlock.block_id == self.block_id).count()
        if count != len(self.db_l1_call_propose_block):
            TaikoL1CallProposeBlock.delete().where(TaikoL1CallProposeBlock.block_id == self.block_id).execute()
            TaikoL1CallProposeBlock.insert_many(self.db_l1_call_propose_block).execute()

    def parse_l1_call_prove_block(self):
        self.db_l1_call_prove_block = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l1_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "proveBlock":
                    self.db_l1_call_prove_block.append({
                        "block_id": tx.get("blockNumber"),
                        "tx_hash": tx.get("hash").hex(),
                        "proven_id": data["blockId"],
                        "status": receipt.get("status"),
                    })
            except Exception:
                continue

    def save_l1_call_prove_block(self):
        count = TaikoL1CallProveBlock.select().where(TaikoL1CallProveBlock.block_id == self.block_id).count()
        if count != len(self.db_l1_call_prove_block):
            TaikoL1CallProveBlock.delete().where(TaikoL1CallProveBlock.block_id == self.block_id).execute()
            TaikoL1CallProveBlock.insert_many(self.db_l1_call_prove_block).execute()

    def parse_l1_call_verify_blocks(self):
        self.db_l1_call_verify_blocks = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l1_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "verifyBlocks":
                    self.db_l1_call_verify_blocks.append({
                        "block_id": tx.get("blockNumber"),
                        "tx_hash": tx.get("hash").hex(),
                        "max_blocks": data["maxBlocks"],
                        "status": receipt.get("status"),
                    })
            except Exception:
                continue

    def save_l1_call_verify_blocks(self):
        count = TaikoL1CallVerifyBlocks.select().where(TaikoL1CallVerifyBlocks.block_id == self.block_id).count()
        if count != len(self.db_l1_call_verify_blocks):
            TaikoL1CallVerifyBlocks.delete().where(TaikoL1CallVerifyBlocks.block_id == self.block_id).execute()
            TaikoL1CallVerifyBlocks.insert_many(self.db_l1_call_verify_blocks).execute()

    def parse_l1_call_deposit_taiko_token(self):
        self.db_l1_call_deposit_taiko_token = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l1_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "depositTaikoToken":
                    self.db_l1_call_deposit_taiko_token.append({
                        "block_id": tx.get("blockNumber"),
                        "tx_hash": tx.get("hash").hex(),
                        "amount": data["amount"],
                        "status": receipt.get("status"),
                    })
            except Exception:
                continue

    def save_l1_call_deposit_taiko_token(self):
        count = TaikoL1CallDepositTaikoToken.select().where(TaikoL1CallDepositTaikoToken.block_id == self.block_id).count()
        if count != len(self.db_l1_call_deposit_taiko_token):
            TaikoL1CallDepositTaikoToken.delete().where(TaikoL1CallDepositTaikoToken.block_id == self.block_id).execute()
            TaikoL1CallDepositTaikoToken.insert_many(self.db_l1_call_deposit_taiko_token).execute()

    def parse_l1_call_withdraw_taiko_token(self):
        self.db_l1_call_withdraw_taiko_token = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l1_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "withdrawTaikoToken":
                    self.db_l1_call_withdraw_taiko_token.append({
                        "block_id": tx.get("blockNumber"),
                        "tx_hash": tx.get("hash").hex(),
                        "amount": data["amount"],
                        "status": receipt.get("status"),
                    })
            except Exception:
                continue

    def save_l1_call_withdraw_taiko_token(self):
        count = TaikoL1CallWithdrawTaikoToken.select().where(TaikoL1CallWithdrawTaikoToken.block_id == self.block_id).count()
        if count != len(self.db_l1_call_withdraw_taiko_token):
            TaikoL1CallWithdrawTaikoToken.delete().where(TaikoL1CallWithdrawTaikoToken.block_id == self.block_id).execute()
            TaikoL1CallWithdrawTaikoToken.insert_many(self.db_l1_call_withdraw_taiko_token).execute()

    # def parse_l1_event_block_committed(self):
    #     self.db_l1_event_block_committed = []
    #     for receipt in self.receipt_list:
    #         if receipt.get("to") != self.taiko_l1_address:
    #             continue
    #         events: Iterable[EventData] = self.taiko_l1_contract.events.BlockCommitted().process_receipt(txn_receipt=receipt)
    #         for event in events:
    #             self.db_l1_event_block_committed.append({
    #                 "block_id": event.get("blockNumber"),
    #                 "tx_hash": event.get("transactionHash").hex(),
    #                 "commit_slot": event.get("args")["commitSlot"],
    #                 "commit_hash": self.w3.to_hex(event.get("args")["commitHash"]),
    #             })

    # def save_l1_event_block_committed(self):
    #     count = TaikoL1EventBlockCommitted.select().where(TaikoL1EventBlockCommitted.block_id == self.block_id).count()
    #     if count != len(self.db_l1_event_block_committed):
    #         TaikoL1EventBlockCommitted.delete().where(TaikoL1EventBlockCommitted.block_id == self.block_id).execute()
    #         TaikoL1EventBlockCommitted.insert_many(self.db_l1_event_block_committed).execute()

    def parse_l1_event_block_verified(self):
        self.db_l1_event_block_verified = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            if tx_to != self.taiko_l1_address:
                continue
            events: Iterable[EventData] = self.taiko_l1_contract.events.BlockVerified().process_receipt(txn_receipt=receipt)
            for event in events:                                
                self.db_l1_event_block_verified.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "verified_id": event.get("args").get("id"),
                    "block_hash": self.w3.to_hex(event.get("args").get("blockHash")),
                    "reward": event.get("args").get("reward"),
                })
    
    def save_l1_event_block_verified(self):
        count = TaikoL1EventBlockVerified.select().where(TaikoL1EventBlockVerified.block_id == self.block_id).count()
        if count != len(self.db_l1_event_block_verified):
            TaikoL1EventBlockVerified.delete().where(TaikoL1EventBlockVerified.block_id == self.block_id).execute()
            TaikoL1EventBlockVerified.insert_many(self.db_l1_event_block_verified).execute()

    def parse_l1_event_cross_chain_synced(self):
        self.db_l1_event_cross_chain_synced = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            if tx_to != self.taiko_l1_address:
                continue
            events: Iterable[EventData] = self.taiko_l1_contract.events.CrossChainSynced().process_receipt(txn_receipt=receipt)
            for event in events:                                
                self.db_l1_event_cross_chain_synced.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "src_height": event.get("args").get("srcHeight"),
                    "block_hash": self.w3.to_hex(event.get("args").get("blockHash")),
                    "signal_root": self.w3.to_hex(event.get("args").get("signalRoot")),
                })
    
    def save_l1_event_cross_chain_synced(self):
        count = TaikoL1EventCrossChainSynced.select().where(TaikoL1EventCrossChainSynced.block_id == self.block_id).count()
        if count != len(self.db_l1_event_cross_chain_synced):
            TaikoL1EventCrossChainSynced.delete().where(TaikoL1EventCrossChainSynced.block_id == self.block_id).execute()
            TaikoL1EventCrossChainSynced.insert_many(self.db_l1_event_cross_chain_synced).execute()

    def parse_l1_event_block_proposed(self):
        self.db_l1_event_block_proposed = []
        for receipt in self.receipt_list:
            tx_from = receipt.get("from")
            events: Iterable[EventData] = self.taiko_l1_contract.events.BlockProposed().process_receipt(txn_receipt=receipt)

            for event in events:
                self.db_l1_event_block_proposed.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "proposer": tx_from,
                    "proposed_id": event.get("args").get("id"),
                    "meta_id": event.get("args").get("meta").get("id"),
                    "meta_timestamp": event.get("args").get("meta").get("timestamp"),
                    "meta_l1_height": event.get("args").get("meta").get("l1Height"),
                    "meta_l1_hash": self.w3.to_hex(event.get("args").get("meta").get("l1Hash")),
                    "meta_mix_hash": self.w3.to_hex(event.get("args").get("meta").get("mixHash")),
                    "meta_tx_list_hash": self.w3.to_hex(event.get("args").get("meta").get("txListHash")),
                    "meta_tx_list_byte_start": event.get("args").get("meta").get("txListByteStart"),
                    "meta_tx_list_byte_end": event.get("args").get("meta").get("txListByteEnd"),
                    "meta_gas_limit": event.get("args").get("meta").get("gasLimit"),
                    "meta_beneficiary": event.get("args").get("meta").get("beneficiary"),
                    "meta_treasury": event.get("args").get("meta").get("treasury"),
                    "block_fee": event.get("args").get("blockFee"),
                })
        # print(self.db_l1_event_block_proposed)

    def save_l1_event_block_proposed(self):
        count = TaikoL1EventBlockProposed.select().where(TaikoL1EventBlockProposed.block_id == self.block_id).count()
        if count != len(self.db_l1_event_block_proposed):
            TaikoL1EventBlockProposed.delete().where(TaikoL1EventBlockProposed.block_id == self.block_id).execute()
            TaikoL1EventBlockProposed.insert_many(self.db_l1_event_block_proposed).execute()

    def parse_l1_event_block_proven(self):
        self.db_l1_event_block_proven = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            if tx_to != self.taiko_l1_address:
                continue
            events: Iterable[EventData] = self.taiko_l1_contract.events.BlockProven().process_receipt(txn_receipt=receipt)
            for event in events:
                self.db_l1_event_block_proven.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "proven_id": event.get("args").get("id"),
                    "parent_hash": self.w3.to_hex(event.get("args").get("parentHash")),
                    "block_hash": self.w3.to_hex(event.get("args").get("blockHash")),
                    "signal_root": self.w3.to_hex(event.get("args").get("signalRoot")),
                    "prover": event.get("args").get("prover"),
                    "parent_gas_used": event.get("args").get("parentGasUsed"),
                })

    def save_l1_event_block_proven(self):
        count = TaikoL1EventBlockProven.select().where(TaikoL1EventBlockProven.block_id == self.block_id).count()
        if count != len(self.db_l1_event_block_proven):
            TaikoL1EventBlockProven.delete().where(TaikoL1EventBlockProven.block_id == self.block_id).execute()
            TaikoL1EventBlockProven.insert_many(self.db_l1_event_block_proven).execute()

    def parse_l1_event_eth_deposited(self):
        self.db_l1_event_eth_deposited = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            if tx_to != self.taiko_l1_address:
                continue
            events: Iterable[EventData] = self.taiko_l1_contract.events.EthDeposited().process_receipt(txn_receipt=receipt)
            for event in events:
                self.db_l1_event_eth_deposited.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "recipient": event.get("args").get("deposit").get("recipient"),
                    "amount": event.get("args").get("deposit").get("amount"),
                })

    def save_l1_event_eth_deposited(self):
        count = TaikoL1EventEthDeposited.select().where(TaikoL1EventEthDeposited.block_id == self.block_id).count()
        if count != len(self.db_l1_event_eth_deposited):
            TaikoL1EventEthDeposited.delete().where(TaikoL1EventEthDeposited.block_id == self.block_id).execute()
            TaikoL1EventEthDeposited.insert_many(self.db_l1_event_eth_deposited).execute()


    # def parse_l1_event_header_synced(self):
    #     self.db_l1_event_header_synced = []
    #     for receipt in self.receipt_list:
    #         tx_to = receipt.get("to")
    #         if tx_to != self.taiko_l1_address:
    #             continue
    #         events: Iterable[EventData] = self.taiko_l1_contract.events.HeaderSynced().process_receipt(txn_receipt=receipt)
    #         for event in events:
    #             self.db_l1_event_header_synced.append({
    #                 "block_id": event.get("blockNumber"),
    #                 "tx_hash": event.get("transactionHash").hex(),
    #                 "src_height": event.get("args").get("srcHeight"),
    #                 "src_hash": self.w3.to_hex(event.get("args").get("srcHash")),
    #             })
    
    # def save_l1_event_header_synced(self):
    #     count = TaikoL1EventHeaderSynced.select().where(TaikoL1EventHeaderSynced.block_id == self.block_id).count()
    #     if count != len(self.db_l1_event_header_synced):
    #         TaikoL1EventHeaderSynced.delete().where(TaikoL1EventHeaderSynced.block_id == self.block_id).execute()
    #         TaikoL1EventHeaderSynced.insert_many(self.db_l1_event_header_synced).execute()


    def parse_taiko_token_event_mint(self):
        self.db_taiko_token_event_mint = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            if not (tx_to == self.taiko_l1_address or tx_to == None):
                continue
            events: Iterable[EventData] = self.taiko_token_l1_contract.events.Mint().process_receipt(txn_receipt=receipt)
            for event in events:
                self.db_taiko_token_event_mint.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "account": event.get("args").get("account"),
                    "amount": event.get("args").get("amount"),
                })

    def save_taiko_token_event_mint(self):
        count = TaikoTokenL1EventMint.select().where(TaikoTokenL1EventMint.block_id == self.block_id).count()
        if count != len(self.db_taiko_token_event_mint):
            TaikoTokenL1EventMint.delete().where(TaikoTokenL1EventMint.block_id == self.block_id).execute()
            TaikoTokenL1EventMint.insert_many(self.db_taiko_token_event_mint).execute()

    def parse_taiko_token_event_burn(self):
        self.db_taiko_token_event_burn = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            if tx_to != self.taiko_l1_address:
                continue
            events: Iterable[EventData] = self.taiko_token_l1_contract.events.Burn().process_receipt(txn_receipt=receipt)
            for event in events:
                self.db_taiko_token_event_burn.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "account": event.get("args").get("account"),
                    "amount": event.get("args").get("amount"),
                })

    def save_taiko_token_event_burn(self):
        count = TaikoTokenL1EventBurn.select().where(TaikoTokenL1EventBurn.block_id == self.block_id).count()
        if count != len(self.db_taiko_token_event_burn):
            TaikoTokenL1EventBurn.delete().where(TaikoTokenL1EventBurn.block_id == self.block_id).execute()
            TaikoTokenL1EventBurn.insert_many(self.db_taiko_token_event_burn).execute()

    def parse_taiko_token_event_transfer(self):
        self.db_taiko_token_event_transfer = []
        for receipt in self.receipt_list:
            # tx_to = receipt.get("to")
            events: Iterable[EventData] = self.taiko_token_l1_contract.events.Transfer().process_receipt(txn_receipt=receipt)
            for event in events:
                # here makes the process more general
                # to-do: make all events parsing in this way
                if event.get("address") != self.taiko_token_l1_address:
                    continue
                self.db_taiko_token_event_transfer.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "tx_from": event.get("args").get("from"),
                    "tx_to": event.get("args").get("to"),
                    "value": event.get("args").get("value"),
                })

    def save_taiko_token_event_transfer(self):
        count = TaikoTokenL1EventTransfer.select().where(TaikoTokenL1EventTransfer.block_id == self.block_id).count()
        if count != len(self.db_taiko_token_event_transfer):
            TaikoTokenL1EventTransfer.delete().where(TaikoTokenL1EventTransfer.block_id == self.block_id).execute()
            TaikoTokenL1EventTransfer.insert_many(self.db_taiko_token_event_transfer).execute()


    def parse_bridge_l1_call_process_message(self):
        self.db_bridge_l1_call_process_message = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l1_bridge_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "processMessage":
                    self.db_bridge_l1_call_process_message.append({
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

    def save_bridge_l1_call_process_message(self):
        count = BridgeL1CallProcessMessage.select().where(BridgeL1CallProcessMessage.block_id == self.block_id).count()
        if count != len(self.db_bridge_l1_call_process_message):
            BridgeL1CallProcessMessage.delete().where(BridgeL1CallProcessMessage.block_id == self.block_id).execute()
            BridgeL1CallProcessMessage.insert_many(self.db_bridge_l1_call_process_message).execute()

    def parse_bridge_l1_call_send_message(self):
        self.db_bridge_l1_call_send_message = []
        for tx, receipt in zip(self.tx_list, self.receipt_list):
            try:
                (func, data) = self.taiko_l1_bridge_contract.decode_function_input(tx.get("input"))
                if func.function_identifier == "sendMessage":
                    self.db_bridge_l1_call_send_message.append({
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

    def save_bridge_l1_call_send_message(self):
        count = BridgeL1CallSendMessage.select().where(BridgeL1CallSendMessage.block_id == self.block_id).count()
        if count != len(self.db_bridge_l1_call_send_message):
            BridgeL1CallSendMessage.delete().where(BridgeL1CallSendMessage.block_id == self.block_id).execute()
            BridgeL1CallSendMessage.insert_many(self.db_bridge_l1_call_send_message).execute()

    def parse_token_vault_l1_event_erc20_sent(self):
        self.db_token_vault_l1_event_erc20_sent = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            # if tx_to != self.taiko_l1_bridge: # todo: check if its complete
            #     continue
            events: Iterable[EventData] = self.taiko_l1_token_vault_contract.events.ERC20Sent().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l1_token_vault:
                    continue
                self.db_token_vault_l1_event_erc20_sent.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                    "tx_from": event.get("args").get("from"),
                    "tx_to": event.get("args").get("to"),
                    "dest_chain_id": event.get("args").get("destChainId"),
                    "token": event.get("args").get("token"),
                    "amount": event.get("args").get("amount"),
                })

    def save_token_vault_l1_event_erc20_sent(self):
        count = TokenVaultL1EventERC20Sent.select().where(TokenVaultL1EventERC20Sent.block_id == self.block_id).count()
        if count != len(self.db_token_vault_l1_event_erc20_sent):
            TokenVaultL1EventERC20Sent.delete().where(TokenVaultL1EventERC20Sent.block_id == self.block_id).execute()
            TokenVaultL1EventERC20Sent.insert_many(self.db_token_vault_l1_event_erc20_sent).execute()


    def parse_token_vault_l1_event_erc20_received(self):
        self.db_token_vault_l1_event_erc20_received = []
        for receipt in self.receipt_list:
            tx_to = receipt.get("to")
            # if tx_to != self.taiko_l1_bridge: # todo: check if its complete
            #     continue
            events: Iterable[EventData] = self.taiko_l1_token_vault_contract.events.ERC20Received().process_receipt(txn_receipt=receipt)
            for event in events:
                if event.get("address") != self.taiko_l1_token_vault:
                    continue
                self.db_token_vault_l1_event_erc20_received.append({
                    "block_id": event.get("blockNumber"),
                    "tx_hash": event.get("transactionHash").hex(),
                    "msg_hash": self.w3.to_hex(event.get("args").get("msgHash")),
                    "tx_from": event.get("args").get("from"),
                    "tx_to": event.get("args").get("to"),
                    "src_chain_id": event.get("args").get("srcChainId"),
                    "token": event.get("args").get("token"),
                    "amount": event.get("args").get("amount"),
                })

    def save_token_vault_l1_event_erc20_received(self):
        count = TokenVaultL1EventERC20Received.select().where(TokenVaultL1EventERC20Received.block_id == self.block_id).count()
        if count != len(self.db_token_vault_l1_event_erc20_received):
            TokenVaultL1EventERC20Received.delete().where(TokenVaultL1EventERC20Received.block_id == self.block_id).execute()
            TokenVaultL1EventERC20Received.insert_many(self.db_token_vault_l1_event_erc20_received).execute()
    
    def get_all_tokens_info(self):
        self.db_erc20_info = []

        result = mysql_db.execute_sql("""
            with token_raw as (
                select token from token_vault_l1_event_erc20_received
                union
                select token from token_vault_l1_event_erc20_sent
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
    
