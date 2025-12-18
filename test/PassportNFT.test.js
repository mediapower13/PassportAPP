const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PassportNFT", function () {
    let passportNFT;
    let owner;
    let addr1;
    let addr2;

    beforeEach(async function () {
        [owner, addr1, addr2] = await ethers.getSigners();

        const PassportNFT = await ethers.getContractFactory("PassportNFT");
        passportNFT = await PassportNFT.deploy();
        await passportNFT.deployed();
    });

    describe("Deployment", function () {
        it("Should set the right name and symbol", async function () {
            expect(await passportNFT.name()).to.equal("PassportNFT");
            expect(await passportNFT.symbol()).to.equal("PNFT");
        });

        it("Should start with token counter at 1", async function () {
            expect(await passportNFT.totalSupply()).to.equal(0);
        });
    });

    describe("Minting", function () {
        it("Should mint a new passport NFT", async function () {
            const passportNumber = "AB123456";
            const countryCode = "US";
            const issueDate = Math.floor(Date.now() / 1000);
            const expiryDate = issueDate + (365 * 24 * 60 * 60 * 10); // 10 years
            const ipfsHash = "QmTest123";

            await passportNFT.mint(
                addr1.address,
                passportNumber,
                countryCode,
                issueDate,
                expiryDate,
                ipfsHash
            );

            expect(await passportNFT.balanceOf(addr1.address)).to.equal(1);
            expect(await passportNFT.ownerOf(1)).to.equal(addr1.address);
        });

        it("Should set correct metadata", async function () {
            const passportNumber = "CD789012";
            const countryCode = "UK";
            const issueDate = Math.floor(Date.now() / 1000);
            const expiryDate = issueDate + (365 * 24 * 60 * 60 * 10);
            const ipfsHash = "QmTest456";

            await passportNFT.mint(
                addr1.address,
                passportNumber,
                countryCode,
                issueDate,
                expiryDate,
                ipfsHash
            );

            const metadata = await passportNFT.getPassportMetadata(1);
            expect(metadata[0]).to.equal(passportNumber);
            expect(metadata[1]).to.equal(countryCode);
            expect(metadata[4]).to.equal(ipfsHash);
            expect(metadata[5]).to.be.true; // isActive
        });

        it("Should increment token IDs", async function () {
            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");
            await passportNFT.mint(addr1.address, "P2", "UK", 0, 0, "hash2");

            expect(await passportNFT.balanceOf(addr1.address)).to.equal(2);
            expect(await passportNFT.totalSupply()).to.equal(2);
        });

        it("Should not mint to zero address", async function () {
            await expect(
                passportNFT.mint(ethers.constants.AddressZero, "P1", "US", 0, 0, "hash1")
            ).to.be.revertedWith("Cannot mint to zero address");
        });
    });

    describe("Transfers", function () {
        beforeEach(async function () {
            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");
        });

        it("Should transfer NFT", async function () {
            await passportNFT.connect(addr1).transferFrom(addr1.address, addr2.address, 1);

            expect(await passportNFT.ownerOf(1)).to.equal(addr2.address);
            expect(await passportNFT.balanceOf(addr1.address)).to.equal(0);
            expect(await passportNFT.balanceOf(addr2.address)).to.equal(1);
        });

        it("Should not transfer without authorization", async function () {
            await expect(
                passportNFT.connect(addr2).transferFrom(addr1.address, addr2.address, 1)
            ).to.be.revertedWith("Not authorized");
        });

        it("Should transfer after approval", async function () {
            await passportNFT.connect(addr1).approve(addr2.address, 1);
            await passportNFT.connect(addr2).transferFrom(addr1.address, addr2.address, 1);

            expect(await passportNFT.ownerOf(1)).to.equal(addr2.address);
        });
    });

    describe("Approvals", function () {
        beforeEach(async function () {
            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");
        });

        it("Should approve address", async function () {
            await passportNFT.connect(addr1).approve(addr2.address, 1);
            expect(await passportNFT.getApproved(1)).to.equal(addr2.address);
        });

        it("Should set approval for all", async function () {
            await passportNFT.connect(addr1).setApprovalForAll(addr2.address, true);
            expect(await passportNFT.isApprovedForAll(addr1.address, addr2.address)).to.be.true;
        });

        it("Should not approve without authorization", async function () {
            await expect(
                passportNFT.connect(addr2).approve(addr2.address, 1)
            ).to.be.revertedWith("Not authorized");
        });
    });

    describe("Burning", function () {
        beforeEach(async function () {
            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");
        });

        it("Should burn NFT", async function () {
            await passportNFT.connect(addr1).burn(1);

            expect(await passportNFT.balanceOf(addr1.address)).to.equal(0);
            await expect(passportNFT.ownerOf(1)).to.be.revertedWith("Token does not exist");
        });

        it("Should not burn without authorization", async function () {
            await expect(
                passportNFT.connect(addr2).burn(1)
            ).to.be.revertedWith("Not authorized");
        });
    });

    describe("Metadata Updates", function () {
        beforeEach(async function () {
            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");
        });

        it("Should update metadata", async function () {
            const newHash = "QmNewHash";
            await passportNFT.connect(addr1).updateMetadata(1, newHash);

            const metadata = await passportNFT.getPassportMetadata(1);
            expect(metadata[4]).to.equal(newHash);
        });

        it("Should not update metadata if not owner", async function () {
            await expect(
                passportNFT.connect(addr2).updateMetadata(1, "newHash")
            ).to.be.revertedWith("Not token owner");
        });

        it("Should deactivate passport", async function () {
            await passportNFT.connect(addr1).deactivatePassport(1);

            const metadata = await passportNFT.getPassportMetadata(1);
            expect(metadata[5]).to.be.false; // isActive
        });
    });

    describe("Expiration", function () {
        it("Should check if passport is expired", async function () {
            const issueDate = Math.floor(Date.now() / 1000);
            const expiryDate = issueDate - 1; // Already expired

            await passportNFT.mint(addr1.address, "P1", "US", issueDate, expiryDate, "hash1");

            expect(await passportNFT.isExpired(1)).to.be.true;
        });

        it("Should check if passport is not expired", async function () {
            const issueDate = Math.floor(Date.now() / 1000);
            const expiryDate = issueDate + (365 * 24 * 60 * 60); // 1 year from now

            await passportNFT.mint(addr1.address, "P1", "US", issueDate, expiryDate, "hash1");

            expect(await passportNFT.isExpired(1)).to.be.false;
        });
    });

    describe("Total Supply", function () {
        it("Should track total supply correctly", async function () {
            expect(await passportNFT.totalSupply()).to.equal(0);

            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");
            expect(await passportNFT.totalSupply()).to.equal(1);

            await passportNFT.mint(addr2.address, "P2", "UK", 0, 0, "hash2");
            expect(await passportNFT.totalSupply()).to.equal(2);

            await passportNFT.connect(addr1).burn(1);
            expect(await passportNFT.totalSupply()).to.equal(2); // Total supply doesn't decrease
        });
    });

    describe("Events", function () {
        it("Should emit Transfer event on mint", async function () {
            await expect(
                passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1")
            ).to.emit(passportNFT, "Transfer")
             .withArgs(ethers.constants.AddressZero, addr1.address, 1);
        });

        it("Should emit Transfer event on transfer", async function () {
            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");

            await expect(
                passportNFT.connect(addr1).transferFrom(addr1.address, addr2.address, 1)
            ).to.emit(passportNFT, "Transfer")
             .withArgs(addr1.address, addr2.address, 1);
        });

        it("Should emit MetadataUpdate event", async function () {
            await passportNFT.mint(addr1.address, "P1", "US", 0, 0, "hash1");

            await expect(
                passportNFT.connect(addr1).updateMetadata(1, "newHash")
            ).to.emit(passportNFT, "MetadataUpdate")
             .withArgs(1);
        });
    });
});
