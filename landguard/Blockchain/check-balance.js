// Script to check account balance
import { ethers } from "ethers";
import { config } from "dotenv";

// Load environment variables
config({ path: "../.env" });

async function main() {
  console.log("Checking account balance on Polygon Amoy testnet...");
  
  // Get private key from environment variables
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.log("❌ PRIVATE_KEY not found in .env file");
    return;
  }
  
  // Create provider and wallet
  const provider = new ethers.JsonRpcProvider("https://rpc-amoy.polygon.technology/");
  const wallet = new ethers.Wallet(privateKey, provider);
  
  console.log(`Account address: ${wallet.address}`);
  
  // Check balance
  try {
    const balance = await provider.getBalance(wallet.address);
    const balanceInETH = ethers.formatEther(balance);
    console.log(`Balance: ${balanceInETH} MATIC`);
    
    if (parseFloat(balanceInETH) > 0) {
      console.log("✅ Account has sufficient funds for deployment");
    } else {
      console.log("❌ Account has insufficient funds. Please use a faucet to get test MATIC.");
    }
  } catch (error) {
    console.log(`Error checking balance: ${error.message}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});