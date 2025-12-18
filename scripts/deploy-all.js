const hre = require("hardhat");

async function main() {
    console.log("Starting deployment of all contracts...");

    // Get deployer
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying contracts with account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy PassportStorage
    console.log("\n1. Deploying PassportStorage...");
    const PassportStorage = await hre.ethers.getContractFactory("PassportStorage");
    const passportStorage = await PassportStorage.deploy();
    await passportStorage.deployed();
    console.log("✓ PassportStorage deployed to:", passportStorage.address);

    // Deploy PassportVerification
    console.log("\n2. Deploying PassportVerification...");
    const PassportVerification = await hre.ethers.getContractFactory("PassportVerification");
    const passportVerification = await PassportVerification.deploy(passportStorage.address);
    await passportVerification.deployed();
    console.log("✓ PassportVerification deployed to:", passportVerification.address);

    // Deploy PassportAccessControl
    console.log("\n3. Deploying PassportAccessControl...");
    const PassportAccessControl = await hre.ethers.getContractFactory("PassportAccessControl");
    const passportAccessControl = await PassportAccessControl.deploy(passportStorage.address);
    await passportAccessControl.deployed();
    console.log("✓ PassportAccessControl deployed to:", passportAccessControl.address);

    // Deploy PassportNFT
    console.log("\n4. Deploying PassportNFT...");
    const PassportNFT = await hre.ethers.getContractFactory("PassportNFT");
    const passportNFT = await PassportNFT.deploy();
    await passportNFT.deployed();
    console.log("✓ PassportNFT deployed to:", passportNFT.address);

    // Deploy PassportMarketplace
    console.log("\n5. Deploying PassportMarketplace...");
    const PassportMarketplace = await hre.ethers.getContractFactory("PassportMarketplace");
    const passportMarketplace = await PassportMarketplace.deploy(
        passportStorage.address,
        deployer.address // Platform wallet
    );
    await passportMarketplace.deployed();
    console.log("✓ PassportMarketplace deployed to:", passportMarketplace.address);

    // Wait for confirmations
    console.log("\nWaiting for block confirmations...");
    await passportStorage.deployTransaction.wait(5);
    await passportVerification.deployTransaction.wait(5);
    await passportAccessControl.deployTransaction.wait(5);
    await passportNFT.deployTransaction.wait(5);
    await passportMarketplace.deployTransaction.wait(5);

    console.log("\n✅ All contracts deployed successfully!");

    // Print summary
    console.log("\n" + "=".repeat(60));
    console.log("DEPLOYMENT SUMMARY");
    console.log("=".repeat(60));
    console.log("Network:", hre.network.name);
    console.log("Deployer:", deployer.address);
    console.log("\nContract Addresses:");
    console.log("-------------------");
    console.log("PassportStorage:       ", passportStorage.address);
    console.log("PassportVerification:  ", passportVerification.address);
    console.log("PassportAccessControl: ", passportAccessControl.address);
    console.log("PassportNFT:          ", passportNFT.address);
    console.log("PassportMarketplace:  ", passportMarketplace.address);
    console.log("=".repeat(60));

    // Save deployment addresses to file
    const fs = require('fs');
    const deploymentInfo = {
        network: hre.network.name,
        chainId: hre.network.config.chainId,
        deployer: deployer.address,
        timestamp: new Date().toISOString(),
        contracts: {
            PassportStorage: passportStorage.address,
            PassportVerification: passportVerification.address,
            PassportAccessControl: passportAccessControl.address,
            PassportNFT: passportNFT.address,
            PassportMarketplace: passportMarketplace.address
        }
    };

    const deploymentFile = `deployments/${hre.network.name}_deployment.json`;
    fs.mkdirSync('deployments', { recursive: true });
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
    console.log("\n📝 Deployment info saved to:", deploymentFile);

    // Verify contracts on Etherscan (if not localhost)
    if (hre.network.name !== "localhost" && hre.network.name !== "hardhat") {
        console.log("\n⏳ Waiting before verification...");
        await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds

        console.log("\n🔍 Verifying contracts on Etherscan...");

        try {
            await hre.run("verify:verify", {
                address: passportStorage.address,
                constructorArguments: []
            });
            console.log("✓ PassportStorage verified");
        } catch (error) {
            console.log("⚠ PassportStorage verification failed:", error.message);
        }

        try {
            await hre.run("verify:verify", {
                address: passportVerification.address,
                constructorArguments: [passportStorage.address]
            });
            console.log("✓ PassportVerification verified");
        } catch (error) {
            console.log("⚠ PassportVerification verification failed:", error.message);
        }

        try {
            await hre.run("verify:verify", {
                address: passportAccessControl.address,
                constructorArguments: [passportStorage.address]
            });
            console.log("✓ PassportAccessControl verified");
        } catch (error) {
            console.log("⚠ PassportAccessControl verification failed:", error.message);
        }

        try {
            await hre.run("verify:verify", {
                address: passportNFT.address,
                constructorArguments: []
            });
            console.log("✓ PassportNFT verified");
        } catch (error) {
            console.log("⚠ PassportNFT verification failed:", error.message);
        }

        try {
            await hre.run("verify:verify", {
                address: passportMarketplace.address,
                constructorArguments: [passportStorage.address, deployer.address]
            });
            console.log("✓ PassportMarketplace verified");
        } catch (error) {
            console.log("⚠ PassportMarketplace verification failed:", error.message);
        }
    }

    console.log("\n✅ Deployment complete!");
    console.log("\n📋 Next steps:");
    console.log("1. Update frontend contract addresses");
    console.log("2. Update backend .env file");
    console.log("3. Test contract interactions");
    console.log("4. Initialize monitoring services");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
