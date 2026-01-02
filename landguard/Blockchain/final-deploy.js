// Final deployment script
import { ethers } from "ethers";
import { writeFileSync, readFileSync } from "fs";
import { config } from "dotenv";

// Load environment variables
config({ path: "../.env" });

async function main() {
  console.log("🚀 Starting Polygon Amoy deployment...");
  
  // Get private key from environment variables
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.log("❌ PRIVATE_KEY not found in .env file");
    return;
  }
  
  // Create provider and wallet
  const provider = new ethers.JsonRpcProvider("https://rpc-amoy.polygon.technology/");
  const wallet = new ethers.Wallet(privateKey, provider);
  
  console.log(`Using account: ${wallet.address}`);
  
  // Check balance
  try {
    const balance = await provider.getBalance(wallet.address);
    const balanceInETH = ethers.formatEther(balance);
    console.log(`Balance: ${balanceInETH} MATIC`);
    
    if (parseFloat(balanceInETH) === 0) {
      console.log("❌ Insufficient funds. Please get test MATIC from a faucet first.");
      console.log("Visit: https://faucet.polygon.technology/");
      return;
    }
  } catch (error) {
    console.log(`Error checking balance: ${error.message}`);
    return;
  }
  
  // Get the compiled contract
  const contractJson = JSON.parse(readFileSync("./artifacts/contracts/LandRecordRegistry.sol/LandRecordRegistry.json", "utf8"));
  const abi = contractJson.abi;
  const bytecode = contractJson.bytecode;
  
  // Create contract factory
  const factory = new ethers.ContractFactory(abi, bytecode, wallet);
  
  console.log("Deploying contract...");
  
  // Deploy contract
  try {
    const contract = await factory.deploy();
    console.log("Transaction hash:", contract.deploymentTransaction().hash);
    
    // Wait for deployment
    await contract.waitForDeployment();
    
    const contractAddress = await contract.getAddress();
    console.log(`✅ Contract deployed at: ${contractAddress}`);
    
    // Update .env file with the new contract address
    const envPath = "../.env";
    let envContent = readFileSync(envPath, "utf8");
    
    // Update the CONTRACT_ADDRESS line
    const updatedEnvContent = envContent.replace(
      /CONTRACT_ADDRESS=.*/g,
      `CONTRACT_ADDRESS=${contractAddress}`
    );
    
    // Write the updated content back to the .env file
    writeFileSync(envPath, updatedEnvContent);
    
    console.log("Contract address updated in .env file");
    
    // Verify on explorer
    console.log(`View on explorer: https://www.oklink.com/amoy/address/${contractAddress}`);
    
    // Test the contract by registering a land record
    console.log("\nTesting contract by registering a land record...");
    try {
      const tx = await contract.registerLandRecord(12345, "QmTestCID1234567890");
      console.log(`Registration transaction hash: ${tx.hash}`);
      await tx.wait();
      console.log("✅ Land record registered successfully!");
      
      // Verify the registration
      const record = await contract.getLandRecord(12345);
      console.log(`Retrieved record - IPFS CID: ${record.ipfsCid}, Timestamp: ${new Date(Number(record.timestamp) * 1000).toISOString()}`);
    } catch (error) {
      console.log(`❌ Error testing contract: ${error.message}`);
    }
  } catch (error) {
    console.log(`❌ Deployment failed: ${error.message}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});