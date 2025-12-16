const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PassportStorage", function () {
  let PassportStorage;
  let passportStorage;
  let owner;
  let addr1;
  let addr2;

  beforeEach(async function () {
    // Get signers
    [owner, addr1, addr2] = await ethers.getSigners();

    // Deploy contract
    PassportStorage = await ethers.getContractFactory("PassportStorage");
    passportStorage = await PassportStorage.deploy();
    await passportStorage.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should deploy successfully", async function () {
      expect(await passportStorage.getAddress()).to.be.properAddress;
    });
  });

  describe("Store Passport", function () {
    it("Should store passport data correctly", async function () {
      const passportNumber = "A12345678";
      const documentHash = "0x1234567890abcdef";

      await expect(
        passportStorage.connect(owner).storePassport(passportNumber, documentHash)
      )
        .to.emit(passportStorage, "PassportStored")
        .withArgs(1, owner.address, passportNumber);

      const passport = await passportStorage.getPassport(1);
      expect(passport.passportNumber).to.equal(passportNumber);
      expect(passport.documentHash).to.equal(documentHash);
      expect(passport.owner).to.equal(owner.address);
      expect(passport.isActive).to.equal(true);
    });

    it("Should increment passport counter", async function () {
      await passportStorage.storePassport("A11111111", "0xhash1");
      await passportStorage.storePassport("A22222222", "0xhash2");

      const ownerPassports = await passportStorage.getOwnerPassports(owner.address);
      expect(ownerPassports.length).to.equal(2);
    });

    it("Should allow multiple users to store passports", async function () {
      await passportStorage.connect(owner).storePassport("A11111111", "0xhash1");
      await passportStorage.connect(addr1).storePassport("B22222222", "0xhash2");

      const ownerPassports = await passportStorage.getOwnerPassports(owner.address);
      const addr1Passports = await passportStorage.getOwnerPassports(addr1.address);

      expect(ownerPassports.length).to.equal(1);
      expect(addr1Passports.length).to.equal(1);
    });
  });

  describe("Update Passport", function () {
    it("Should update passport document hash", async function () {
      await passportStorage.storePassport("A12345678", "0xoldhash");
      
      const newHash = "0xnewhash";
      await expect(
        passportStorage.updatePassport(1, newHash)
      )
        .to.emit(passportStorage, "PassportUpdated")
        .withArgs(1, newHash);

      const passport = await passportStorage.getPassport(1);
      expect(passport.documentHash).to.equal(newHash);
    });

    it("Should only allow owner to update passport", async function () {
      await passportStorage.connect(owner).storePassport("A12345678", "0xhash");

      await expect(
        passportStorage.connect(addr1).updatePassport(1, "0xnewhash")
      ).to.be.revertedWith("Not passport owner");
    });

    it("Should not update inactive passport", async function () {
      await passportStorage.storePassport("A12345678", "0xhash");
      await passportStorage.deactivatePassport(1);

      await expect(
        passportStorage.updatePassport(1, "0xnewhash")
      ).to.be.revertedWith("Passport is not active");
    });
  });

  describe("Deactivate Passport", function () {
    it("Should deactivate passport", async function () {
      await passportStorage.storePassport("A12345678", "0xhash");

      await expect(
        passportStorage.deactivatePassport(1)
      )
        .to.emit(passportStorage, "PassportDeactivated")
        .withArgs(1);

      const passport = await passportStorage.getPassport(1);
      expect(passport.isActive).to.equal(false);
    });

    it("Should only allow owner to deactivate passport", async function () {
      await passportStorage.connect(owner).storePassport("A12345678", "0xhash");

      await expect(
        passportStorage.connect(addr1).deactivatePassport(1)
      ).to.be.revertedWith("Not passport owner");
    });

    it("Should not deactivate already inactive passport", async function () {
      await passportStorage.storePassport("A12345678", "0xhash");
      await passportStorage.deactivatePassport(1);

      await expect(
        passportStorage.deactivatePassport(1)
      ).to.be.revertedWith("Already deactivated");
    });
  });

  describe("Get Passport", function () {
    it("Should return correct passport details", async function () {
      const passportNumber = "A12345678";
      const documentHash = "0xhash";

      await passportStorage.storePassport(passportNumber, documentHash);
      const passport = await passportStorage.getPassport(1);

      expect(passport.passportNumber).to.equal(passportNumber);
      expect(passport.documentHash).to.equal(documentHash);
      expect(passport.owner).to.equal(owner.address);
      expect(passport.isActive).to.equal(true);
      expect(passport.timestamp).to.be.gt(0);
    });
  });

  describe("Get Owner Passports", function () {
    it("Should return all passports for owner", async function () {
      await passportStorage.storePassport("A11111111", "0xhash1");
      await passportStorage.storePassport("A22222222", "0xhash2");
      await passportStorage.storePassport("A33333333", "0xhash3");

      const passports = await passportStorage.getOwnerPassports(owner.address);
      expect(passports.length).to.equal(3);
    });

    it("Should return empty array for address with no passports", async function () {
      const passports = await passportStorage.getOwnerPassports(addr1.address);
      expect(passports.length).to.equal(0);
    });
  });

  describe("Verify Ownership", function () {
    it("Should verify correct ownership", async function () {
      await passportStorage.connect(owner).storePassport("A12345678", "0xhash");

      const isOwner = await passportStorage.verifyOwnership(1, owner.address);
      expect(isOwner).to.equal(true);
    });

    it("Should return false for non-owner", async function () {
      await passportStorage.connect(owner).storePassport("A12345678", "0xhash");

      const isOwner = await passportStorage.verifyOwnership(1, addr1.address);
      expect(isOwner).to.equal(false);
    });

    it("Should return false for inactive passport", async function () {
      await passportStorage.storePassport("A12345678", "0xhash");
      await passportStorage.deactivatePassport(1);

      const isOwner = await passportStorage.verifyOwnership(1, owner.address);
      expect(isOwner).to.equal(false);
    });
  });
});
