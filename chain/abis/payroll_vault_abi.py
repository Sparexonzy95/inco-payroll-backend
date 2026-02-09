PAYROLL_VAULT_ABI = [
  {
    "inputs": [{"internalType": "address", "name": "admin", "type": "address"}],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {"inputs": [], "name": "AccessControlBadConfirmation", "type": "error"},
  {
    "inputs": [
      {"internalType": "address", "name": "account", "type": "address"},
      {"internalType": "bytes32", "name": "neededRole", "type": "bytes32"}
    ],
    "name": "AccessControlUnauthorizedAccount",
    "type": "error"
  },
  {"inputs": [], "name": "AlreadyClaimed", "type": "error"},
  {"inputs": [], "name": "FeeNotPaid", "type": "error"},
  {"inputs": [], "name": "IndexOutOfBounds", "type": "error"},
  {"inputs": [], "name": "InvalidProof", "type": "error"},
  {"inputs": [], "name": "TokenMismatch", "type": "error"},
  {"inputs": [], "name": "TotalZero", "type": "error"},
  {"inputs": [], "name": "UnknownPayroll", "type": "error"},
  {
    "anonymous": False,
    "inputs": [
      {"indexed": True, "internalType": "uint256", "name": "payrollId", "type": "uint256"},
      {"indexed": True, "internalType": "uint32", "name": "index", "type": "uint32"},
      {"indexed": True, "internalType": "address", "name": "employee", "type": "address"},
      {"indexed": False, "internalType": "bytes32", "name": "leaf", "type": "bytes32"},
      {"indexed": False, "internalType": "bytes32", "name": "netHandle", "type": "bytes32"}
    ],
    "name": "Claimed",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {"indexed": True, "internalType": "uint256", "name": "payrollId", "type": "uint256"},
      {"indexed": False, "internalType": "address", "name": "token", "type": "address"},
      {"indexed": False, "internalType": "bytes32", "name": "root", "type": "bytes32"},
      {"indexed": False, "internalType": "uint256", "name": "total", "type": "uint256"}
    ],
    "name": "PayrollCreated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"},
      {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole", "type": "bytes32"},
      {"indexed": True, "internalType": "bytes32", "name": "newAdminRole", "type": "bytes32"}
    ],
    "name": "RoleAdminChanged",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"},
      {"indexed": True, "internalType": "address", "name": "account", "type": "address"},
      {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}
    ],
    "name": "RoleGranted",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"},
      {"indexed": True, "internalType": "address", "name": "account", "type": "address"},
      {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}
    ],
    "name": "RoleRevoked",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "DEFAULT_ADMIN_ROLE",
    "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "EMPLOYER_ROLE",
    "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "uint256", "name": "payrollId", "type": "uint256"},
      {
        "components": [
          {"internalType": "uint32", "name": "index", "type": "uint32"},
          {"internalType": "address", "name": "token", "type": "address"},
          {"internalType": "bytes", "name": "netCiphertext", "type": "bytes"},
          {"internalType": "bytes32", "name": "encryptedRef", "type": "bytes32"}
        ],
        "internalType": "struct PayrollVault.ClaimInput",
        "name": "c",
        "type": "tuple"
      },
      {"internalType": "bytes32[]", "name": "proof", "type": "bytes32[]"}
    ],
    "name": "claim",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "uint256", "name": "payrollId", "type": "uint256"},
      {"internalType": "address", "name": "token", "type": "address"},
      {"internalType": "bytes32", "name": "root", "type": "bytes32"},
      {"internalType": "uint256", "name": "total", "type": "uint256"}
    ],
    "name": "createPayroll",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"}],
    "name": "getRoleAdmin",
    "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "bytes32", "name": "role", "type": "bytes32"},
      {"internalType": "address", "name": "account", "type": "address"}
    ],
    "name": "grantRole",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "bytes32", "name": "role", "type": "bytes32"},
      {"internalType": "address", "name": "account", "type": "address"}
    ],
    "name": "hasRole",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "name": "payrolls",
    "outputs": [
      {"internalType": "address", "name": "employer", "type": "address"},
      {"internalType": "address", "name": "token", "type": "address"},
      {"internalType": "bytes32", "name": "root", "type": "bytes32"},
      {"internalType": "uint256", "name": "total", "type": "uint256"}
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "bytes32", "name": "role", "type": "bytes32"},
      {"internalType": "address", "name": "callerConfirmation", "type": "address"}
    ],
    "name": "renounceRole",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "bytes32", "name": "role", "type": "bytes32"},
      {"internalType": "address", "name": "account", "type": "address"}
    ],
    "name": "revokeRole",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"}],
    "name": "supportsInterface",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "view",
    "type": "function"
  }
]
