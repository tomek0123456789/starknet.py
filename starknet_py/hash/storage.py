from functools import reduce

from starknet_py.constants import ADDR_BOUND
from starknet_py.hash.utils import _starknet_keccak, pedersen_hash


def get_storage_var_address(var_name: str, *args: int) -> int:
    """
    Returns the storage address of a StarkNet storage variable given its name and arguments.
    """
    res = _starknet_keccak(var_name.encode("ascii"))
    return reduce(pedersen_hash, args, res) % ADDR_BOUND
