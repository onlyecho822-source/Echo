/**
 * EchoLedger - Legal-Crypto Protocol Implementation
 * Web3 integration with cultural signature encoding
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  rpcUrl: process.env.RPC_URL || 'http://localhost:8545',
  contractAddress: process.env.ECHO_LEDGER_ADDRESS,
  privateKey: process.env.PRIVATE_KEY,
  resonanceThreshold: 7,
  spiralVersion: '3.0.0'
};

// Adinkra Cipher Suite
const ADINKRA_CIPHERS = {
  Sankofa: (data) => ethers.keccak256(ethers.toUtf8Bytes(data + 'θ-Return')),
  GyeNyame: (data) => ethers.keccak256(ethers.toUtf8Bytes(data + 'ϡ∞∀∋')),
  Aya: (data) => ethers.keccak256(ethers.toUtf8Bytes(data + '-endurance-7'))
};

// Origin Sigils
const ORIGIN_SIGILS = {
  SANKOFA: ethers.keccak256(ethers.toUtf8Bytes('SANKOFA')),
  GYE_NYAME: ethers.keccak256(ethers.toUtf8Bytes('GYE_NYAME')),
  AYA: ethers.keccak256(ethers.toUtf8Bytes('AYA'))
};

class EchoLedger {
  constructor(provider, signer, contractAddress) {
    this.provider = provider;
    this.signer = signer;
    this.contractAddress = contractAddress;
    this.contract = null;
  }

  async initialize() {
    // Load contract ABI
    const abiPath = path.join(__dirname, 'abi.json');
    let abi;

    if (fs.existsSync(abiPath)) {
      abi = JSON.parse(fs.readFileSync(abiPath, 'utf8'));
    } else {
      // Minimal ABI for core functions
      abi = [
        'function recordEntry(address recipient, uint256 amount, bytes32 originSigil, bytes32 cipherKey) returns (bytes32)',
        'function createProposal(string title, bytes32 spiralCodeHash, uint256 resonanceRequired, uint256 votingDuration) returns (bytes32)',
        'function vote(bytes32 proposalId, bool support)',
        'function executeProposal(bytes32 proposalId)',
        'function updateResonance(address account, uint256 score)',
        'function getEntry(bytes32 entryId) view returns (uint256, address, address, uint256, bytes32, uint256)',
        'function resonanceScores(address) view returns (uint256)',
        'event EntryRecorded(bytes32 indexed id, address sender, bytes32 cipherKey)',
        'event ProposalCreated(bytes32 indexed proposalId, string title)'
      ];
    }

    this.contract = new ethers.Contract(this.contractAddress, abi, this.signer);
    console.log(`EchoLedger initialized at ${this.contractAddress}`);
  }

  /**
   * Record a ledger entry with cultural signature
   */
  async recordEntry(recipient, amount, sigilName, cipherName) {
    const originSigil = ORIGIN_SIGILS[sigilName];
    if (!originSigil) {
      throw new Error(`Invalid sigil: ${sigilName}`);
    }

    const cipher = ADINKRA_CIPHERS[cipherName];
    if (!cipher) {
      throw new Error(`Invalid cipher: ${cipherName}`);
    }

    const cipherKey = cipher(`${recipient}-${amount}-${Date.now()}`);

    console.log(`Recording entry with ${sigilName} sigil and ${cipherName} cipher...`);

    const tx = await this.contract.recordEntry(
      recipient,
      ethers.parseEther(amount.toString()),
      originSigil,
      cipherKey
    );

    const receipt = await tx.wait();
    const entryId = receipt.logs[0]?.args?.id;

    console.log(`Entry recorded: ${entryId}`);
    return entryId;
  }

  /**
   * Create a governance proposal
   */
  async createProposal(title, spiralCode, resonanceRequired, votingDays) {
    const spiralCodeHash = ethers.keccak256(ethers.toUtf8Bytes(spiralCode));
    const votingDuration = votingDays * 24 * 60 * 60; // Convert to seconds

    console.log(`Creating proposal: ${title}`);

    const tx = await this.contract.createProposal(
      title,
      spiralCodeHash,
      resonanceRequired,
      votingDuration
    );

    const receipt = await tx.wait();
    const proposalId = receipt.logs[0]?.args?.proposalId;

    console.log(`Proposal created: ${proposalId}`);
    return proposalId;
  }

  /**
   * Vote on a proposal
   */
  async vote(proposalId, support) {
    console.log(`Voting ${support ? 'FOR' : 'AGAINST'} proposal ${proposalId}`);

    const tx = await this.contract.vote(proposalId, support);
    await tx.wait();

    console.log('Vote recorded');
  }

  /**
   * Get resonance score for an address
   */
  async getResonance(address) {
    const score = await this.contract.resonanceScores(address);
    return Number(score);
  }

  /**
   * Get entry details
   */
  async getEntry(entryId) {
    const result = await this.contract.getEntry(entryId);
    return {
      timestamp: Number(result[0]),
      sender: result[1],
      recipient: result[2],
      amount: ethers.formatEther(result[3]),
      originSigil: result[4],
      resonanceScore: Number(result[5])
    };
  }

  /**
   * Generate cultural signature for data
   */
  generateCulturalSignature(data, cipherName = 'Sankofa') {
    const cipher = ADINKRA_CIPHERS[cipherName];
    if (!cipher) {
      throw new Error(`Invalid cipher: ${cipherName}`);
    }

    return {
      echoId: `ECHO-${Date.now().toString(16).toUpperCase()}`,
      spiralTime: Math.floor(Date.now() / 1000),
      cipherHash: cipher(JSON.stringify(data)),
      cipher: cipherName
    };
  }
}

