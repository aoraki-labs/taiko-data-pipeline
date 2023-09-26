from peewee import MySQLDatabase
from peewee import Model, BigIntegerField, CharField, SmallIntegerField, AutoField, BlobField, DecimalField, BigBitField

class MediumBlogField(BlobField):
    field_type = 'MEDIUMBLOB'

# Connect to a MySQL database on network.
mysql_db = MySQLDatabase(
    database = 'taiko_data_a5',
    user='aaaaaaaa',
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
# event BlockVerified(
#     uint256 indexed blockId, address indexed prover, bytes32 blockHash
# );
class TaikoL1EventBlockVerified(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    log_index    = BigIntegerField(index=True)
    verified_id  = BigIntegerField(index=True)
    prover       = CharField(index=True)
    block_hash   = CharField(index=True)


# event CrossChainSynced(
#     uint64 indexed srcHeight, bytes32 blockHash, bytes32 signalRoot
# );
class TaikoL1EventCrossChainSynced(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    log_index    = BigIntegerField(index=True)
    src_height   = BigIntegerField(index=True)
    block_hash   = CharField(index=True)
    signal_root  = CharField(index=True)
    

# event BlockProposed(
#     uint256 indexed blockId,
#     address indexed prover,
#     uint256 reward,
#     TaikoData.BlockMetadata meta
# );
class TaikoL1EventBlockProposed(BaseModel):
    block_id                = BigIntegerField(index=True)
    tx_hash                 = CharField(index=True)
    log_index               = BigIntegerField(index=True)
    proposer                = CharField(index=True)
    proposed_id             = BigIntegerField(index=True)
    prover                  = CharField(index=True)
    reward                  = BigIntegerField()
    meta_id                 = BigIntegerField()
    meta_timestamp          = BigIntegerField()
    meta_l1_height          = BigIntegerField()
    meta_l1_hash            = CharField()
    meta_mix_hash           = CharField()
    meta_tx_list_hash       = CharField()
    meta_tx_list_byte_start = BigIntegerField()
    meta_tx_list_byte_end   = BigIntegerField()
    meta_gas_limit          = BigIntegerField()
    meta_proposer           = CharField(index=True)


# event BlockProven(
#     uint256 indexed blockId,
#     bytes32 parentHash,
#     bytes32 blockHash,
#     bytes32 signalRoot,
#     address prover
# );
class TaikoL1EventBlockProven(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    proven_id       = BigIntegerField(index=True)
    parent_hash     = CharField(index=True)
    block_hash      = CharField(index=True)
    signal_root     = CharField(index=True)
    prover          = CharField(index=True)
    

# event EthDeposited(TaikoData.EthDeposit deposit);
# struct EthDeposit {
#     address recipient;
#     uint96 amount;
#     uint64 id;
# }
class TaikoL1EventEthDeposited(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    recipient       = CharField(index=True)
    amount          = BigIntegerField()
    id              = BigIntegerField()


# event BondReceived(address indexed from, uint64 blockId, uint256 bond);
class TaikoL1EventBondReceived(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    bond_from       = CharField(index=True)
    bond_block_id   = BigIntegerField(index=True)
    bond_amount     = BigIntegerField()


# event BondReturned(address indexed to, uint64 blockId, uint256 bond);
class TaikoL1EventBondReturned(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    bond_to         = CharField(index=True)
    bond_block_id   = BigIntegerField(index=True)
    bond_amount     = BigIntegerField()


# event BondRewarded(address indexed to, uint64 blockId, uint256 bond);
class TaikoL1EventBondRewarded(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    bond_to         = CharField(index=True)
    bond_block_id   = BigIntegerField(index=True)
    bond_amount     = BigIntegerField()


####################
#  Taiko L1 Calls  
####################
# function proposeBlock(
#     bytes calldata input,
#     bytes calldata assignment,
#     bytes calldata txList
# )
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

# Mint & Burn can be inferred from Transfer from or to zero address.

# event Transfer(address indexed from, address indexed to, uint256 value);
class TaikoTokenL1EventTransfer(BaseModel):
    block_id     = BigIntegerField(index=True)
    tx_hash      = CharField(index=True)
    log_index    = BigIntegerField(index=True)
    tx_from      = CharField(index=True)
    tx_to        = CharField(index=True)
    value        = BigIntegerField()

####################
#  Bridge
####################

# For Ether and ERC20 token receive.
# function processMessage(Message calldata message, bytes calldata proof)
# struct Message {
#     // Message ID.
#     uint256 id;
#     // Message sender address (auto filled).
#     address from;
#     // Source chain ID (auto filled).
#     uint256 srcChainId;
#     // Destination chain ID where the `to` address lives (auto filled).
#     uint256 destChainId;
#     // User address of the bridged asset.
#     address user;
#     // Destination address.
#     address to;
#     // Alternate address to send any refund. If blank, defaults to user.
#     address refundTo;
#     // value to invoke on the destination chain, for ERC20 transfers.
#     uint256 value;
#     // Processing fee for the relayer. Zero if user will process themself.
#     uint256 fee;
#     // gasLimit to invoke on the destination chain, for ERC20 transfers.
#     uint256 gasLimit;
#     // callData to invoke on the destination chain, for ERC20 transfers.
#     bytes data;
#     // Optional memo.
#     string memo;
# }
class BridgeL1CallProcessMessage(BaseModel):
    block_id                = BigIntegerField(index=True)
    tx_hash                 = CharField(index=True)
    message_id              = BigIntegerField()
    message_from            = CharField(index=True)
    message_src_chain_id    = BigIntegerField()
    message_dest_chain_id   = BigIntegerField()
    message_user            = CharField(index=True)
    message_to              = CharField(index=True)
    message_refund_to       = CharField(index=True)
    message_value           = DecimalField(max_digits=64, decimal_places=0)
    message_fee             = DecimalField(max_digits=64, decimal_places=0)
    message_gas_limit       = DecimalField(max_digits=64, decimal_places=0)
    message_data            = CharField() # 0x if ether, else erc20 token
    message_memo            = CharField()
    status                  = SmallIntegerField() # 0 failed, 1 success


# For Ether send.
# function sendMessage(Message calldata message)
# struct Message {
#     // Message ID.
#     uint256 id;
#     // Message sender address (auto filled).
#     address from;
#     // Source chain ID (auto filled).
#     uint256 srcChainId;
#     // Destination chain ID where the `to` address lives (auto filled).
#     uint256 destChainId;
#     // User address of the bridged asset.
#     address user;
#     // Destination address.
#     address to;
#     // Alternate address to send any refund. If blank, defaults to user.
#     address refundTo;
#     // value to invoke on the destination chain, for ERC20 transfers.
#     uint256 value;
#     // Processing fee for the relayer. Zero if user will process themself.
#     uint256 fee;
#     // gasLimit to invoke on the destination chain, for ERC20 transfers.
#     uint256 gasLimit;
#     // callData to invoke on the destination chain, for ERC20 transfers.
#     bytes data;
#     // Optional memo.
#     string memo;
# }
class BridgeL1CallSendMessage(BaseModel):
    block_id                = BigIntegerField(index=True)
    tx_hash                 = CharField(index=True)
    message_id              = BigIntegerField()
    message_from            = CharField(index=True)
    message_src_chain_id    = BigIntegerField()
    message_dest_chain_id   = BigIntegerField()
    message_user            = CharField(index=True)
    message_to              = CharField(index=True)
    message_refund_to       = CharField(index=True)
    message_value           = DecimalField(max_digits=64, decimal_places=0)
    message_fee             = DecimalField(max_digits=64, decimal_places=0)
    message_gas_limit       = DecimalField(max_digits=64, decimal_places=0)
    message_data            = CharField()
    message_memo            = CharField()
    status                  = SmallIntegerField() # 0 failed, 1 success


# event BridgedTokenDeployed(
#     uint256 indexed srcChainId,
#     address indexed ctoken, // CanonicalERC20 data.
#     address indexed btoken, // Address of the deployed bridged token contract.
#     string ctokenSymbol,
#     string ctokenName,
#     uint8 ctokenDecimal
# );
class ERC20VaultL1EventBridgedTokenDeployed(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    src_chain_id    = BigIntegerField(index=True)
    ctoken          = CharField(index=True)
    btoken          = CharField(index=True)
    ctoken_symbol   = CharField(index=True)
    ctoken_name     = CharField(index=True)
    ctoken_decimal  = BigIntegerField()

# event TokenSent(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 destChainId,
#     address token,
#     uint256 amount
# );
class ERC20VaultL1EventTokenSent(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    dest_chain_id   = BigIntegerField(index=True)
    token           = CharField(index=True)
    amount          = BigIntegerField()

# event TokenReleased(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address token,
#     uint256 amount
# );
class ERC20VaultL1EventTokenReleased(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    token           = CharField(index=True)
    amount          = BigIntegerField()

# event TokenReceived(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 srcChainId,
#     address token,
#     uint256 amount
# );
class ERC20VaultL1EventTokenReceived(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    src_chain_id    = BigIntegerField(index=True)
    token           = CharField(index=True)
    amount          = BigIntegerField()

######

# event BridgedTokenDeployed(
#     uint256 indexed chainId,
#     address indexed ctoken,
#     address indexed btoken,
#     string ctokenSymbol,
#     string ctokenName
# );
class ERC721VaultL1EventBridgedTokenDeployed(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    chain_id        = BigIntegerField(index=True)
    ctoken          = CharField(index=True)
    btoken          = CharField(index=True)
    ctoken_symbol   = CharField(index=True)
    ctoken_name     = CharField(index=True)

# event TokenSent(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 destChainId,
#     address token,
#     uint256[] tokenIds,
#     uint256[] amounts
# );
class ERC721VaultL1EventTokenSent(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    dest_chain_id   = BigIntegerField(index=True)
    token           = CharField(index=True)
    token_id        = BigIntegerField(index=True) # Notice: this field is different from the original event
    amount          = BigIntegerField() # Notice: this field is different from the original event

# event TokenReleased(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address token,
#     uint256[] tokenIds,
#     uint256[] amounts
# );
class ERC721VaultL1EventTokenReleased(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    token           = CharField(index=True)
    token_id        = BigIntegerField(index=True) # Notice: this field is different from the original event
    amount          = BigIntegerField() # Notice: this field is different from the original event

# event TokenReceived(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 srcChainId,
#     address token,
#     uint256[] tokenIds,
#     uint256[] amounts
# );
class ERC721VaultL1EventTokenReceived(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    src_chain_id    = BigIntegerField(index=True)
    token_id        = BigIntegerField(index=True) # Notice: this field is different from the original event
    amount          = BigIntegerField() # Notice: this field is different from the original event

######

# event BridgedTokenDeployed(
#     uint256 indexed chainId,
#     address indexed ctoken,
#     address indexed btoken,
#     string ctokenSymbol,
#     string ctokenName
# );
class ERC1155VaultL1EventBridgedTokenDeployed(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    chain_id        = BigIntegerField(index=True)
    ctoken          = CharField(index=True)
    btoken          = CharField(index=True)
    ctoken_symbol   = CharField(index=True)
    ctoken_name     = CharField(index=True)

# event TokenSent(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 destChainId,
#     address token,
#     uint256[] tokenIds,
#     uint256[] amounts
# );
class ERC1155VaultL1EventTokenSent(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    dest_chain_id   = BigIntegerField(index=True)
    token           = CharField(index=True)
    token_id        = BigIntegerField(index=True) # Notice: this field is different from the original event
    amount          = BigIntegerField() # Notice: this field is different from the original event

# event TokenReleased(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address token,
#     uint256[] tokenIds,
#     uint256[] amounts
# );
class ERC1155VaultL1EventTokenReleased(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    token           = CharField(index=True)
    token_id        = BigIntegerField(index=True) # Notice: this field is different from the original event
    amount          = BigIntegerField() # Notice: this field is different from the original event

# event TokenReceived(
#     bytes32 indexed msgHash,
#     address indexed from,
#     address indexed to,
#     uint256 srcChainId,
#     address token,
#     uint256[] tokenIds,
#     uint256[] amounts
# );
class ERC1155VaultL1EventTokenReceived(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    src_chain_id    = BigIntegerField(index=True)
    token_id        = BigIntegerField(index=True) # Notice: this field is different from the original event
    amount          = BigIntegerField() # Notice: this field is different from the original event

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
    TaikoTokenL1EventTransfer,
    BridgeL1CallProcessMessage,
    BridgeL1CallSendMessage,
    TaikoL1EventBondReceived,
    TaikoL1EventBondReturned,
    TaikoL1EventBondRewarded,
    ERC20VaultL1EventBridgedTokenDeployed,
    ERC20VaultL1EventTokenSent,
    ERC20VaultL1EventTokenReleased,
    ERC20VaultL1EventTokenReceived,
    ERC721VaultL1EventBridgedTokenDeployed,
    ERC721VaultL1EventTokenSent,
    ERC721VaultL1EventTokenReleased,
    ERC721VaultL1EventTokenReceived,
    ERC1155VaultL1EventBridgedTokenDeployed,
    ERC1155VaultL1EventTokenSent,
    ERC1155VaultL1EventTokenReleased,
    ERC1155VaultL1EventTokenReceived,
    L1Block,
    L1Transaction,
    ERC20Info
])