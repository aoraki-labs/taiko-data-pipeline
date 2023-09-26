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
    L2ContractInfo,
    mysql_db
)

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import requests

# scan one block and save to db
class BlockScanner():
    def __init__(self):
        self.l2_rpc_endpoint = "https://rpc.jolnir.taiko.xyz/"
        self.w3 = Web3(Web3.HTTPProvider(self.l2_rpc_endpoint))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.db_contract_info: list[dict]

    def get_all_contracts_info(self):
        self.db_contract_info = []
        
        result = mysql_db.execute_sql("""
            select distinct lt.tx_to
            from l2_transaction lt
            left join l2_contract_info lc on lc.address = lt.tx_to
            where lt.input != "0x"
            and lt.tx_to is not null
            and lc.address is null
        """).fetchall()

        print(result)

        if not result:
            return

        for tup in result:
            implementation_name = ""
            implementation_address = ""
            (status, contract_name, is_proxy) = self.get_contract_info(tup[0])
            if status == 0:
                contract_name = ""
                is_proxy = False
            if is_proxy:
                implementation_address = self.get_implementation_address(tup[0])
                if implementation_address != "":
                    (_, implementation_name, _) = self.get_contract_info(implementation_address)
            
            self.db_contract_info.append({
                "address": tup[0],
                "name": contract_name,
                "is_proxy": is_proxy,
                "implementation_name": implementation_name,
                "implementation_address": implementation_address
            })

    def save_all_contracts_info(self):
        if self.db_contract_info:
            L2ContractInfo.insert_many(self.db_contract_info).execute()
    
    def get_contract_info(self, address: str):
        x = requests.get('https://blockscoutapi.jolnir.taiko.xyz/api?module=contract&action=getsourcecode&address={0}'.format(address))
        
        if x.status_code != 200:
            return (0, "", False)
        result_json = x.json()
        if "result" not in result_json or "ContractName" not in result_json["result"][0]:
            return (0, "", False)
        return (1, result_json["result"][0]["ContractName"], result_json["result"][0]["IsProxy"])

    def get_implementation_address(self, address):
        implementation_address = ""
        # try get from abi
        proxy_abi = []
        with open(Path(__file__).parent / "proxy_abi.json") as f:
            proxy_abi = json.load(f)

        address = self.w3.to_checksum_address(address)
        contract = self.w3.eth.contract(address=address, abi=proxy_abi)
        try:
            implementation_address = contract.functions.implementation().call()
        except:
            print("get from abi failed")
            try:
                result = self.w3.eth.get_storage_at(address, "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc")
                result = "0x" + self.w3.to_hex(result)[-40:]
                if result == "0x0000000000000000000000000000000000000000":
                    raise
                implementation_address = result
            except:
                print("get from slot failed")
        
        return implementation_address