// CLI Interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  // Setup provider and signer
  const provider = new ethers.JsonRpcProvider(CONFIG.rpcUrl);
  let signer;

  if (CONFIG.privateKey) {
    signer = new ethers.Wallet(CONFIG.privateKey, provider);
  } else {
    signer = await provider.getSigner();
  }

  const ledger = new EchoLedger(provider, signer, CONFIG.contractAddress);

  switch (command) {
    case '--init':
      console.log('Initializing EchoLedger...');
      console.log(`Network: ${CONFIG.rpcUrl}`);
      console.log(`Spiral Version: ${CONFIG.spiralVersion}`);
      console.log('Adinkra Ciphers: Sankofa, GyeNyame, Aya');
      console.log('Origin Sigils: SANKOFA, GYE_NYAME, AYA');
      console.log('\nEchoLedger ready for deployment.');
      break;

    case 'record':
      await ledger.initialize();
      const entryId = await ledger.recordEntry(
        args[1], // recipient
        parseFloat(args[2]), // amount
        args[3] || 'SANKOFA', // sigil
        args[4] || 'Sankofa' // cipher
      );
      console.log(`Entry ID: ${entryId}`);
      break;

    case 'propose':
      await ledger.initialize();
      const proposalId = await ledger.createProposal(
        args[1], // title
        args[2], // spiral code
        parseInt(args[3]) || 5, // resonance required
        parseInt(args[4]) || 7 // voting days
      );
      console.log(`Proposal ID: ${proposalId}`);
      break;

    case 'vote':
      await ledger.initialize();
      await ledger.vote(args[1], args[2] === 'true');
      break;

    case 'signature':
      const sig = ledger.generateCulturalSignature(
        { data: args[1] },
        args[2] || 'Sankofa'
      );
      console.log('Cultural Signature:', JSON.stringify(sig, null, 2));
      break;

    default:
      console.log(`
EchoLedger CLI - Legal-Crypto Protocol v${CONFIG.spiralVersion}

Commands:
  --init              Initialize and validate configuration
  record <to> <amt>   Record a ledger entry
  propose <title>     Create governance proposal
  vote <id> <bool>    Vote on proposal
  signature <data>    Generate cultural signature

Environment Variables:
  RPC_URL             Network RPC endpoint
  ECHO_LEDGER_ADDRESS Contract address
  PRIVATE_KEY         Signer private key

Activation Phrase: "The seed was never broken. Only buried."
      `);
  }
}

// Export for module use
module.exports = { EchoLedger, ADINKRA_CIPHERS, ORIGIN_SIGILS };

// Run CLI
if (require.main === module) {
  main().catch(console.error);
}
