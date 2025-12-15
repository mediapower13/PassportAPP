const hre = require("hardhat");

async function main() {
  console.log("Deploying PassportStorage contract...");

  // Get the contract factory
  const PassportStorage = await hre.ethers.getContractFactory("PassportStorage");
  
  // Deploy the contract
  const passportStorage = await PassportStorage.deploy();
  
  await passportStorage.waitForDeployment();
  
  const address = await passportStorage.getAddress();
  
  console.log(`PassportStorage deployed to: ${address}`);
  console.log("\nContract deployment details:");
  console.log("- Network:", hre.network.name);
  console.log("- Contract Address:", address);
  
  // Save deployment info
  const fs = require('fs');
  const deploymentInfo = {
    network: hre.network.name,
    contractAddress: address,
    deployedAt: new Date().toISOString()
  };
  
  fs.writeFileSync(
    'deployment-info.json',
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log("\nDeployment info saved to deployment-info.json");
  
  // Wait for block confirmations if on a live network
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\nWaiting for block confirmations...");
    await passportStorage.deploymentTransaction().wait(6);
    console.log("Contract deployment confirmed!");
    
    // Verify contract on Etherscan
    console.log("\nVerifying contract on Etherscan...");
    try {
      await hre.run("verify:verify", {
        address: address,
        constructorArguments: [],
      });
      console.log("Contract verified successfully!");
    } catch (error) {
      console.log("Verification failed:", error.message);
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
