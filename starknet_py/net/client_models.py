from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Union

from typing_extensions import Literal

from starknet_py.abi.shape import AbiDictList

Hash = Union[int, str]
Tag = Literal["pending", "latest"]


@dataclass
class Call:
    to_addr: int
    selector: int
    calldata: List[int]


Calls = Union[Call, Iterable[Call]]


@dataclass
class Event:
    """
    Dataclass representing an event emitted by transaction
    """

    from_address: int
    keys: List[int]
    data: List[int]


@dataclass
class L1toL2Message:
    """
    Dataclass representing a L1->L2 message
    """

    payload: List[int]
    l1_address: int
    l2_address: Optional[int] = None


@dataclass
class L2toL1Message:
    """
    Dataclass representing a L2->L1 message
    """

    payload: List[int]
    l1_address: int
    l2_address: Optional[int] = None


class TransactionType(Enum):
    """
    Enum representing transaction types
    """

    INVOKE = "INVOKE"
    DEPLOY = "DEPLOY"
    DECLARE = "DECLARE"
    DEPLOY_ACCOUNT = "DEPLOY_ACCOUNT"
    L1_HANDLER = "L1_HANDLER"


@dataclass
class Transaction(ABC):
    """
    Dataclass representing common attributes of all transactions
    """

    hash: int
    signature: List[int]
    max_fee: int
    version: int

    def __post_init__(self):
        if self.__class__ == Transaction:
            raise TypeError("Cannot instantiate abstract Transaction class.")


@dataclass
class InvokeTransaction(Transaction):
    """
    Dataclass representing invoke transaction
    """

    contract_address: int
    calldata: List[int]
    # This field is always None for transactions with version = 1
    entry_point_selector: Optional[int] = None
    nonce: Optional[int] = None


@dataclass
class DeclareTransaction(Transaction):
    """
    Dataclass representing declare transaction
    """

    class_hash: int
    sender_address: int
    nonce: Optional[int] = None


@dataclass
class DeployTransaction(Transaction):
    """
    Dataclass representing deploy transaction
    """

    contract_address: Optional[int]
    constructor_calldata: List[int]
    class_hash: int


@dataclass
class DeployAccountTransaction(Transaction):
    """
    Dataclass representing deploy account transaction
    """

    contract_address_salt: int
    class_hash: int
    constructor_calldata: List[int]
    nonce: int


@dataclass
class L1HandlerTransaction(Transaction):
    """
    Dataclass representing l1 handler transaction
    """

    contract_address: int
    calldata: List[int]
    entry_point_selector: int
    nonce: Optional[int] = None


class TransactionStatus(Enum):
    """
    Enum representing transaction statuses
    """

    NOT_RECEIVED = "NOT_RECEIVED"
    RECEIVED = "RECEIVED"
    PENDING = "PENDING"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    REJECTED = "REJECTED"


@dataclass
class TransactionReceipt:
    """
    Dataclass representing details of sent transaction
    """

    # pylint: disable=too-many-instance-attributes

    hash: int
    status: TransactionStatus
    block_number: Optional[int] = None
    block_hash: Optional[int] = None
    actual_fee: int = 0
    rejection_reason: Optional[str] = None

    events: List[Event] = field(default_factory=list)
    l2_to_l1_messages: List[L2toL1Message] = field(default_factory=list)
    l1_to_l2_consumed_message: Optional[L1toL2Message] = None


@dataclass
class SentTransactionResponse:
    """
    Dataclass representing a result of sending a transaction to Starknet.
    """

    transaction_hash: int
    code: Optional[str] = None


@dataclass
class DeclareTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of declaring a contract on Starknet.
    """

    class_hash: int = 0


@dataclass
class DeployAccountTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of deploying an account contract to Starknet
    """

    address: int = 0


class BlockStatus(Enum):
    """
    Enum representing block status
    """

    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    PROVEN = "PROVEN"


@dataclass
class StarknetBlock:
    """
    Dataclass representing a block on Starknet.
    """

    # pylint: disable=too-many-instance-attributes

    block_hash: int
    parent_block_hash: int
    block_number: int
    status: BlockStatus
    root: int
    transactions: List[Transaction]
    timestamp: int


@dataclass
class GatewayBlock(StarknetBlock):
    """
    Dataclass representing a block from the Starknet gateway.
    """

    gas_price: int


@dataclass
class BlockSingleTransactionTrace:
    signature: List[int]
    transaction_hash: int
    function_invocation: Optional[dict] = None
    validate_invocation: Optional[dict] = None
    fee_transfer_invocation: Optional[dict] = None


@dataclass
class BlockTransactionTraces:
    traces: List[BlockSingleTransactionTrace]


@dataclass
class StorageEntry:
    key: int
    value: int


@dataclass
class StorageDiffItem:
    address: int
    storage_entries: List[StorageEntry]


@dataclass
class EstimatedFee:
    overall_fee: int
    gas_price: int
    gas_usage: int


@dataclass
class DeployedContract:
    address: int
    class_hash: int


@dataclass
class ContractsNonce:
    contract_address: int
    nonce: int


@dataclass
class StateDiff:
    deployed_contracts: List[DeployedContract]
    declared_contract_hashes: List[int]
    storage_diffs: List[StorageDiffItem]
    nonces: List[ContractsNonce]


@dataclass
class BlockStateUpdate:
    """
    Dataclass representing a change in state of a block
    """

    block_hash: int
    new_root: int
    old_root: int
    state_diff: StateDiff


@dataclass
class ContractCode:
    """
    Dataclass representing contract deployed to Starknet.
    """

    bytecode: List[int]
    abi: List[Dict[str, Any]]


@dataclass
class EntryPoint:
    """
    Dataclass representing contract entry point
    """

    offset: int
    selector: int


@dataclass
class EntryPointsByType:
    """
    Dataclass representing contract class entrypoints by entry point type
    """

    constructor: List[EntryPoint]
    external: List[EntryPoint]
    l1_handler: List[EntryPoint]


@dataclass
class ContractClass:
    """
    Dataclass representing contract declared to Starknet
    """

    program: dict
    entry_points_by_type: EntryPointsByType
    abi: Optional[AbiDictList] = None


@dataclass
class CompiledContract(ContractClass):
    """
    Dataclass representing ContractClass with required abi.
    """

    # abi is a required key in CompiledContractSchema,
    # default_factory is used, since abi in ContractClass is Optional
    # and otherwise, non-keyword arguments would follow keyword arguments
    abi: AbiDictList = field(default_factory=list)


@dataclass
class TransactionStatusResponse:
    block_hash: Optional[int]
    transaction_status: TransactionStatus
