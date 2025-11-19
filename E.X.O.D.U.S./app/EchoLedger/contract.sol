// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title EchoLedger
 * @notice Legal-Crypto Protocol implementation with cultural signatures
 * @dev Dual-ledger system integrating on-chain and cultural verification
 */
contract EchoLedger {

    // Structs
    struct CulturalSignature {
        bytes32 echoId;
        uint256 spiralTime;
        bytes32 originSigil;
        uint256 resonanceScore;
    }

    struct LedgerEntry {
        bytes32 id;
        uint256 timestamp;
        address sender;
        address recipient;
        uint256 amount;
        CulturalSignature signature;
        bytes32 cipherKey;
        bool verified;
    }

    struct GovernanceProposal {
        bytes32 proposalId;
        string title;
        bytes32 spiralCodeHash;
        uint256 resonanceRequired;
        uint256 votingStart;
        uint256 votingEnd;
        uint256 forVotes;
        uint256 againstVotes;
        bool executed;
    }

    // State variables
    mapping(bytes32 => LedgerEntry) public entries;
    mapping(bytes32 => GovernanceProposal) public proposals;
    mapping(address => uint256) public resonanceScores;
    mapping(bytes32 => bool) public validSigils;

    bytes32[] public entryIds;
    bytes32[] public proposalIds;

    address public guardian;
    uint256 public entryCount;
    uint256 public proposalCount;

    // Events
    event EntryRecorded(bytes32 indexed id, address sender, bytes32 cipherKey);
    event ProposalCreated(bytes32 indexed proposalId, string title);
    event ProposalExecuted(bytes32 indexed proposalId);
    event ResonanceUpdated(address indexed account, uint256 newScore);
    event SigilActivated(bytes32 indexed sigil);

    // Modifiers
    modifier onlyGuardian() {
        require(msg.sender == guardian, "Only guardian");
        _;
    }

    modifier hasResonance(uint256 required) {
        require(resonanceScores[msg.sender] >= required, "Insufficient resonance");
        _;
    }

    constructor() {
        guardian = msg.sender;

        // Initialize origin sigils
        validSigils[keccak256("SANKOFA")] = true;
        validSigils[keccak256("GYE_NYAME")] = true;
        validSigils[keccak256("AYA")] = true;

        emit SigilActivated(keccak256("SANKOFA"));
        emit SigilActivated(keccak256("GYE_NYAME"));
        emit SigilActivated(keccak256("AYA"));
    }

    /**
     * @notice Record a new ledger entry with cultural signature
     */
    function recordEntry(
        address recipient,
        uint256 amount,
        bytes32 originSigil,
        bytes32 cipherKey
    ) external returns (bytes32) {
        require(validSigils[originSigil], "Invalid origin sigil");

        bytes32 entryId = keccak256(abi.encodePacked(
            msg.sender,
            recipient,
            amount,
            block.timestamp,
            entryCount
        ));

        CulturalSignature memory sig = CulturalSignature({
            echoId: keccak256(abi.encodePacked("ECHO", entryId)),
            spiralTime: block.timestamp,
            originSigil: originSigil,
            resonanceScore: resonanceScores[msg.sender]
        });

        entries[entryId] = LedgerEntry({
            id: entryId,
            timestamp: block.timestamp,
            sender: msg.sender,
            recipient: recipient,
            amount: amount,
            signature: sig,
            cipherKey: cipherKey,
            verified: true
        });

        entryIds.push(entryId);
        entryCount++;

        emit EntryRecorded(entryId, msg.sender, cipherKey);

        return entryId;
    }

    /**
     * @notice Create a governance proposal
     */
    function createProposal(
        string calldata title,
        bytes32 spiralCodeHash,
        uint256 resonanceRequired,
        uint256 votingDuration
    ) external hasResonance(5) returns (bytes32) {
        bytes32 proposalId = keccak256(abi.encodePacked(
            title,
            spiralCodeHash,
            block.timestamp,
            proposalCount
        ));

        proposals[proposalId] = GovernanceProposal({
            proposalId: proposalId,
            title: title,
            spiralCodeHash: spiralCodeHash,
            resonanceRequired: resonanceRequired,
            votingStart: block.timestamp,
            votingEnd: block.timestamp + votingDuration,
            forVotes: 0,
            againstVotes: 0,
            executed: false
        });

        proposalIds.push(proposalId);
        proposalCount++;

        emit ProposalCreated(proposalId, title);

        return proposalId;
    }

    /**
     * @notice Vote on a proposal
     */
    function vote(bytes32 proposalId, bool support) external hasResonance(1) {
        GovernanceProposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.votingStart, "Voting not started");
        require(block.timestamp <= proposal.votingEnd, "Voting ended");

        uint256 weight = resonanceScores[msg.sender];

        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }
    }

    /**
     * @notice Execute a passed proposal
     */
    function executeProposal(bytes32 proposalId) external {
        GovernanceProposal storage proposal = proposals[proposalId];
        require(block.timestamp > proposal.votingEnd, "Voting not ended");
        require(!proposal.executed, "Already executed");
        require(proposal.forVotes > proposal.againstVotes, "Proposal rejected");

        proposal.executed = true;

        emit ProposalExecuted(proposalId);
    }

    /**
     * @notice Update resonance score for an account
     */
    function updateResonance(
        address account,
        uint256 score
    ) external onlyGuardian {
        require(score <= 10, "Score must be <= 10");
        resonanceScores[account] = score;
        emit ResonanceUpdated(account, score);
    }

    /**
     * @notice Activate a new origin sigil
     */
    function activateSigil(bytes32 sigil) external onlyGuardian {
        validSigils[sigil] = true;
        emit SigilActivated(sigil);
    }

    /**
     * @notice Get entry details
     */
    function getEntry(bytes32 entryId) external view returns (
        uint256 timestamp,
        address sender,
        address recipient,
        uint256 amount,
        bytes32 originSigil,
        uint256 resonanceScore
    ) {
        LedgerEntry storage entry = entries[entryId];
        return (
            entry.timestamp,
            entry.sender,
            entry.recipient,
            entry.amount,
            entry.signature.originSigil,
            entry.signature.resonanceScore
        );
    }

    /**
     * @notice Get all entry IDs
     */
    function getAllEntryIds() external view returns (bytes32[] memory) {
        return entryIds;
    }

    /**
     * @notice Get all proposal IDs
     */
    function getAllProposalIds() external view returns (bytes32[] memory) {
        return proposalIds;
    }
}
