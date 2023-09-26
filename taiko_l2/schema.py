from peewee import MySQLDatabase
from peewee import Model, BigIntegerField, CharField, SmallIntegerField, BlobField, DecimalField

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
    transaction_index   = SmallIntegerField(index=True)
    timestamp           = BigIntegerField(index=True)
    contract_address    = CharField(index=True, null=True)

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
class BridgeL2CallProcessMessage(BaseModel):
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
class BridgeL2CallSendMessage(BaseModel):
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
class ERC20VaultL2EventBridgedTokenDeployed(BaseModel):
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
class ERC20VaultL2EventTokenSent(BaseModel):
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
class ERC20VaultL2EventTokenReleased(BaseModel):
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
class ERC20VaultL2EventTokenReceived(BaseModel):
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
class ERC721VaultL2EventBridgedTokenDeployed(BaseModel):
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
class ERC721VaultL2EventTokenSent(BaseModel):
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
class ERC721VaultL2EventTokenReleased(BaseModel):
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
class ERC721VaultL2EventTokenReceived(BaseModel):
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
class ERC1155VaultL2EventBridgedTokenDeployed(BaseModel):
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
class ERC1155VaultL2EventTokenSent(BaseModel):
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
class ERC1155VaultL2EventTokenReleased(BaseModel):
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
class ERC1155VaultL2EventTokenReceived(BaseModel):
    block_id        = BigIntegerField(index=True)
    tx_hash         = CharField(index=True)
    log_index       = BigIntegerField(index=True)
    msg_hash        = CharField(index=True)
    tx_from         = CharField(index=True)
    tx_to           = CharField(index=True)
    src_chain_id    = BigIntegerField(index=True)
    token_id        = BigIntegerField(index=True) # Notice: this field is different from the original event
    amount          = BigIntegerField() # Notice: this field is different from the original event

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
    L2Block,
    L2Transaction,
    BridgeL2CallProcessMessage,
    BridgeL2CallSendMessage,
    ERC20VaultL2EventBridgedTokenDeployed,
    ERC20VaultL2EventTokenSent,
    ERC20VaultL2EventTokenReleased,
    ERC20VaultL2EventTokenReceived,
    ERC721VaultL2EventBridgedTokenDeployed,
    ERC721VaultL2EventTokenSent,
    ERC721VaultL2EventTokenReleased,
    ERC721VaultL2EventTokenReceived,
    ERC1155VaultL2EventBridgedTokenDeployed,
    ERC1155VaultL2EventTokenSent,
    ERC1155VaultL2EventTokenReleased,
    ERC1155VaultL2EventTokenReceived,
    ERC20Info
])