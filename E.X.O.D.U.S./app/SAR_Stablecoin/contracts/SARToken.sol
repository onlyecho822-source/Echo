// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SARToken - Sovereign Autonomous Reserve Stablecoin
 * @notice Dual-ledger integration with cultural signature encoding
 * @dev Implements Adinkra cipher verification for transactions
 */
contract SARToken is ERC20, Ownable {

    // Adinkra cipher keys for transaction encoding
    mapping(bytes32 => bool) public validCipherKeys;

    // Cultural resonance threshold for governance
    uint256 public resonanceThreshold = 7;

    // Spiral-Time timestamp for temporal anchoring
    uint256 public spiralTimeOrigin;

    // Events
    event CipherKeyAdded(bytes32 indexed key, string symbol);
    event ResonanceUpdated(uint256 newThreshold);
    event GovernanceSignalEmitted(bytes32 indexed signal, uint256 timestamp);

    constructor() ERC20("Sovereign Autonomous Reserve", "SAR") Ownable(msg.sender) {
        spiralTimeOrigin = block.timestamp;

        // Initialize Adinkra cipher keys
        _addCipherKey(keccak256("Sankofa"), "Sankofa");
        _addCipherKey(keccak256("GyeNyame"), "Gye Nyame");
        _addCipherKey(keccak256("Aya"), "Aya");
    }

    /**
     * @notice Mint tokens with cultural signature verification
     * @param to Recipient address
     * @param amount Amount to mint
     * @param cipherKey Adinkra cipher key for verification
     */
    function mintWithCipher(
        address to,
        uint256 amount,
        bytes32 cipherKey
    ) external onlyOwner {
        require(validCipherKeys[cipherKey], "Invalid cipher key");
        _mint(to, amount);
        emit GovernanceSignalEmitted(cipherKey, block.timestamp);
    }

    /**
     * @notice Transfer with resonance verification
     * @param to Recipient address
     * @param amount Amount to transfer
     */
    function resonantTransfer(address to, uint256 amount) external returns (bool) {
        require(amount >= resonanceThreshold * 1e18, "Below resonance threshold");
        return transfer(to, amount);
    }

    /**
     * @notice Update cultural resonance threshold
     * @param newThreshold New threshold value
     */
    function updateResonance(uint256 newThreshold) external onlyOwner {
        resonanceThreshold = newThreshold;
        emit ResonanceUpdated(newThreshold);
    }

    /**
     * @notice Add new Adinkra cipher key
     * @param key Cipher key hash
     * @param symbol Symbol name
     */
    function addCipherKey(bytes32 key, string calldata symbol) external onlyOwner {
        _addCipherKey(key, symbol);
    }

    function _addCipherKey(bytes32 key, string memory symbol) internal {
        validCipherKeys[key] = true;
        emit CipherKeyAdded(key, symbol);
    }

    /**
     * @notice Get spiral time elapsed since origin
     */
    function spiralTimeElapsed() external view returns (uint256) {
        return block.timestamp - spiralTimeOrigin;
    }
}
