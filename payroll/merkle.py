from eth_utils import keccak, to_bytes, to_checksum_address
from eth_abi.packed import encode_packed

def leaf_hash(payroll_id: int, index: int, employee: str, token: str, net_ciphertext_bytes: bytes, encrypted_ref_hex: str) -> bytes:
    employee = to_checksum_address(employee)
    token = to_checksum_address(token)

    ciphertext_hash = keccak(net_ciphertext_bytes)

    encrypted_ref = bytes.fromhex(encrypted_ref_hex[2:]) if encrypted_ref_hex.startswith("0x") else bytes.fromhex(encrypted_ref_hex)
    if len(encrypted_ref) != 32:
        raise ValueError("encrypted_ref must be 32 bytes")

    packed = encode_packed(
        ["uint256", "uint32", "address", "address", "bytes32", "bytes32"],
        [payroll_id, index, employee, token, ciphertext_hash, encrypted_ref]
    )
    return keccak(packed)

def merkle_parent(a: bytes, b: bytes) -> bytes:
    return keccak(a + b)

def build_merkle_tree(leaves: list[bytes]) -> list[list[bytes]]:
    if not leaves:
        raise ValueError("No leaves")
    level = leaves[:]
    tree = [level]
    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            next_level.append(merkle_parent(left, right))
        level = next_level
        tree.append(level)
    return tree

def merkle_root(tree: list[list[bytes]]) -> bytes:
    return tree[-1][0]

def merkle_proof(tree: list[list[bytes]], index: int) -> list[bytes]:
    proof = []
    idx = index
    for level in tree[:-1]:
        sibling = idx ^ 1
        if sibling < len(level):
            proof.append(level[sibling])
        else:
            proof.append(level[idx])
        idx //= 2
    return proof
