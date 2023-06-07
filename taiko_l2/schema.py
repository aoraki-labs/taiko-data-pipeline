from peewee import MySQLDatabase
from peewee import Model, BigIntegerField, CharField, SmallIntegerField, BlobField, DecimalField

class MediumBlogField(BlobField):
    field_type = 'MEDIUMBLOB'

# Connect to a MySQL database on network.
mysql_db = MySQLDatabase(
    database = 'taiko_data',
    user='aaaaaaa',
    password='bbbbbb',
    host='127.0.0.1', port=3306
)

class BaseModel(Model):
    class Meta:
        database = mysql_db
        legacy_table_names = False

####################
#  L2 Basic Data
####################
# l2 blocks
class L2Block(BaseModel):
    block_id         = BigIntegerField(index=True, unique=True)
    block_hash       = CharField(index=True)
    parent_hash      = CharField()
    timestamp        = BigIntegerField(index=True)
    base_fee_per_gas = DecimalField(max_digits=64, decimal_places=0)
    gas_used         = DecimalField(max_digits=64, decimal_places=0)
    txs_num          = BigIntegerField()


# l2 transactions
# ** for contract creation: tx_to is None, contract_address is not None
class L2Transaction(BaseModel):
    block_id            = BigIntegerField(index=True)
    tx_hash             = CharField(index=True, unique=True)
    tx_from             = CharField(index=True)
    tx_to               = CharField(index=True, null=True)
    input               = CharField()
    value               = DecimalField(max_digits=64, decimal_places=0)
    gas_used            = DecimalField(max_digits=64, decimal_places=0)
    # baseFeePerGas + maxPriorityFeePerGas, say 1500000000 + 7
    gas_price           = DecimalField(max_digits=64, decimal_places=0)
    nonce               = BigIntegerField()
    status              = SmallIntegerField()
    transaction_index   = SmallIntegerField()
    timestamp           = BigIntegerField(index=True)
    contract_address    = CharField(index=True, null=True)

####################
#  Bridge
####################

# For Ether and ERC20 token receive.
# function processMessage(Message calldata message, bytes calldata proof)
class BridgeL2CallProcessMessage(BaseModel):
    block_id                = BigIntegerField(index=True)
    tx_hash                 = CharField(index=True)
    message_id              = BigIntegerField()
    message_sender          = CharField(index=True)
    message_src_chain_id    = BigIntegerField()
    message_dest_chain_id   = BigIntegerField()
    message_owner           = CharField(index=True)
    message_to              = CharField(index=True)
    message_refund_address  = CharField(index=True)
    message_deposit_value   = DecimalField(max_digits=64, decimal_places=0)
    message_call_value      = DecimalField(max_digits=64, decimal_places=0)
    message_processing_fee  = DecimalField(max_digits=64, decimal_places=0)
    message_gas_limit       = DecimalField(max_digits=64, decimal_places=0)
    message_data            = CharField() # 0x if ether, else erc20 token
    message_memo            = CharField()
    status                  = SmallIntegerField() # 0 failed, 1 success


# For Ether send.
# function sendMessage(Message calldata message)
class BridgeL2CallSendMessage(BaseModel):
    block_id                = BigIntegerField(index=True)
    tx_hash                 = CharField(index=True)
    message_id              = BigIntegerField()
    message_sender          = CharField(index=True)
    message_src_chain_id    = BigIntegerField()
    message_dest_chain_id   = BigIntegerField()
    message_owner           = CharField(index=True)
    message_to              = CharField(index=True)
    message_refund_address  = CharField(index=True)
    message_deposit_value   = DecimalField(max_digits=64, decimal_places=0)
    message_call_value      = DecimalField(max_digits=64, decimal_places=0)
    message_processing_fee  = DecimalField(max_digits=64, decimal_places=0)
    message_gas_limit       = DecimalField(max_digits=64, decimal_places=0)
    message_data            = CharField()
    message_memo            = CharField()
    status                  = SmallIntegerField() # 0 failed, 1 success


# For ERC20 send.
# event ERC20Sent(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 destChainId,
#     address token,
#     uint256 amount
# );
class TokenVaultL2EventERC20Sent(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    dest_chain_id   = BigIntegerField()
    token           = CharField(index=True)
    amount          = BigIntegerField()


# For ERC20 receive.
# event ERC20Received(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 srcChainId,
#     address token,
#     uint256 amount
# );
class TokenVaultL2EventERC20Received(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    src_chain_id    = BigIntegerField()
    token           = CharField(index=True)
    amount          = BigIntegerField()

# token for L2 & L1
class ERC20Info(BaseModel):
    chain_id = BigIntegerField(index=True)
    address  = CharField(index=True)
    name     = CharField(index=True)
    symbol   = CharField(index=True)
    decimal  = BigIntegerField()

class L2ContractInfo(BaseModel):
    address  = CharField(index=True)
    name     = CharField(index=True)
    is_proxy = CharField(index=True)


# Connect to our database.
mysql_db.connect()

# Create the tables if not exist.
mysql_db.create_tables([
    L2Block,
    L2Transaction,
    BridgeL2CallProcessMessage,
    BridgeL2CallSendMessage,
    TokenVaultL2EventERC20Sent,
    TokenVaultL2EventERC20Received,
    ERC20Info,
    L2ContractInfo
])