from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware
import datetime
from peewee import fn
import sys

# change this!!
from .schema import L1Block
from .block_scanner import BlockScanner

import datetime

class TaskManager:
    def __init__(self):
        self.now = datetime.datetime.now()
        self.l1_rpc_endpoint = ""
        if self.now.hour % 2 == 0:
            self.l1_rpc_endpoint = "https://l1rpc.jolnir.taiko.xyz/"
        else:
            self.l1_rpc_endpoint = "https://l1rpc.jolnir.taiko.xyz/"
        self.w3 = Web3(Web3.HTTPProvider(self.l1_rpc_endpoint))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.genesis_on_l1 = 4272650
        self.scanner = BlockScanner()

    def get_latest_block(self):
        block = self.w3.eth.block_number
        return block

    def get_last_block_processed(self):
        result = L1Block.select(L1Block.block_id).order_by(L1Block.block_id.desc()).limit(1).scalar()
        if not result:
            return self.genesis_on_l1
        else:
            return max(result, self.genesis_on_l1)

    def run_one_block(self, block_id: int):
        self.scanner.set_block_id(block_id)
        self.scanner.fetch_data()
        self.scanner.parse_txs()
        self.scanner.parse_l1_call_propose_block()
        self.scanner.parse_l1_call_prove_block()
        self.scanner.parse_l1_call_verify_blocks()
        self.scanner.parse_l1_call_deposit_taiko_token()
        self.scanner.parse_l1_call_withdraw_taiko_token()
        self.scanner.parse_l1_event_block_proposed()
        self.scanner.parse_l1_event_block_proven()
        self.scanner.parse_l1_event_block_verified()
        self.scanner.parse_l1_event_cross_chain_synced()
        self.scanner.parse_l1_event_eth_deposited()
        self.scanner.parse_taiko_token_event_transfer()
        self.scanner.parse_bridge_l1_call_send_message()
        self.scanner.parse_bridge_l1_call_process_message()
        self.scanner.parse_erc20_vault_l1_event_bridged_token_deployed()
        self.scanner.parse_erc20_vault_l1_event_token_sent()
        self.scanner.parse_erc20_vault_l1_event_token_released()
        self.scanner.parse_erc20_vault_l1_event_token_received()
        self.scanner.parse_erc721_vault_l1_event_bridged_token_deployed()
        self.scanner.parse_erc721_vault_l1_event_token_sent()
        self.scanner.parse_erc721_vault_l1_event_token_released()
        self.scanner.parse_erc721_vault_l1_event_token_received()
        self.scanner.parse_erc1155_vault_l1_event_bridged_token_deployed()
        self.scanner.parse_erc1155_vault_l1_event_token_sent()
        self.scanner.parse_erc1155_vault_l1_event_token_released()
        self.scanner.parse_erc1155_vault_l1_event_token_received()
        self.scanner.parse_taiko_l1_event_bond_received()
        self.scanner.parse_taiko_l1_event_bond_returned()
        self.scanner.parse_taiko_l1_event_bond_rewarded()
        self.scanner.get_all_tokens_info()
        self.scanner.save_l1_call_propose_block()
        self.scanner.save_l1_call_prove_block()
        self.scanner.save_l1_call_verify_blocks()
        self.scanner.save_l1_call_deposit_taiko_token()
        self.scanner.save_l1_call_withdraw_taiko_token()
        self.scanner.save_l1_event_block_proposed()
        self.scanner.save_l1_event_block_proven()
        self.scanner.save_l1_event_block_verified()
        self.scanner.save_l1_event_cross_chain_synced()
        self.scanner.save_l1_event_eth_deposited()
        self.scanner.save_taiko_token_event_transfer()
        self.scanner.save_bridge_l1_call_send_message()
        self.scanner.save_bridge_l1_call_process_message()
        self.scanner.save_erc20_vault_l1_event_bridged_token_deployed()
        self.scanner.save_erc20_vault_l1_event_token_sent()
        self.scanner.save_erc20_vault_l1_event_token_released()
        self.scanner.save_erc20_vault_l1_event_token_received()
        self.scanner.save_erc721_vault_l1_event_bridged_token_deployed()
        self.scanner.save_erc721_vault_l1_event_token_sent()
        self.scanner.save_erc721_vault_l1_event_token_released()
        self.scanner.save_erc721_vault_l1_event_token_received()
        self.scanner.save_erc1155_vault_l1_event_bridged_token_deployed()
        self.scanner.save_erc1155_vault_l1_event_token_sent()
        self.scanner.save_erc1155_vault_l1_event_token_released()
        self.scanner.save_erc1155_vault_l1_event_token_received()
        self.scanner.save_taiko_l1_event_bond_received()
        self.scanner.save_taiko_l1_event_bond_returned()
        self.scanner.save_taiko_l1_event_bond_rewarded()
        self.scanner.save_all_tokens_info()
        self.scanner.save_txs()
        self.scanner.save_block()

    def run(self):
        print(datetime.datetime.now())
        start = self.get_last_block_processed() + 1
        end = self.get_latest_block()
        block_id = start
        print(f"start {start} end {end}")
        try:
            while block_id <= end:
                self.run_one_block(block_id)
                print(f"block_id {block_id} finished")
                block_id += 1
        except Exception as e:
            if "not found" in str(e):
                print(str(e))
            else:
                raise
        print(datetime.datetime.now())
    
    def run_manual(self, start, end):
        print(datetime.datetime.now())
        block_id = start
        end = min(self.get_latest_block(), end)
        while block_id <= end:
            self.run_one_block(block_id)
            print(f"block_id {block_id} finished")
            block_id += 1
        print(datetime.datetime.now())


if __name__ == "__main__":
    task_manager = TaskManager()
    if len(sys.argv) == 3:
        print(sys.argv[1])
        print(sys.argv[2])
        start = int(sys.argv[1])
        end = int(sys.argv[2])
        task_manager.run_manual(start, end)
    else:
        task_manager.run()
    
