from peewee import MySQLDatabase
from peewee import Model, BigIntegerField, CharField, SmallIntegerField, AutoField, BlobField, DecimalField, BigBitField

class MediumBlogField(BlobField):
    field_type = 'MEDIUMBLOB'

# Connect to a MySQL database on network.
mysql_db = MySQLDatabase(
    database = 'taiko_data',
    user='aaaaaa',
    password='bbbbbb',
    host='127.0.0.1', port=3306
)

class BaseModel(Model):
    class Meta:
        database = mysql_db
        legacy_table_names = False

####################
#  Taiko L1 Events  
####################

# event BlockVerified(uint256 indexed id, bytes32 blockHash, uint64 reward);
class TaikoL1EventBlockVerified(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    verified_id  = BigIntegerField(index=True)
    block_hash   = CharField()
    reward       = BigIntegerField()


# event CrossChainSynced(uint256 indexed srcHeight, bytes32 blockHash, bytes32 signalRoot);
class TaikoL1EventCrossChainSynced(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    src_height   = BigIntegerField(index=True)
    block_hash   = CharField()
    signal_root  = CharField()


# event BlockProposed(uint256 indexed id, TaikoData.BlockMetadata meta, uint64 blockFee);
class TaikoL1EventBlockProposed(BaseModel):
    block_id                = BigIntegerField(index=True)
    tx_hash                 = CharField(index=True)
    proposer                = CharField(index=True)
    proposed_id             = BigIntegerField(index=True)
    meta_id                 = BigIntegerField()
    meta_timestamp          = BigIntegerField()
    meta_l1_height          = BigIntegerField()
    meta_l1_hash            = CharField()
    meta_mix_hash           = CharField()
    meta_tx_list_hash       = CharField()
    meta_tx_list_byte_start = BigIntegerField()
    meta_tx_list_byte_end   = BigIntegerField()
    meta_gas_limit          = BigIntegerField()
    meta_beneficiary        = CharField(index=True)
    meta_treasury           = CharField(index=True)
    block_fee               = BigIntegerField()


# event BlockProven(
#     uint256 indexed id,
#     bytes32 parentHash,
#     bytes32 blockHash,
#     bytes32 signalRoot,
#     address prover,
#     uint32 parentGasUsed
# );
class TaikoL1EventBlockProven(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    proven_id       = BigIntegerField(index=True)
    parent_hash     = CharField()
    block_hash      = CharField()
    signal_root     = CharField()
    prover          = CharField(index=True)
    parent_gas_used = BigIntegerField()


# event EthDeposited(TaikoData.EthDeposit deposit);
class TaikoL1EventEthDeposited(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    recipient       = CharField(index=True)
    amount          = BigIntegerField()


####################
#  Taiko L1 Calls  
####################
# function proposeBlock(bytes calldata input, bytes calldata txList)
class TaikoL1CallProposeBlock(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    status       = SmallIntegerField() # 0 failed, 1 success


# function proveBlock(uint256 blockId, bytes calldata input)
class TaikoL1CallProveBlock(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    proven_id    = BigIntegerField(index=True)
    status       = SmallIntegerField() # 0 failed, 1 success


# function verifyBlocks(uint256 maxBlocks)
class TaikoL1CallVerifyBlocks(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    max_blocks   = BigIntegerField()
    status       = SmallIntegerField() # 0 failed, 1 success


# function depositTaikoToken(uint256 amount)
class TaikoL1CallDepositTaikoToken(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    amount       = BigIntegerField()
    status       = SmallIntegerField() # 0 failed, 1 success


# function withdrawTaikoToken(uint256 amount)
class TaikoL1CallWithdrawTaikoToken(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    amount       = BigIntegerField()
    status       = SmallIntegerField() # 0 failed, 1 success


# function depositEtherToL2()
# temporarily not needed, TaikoL1EventEthDeposited is enough


####################
#  Taiko Token(TKO)
####################

# event Mint(address account, uint256 amount);
class TaikoTokenL1EventMint(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    account      = CharField(index=True)
    amount       = BigIntegerField()


# event Burn(address account, uint256 amount);
class TaikoTokenL1EventBurn(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    account      = CharField(index=True)
    amount       = BigIntegerField()


# event Transfer(address indexed from, address indexed to, uint256 value);
class TaikoTokenL1EventTransfer(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    tx_from      = CharField(index=True)
    tx_to        = CharField(index=True)
    value        = BigIntegerField()

####################
#  Bridge
####################

# For Ether and ERC20 token receive.
# function processMessage(Message calldata message, bytes calldata proof)
class BridgeL1CallProcessMessage(BaseModel):
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
class BridgeL1CallSendMessage(BaseModel):
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
class TokenVaultL1EventERC20Sent(BaseModel):
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
class TokenVaultL1EventERC20Received(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    src_chain_id    = BigIntegerField()
    token           = CharField(index=True)
    amount          = BigIntegerField()


# # Reward balance is not needed any more. Use block reward to aggregate balances.
# # reward balance
# class RewardBalance(BaseModel):
#     address      = CharField(index=True, unique=True)
#     reward       = DecimalField(max_digits=64, decimal_places=0)

####################
#  L1 Basic Data
####################
# l1 blocks
class L1Block(BaseModel):
    block_id      = BigIntegerField(index=True, unique=True)
    block_hash    = CharField(index=True)
    parent_hash   = CharField()
    timestamp     = BigIntegerField(index=True)
    taiko_txs_num = BigIntegerField()


# l1 transactions
class L1Transaction(BaseModel):
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

# token for L2 & L1
class ERC20Info(BaseModel):
    chain_id = BigIntegerField(index=True)
    address  = CharField(index=True)
    name     = CharField(index=True)
    symbol   = CharField(index=True)
    decimal  = BigIntegerField()

# Connect to our database.
mysql_db.connect()

# Create the tables if not exist.
mysql_db.create_tables([
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
    BridgeL1CallProcessMessage,
    BridgeL1CallSendMessage,
    TokenVaultL1EventERC20Sent,
    TokenVaultL1EventERC20Received,
    L1Block,
    L1Transaction,
    ERC20Info
])