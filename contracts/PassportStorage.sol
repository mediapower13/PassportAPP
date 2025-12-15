// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PassportStorage
 * @dev Store and retrieve passport data on blockchain
 */
contract PassportStorage {
    
    struct PassportData {
        string passportNumber;
        string documentHash;
        uint256 timestamp;
        address owner;
        bool isActive;
    }
    
    // Mapping from passport ID to PassportData
    mapping(uint256 => PassportData) public passports;
    
    // Mapping from owner address to their passport IDs
    mapping(address => uint256[]) public ownerPassports;
    
    // Counter for passport IDs
    uint256 private passportCounter;
    
    // Events
    event PassportStored(uint256 indexed passportId, address indexed owner, string passportNumber);
    event PassportUpdated(uint256 indexed passportId, string documentHash);
    event PassportDeactivated(uint256 indexed passportId);
    
    /**
     * @dev Store new passport data
     * @param _passportNumber Passport number
     * @param _documentHash IPFS hash of the encrypted document
     */
    function storePassport(string memory _passportNumber, string memory _documentHash) public returns (uint256) {
        passportCounter++;
        
        passports[passportCounter] = PassportData({
            passportNumber: _passportNumber,
            documentHash: _documentHash,
            timestamp: block.timestamp,
            owner: msg.sender,
            isActive: true
        });
        
        ownerPassports[msg.sender].push(passportCounter);
        
        emit PassportStored(passportCounter, msg.sender, _passportNumber);
        
        return passportCounter;
    }
    
    /**
     * @dev Update passport document hash
     * @param _passportId ID of the passport
     * @param _newDocumentHash New IPFS hash
     */
    function updatePassport(uint256 _passportId, string memory _newDocumentHash) public {
        require(passports[_passportId].owner == msg.sender, "Not passport owner");
        require(passports[_passportId].isActive, "Passport is not active");
        
        passports[_passportId].documentHash = _newDocumentHash;
        passports[_passportId].timestamp = block.timestamp;
        
        emit PassportUpdated(_passportId, _newDocumentHash);
    }
    
    /**
     * @dev Deactivate a passport
     * @param _passportId ID of the passport
     */
    function deactivatePassport(uint256 _passportId) public {
        require(passports[_passportId].owner == msg.sender, "Not passport owner");
        require(passports[_passportId].isActive, "Already deactivated");
        
        passports[_passportId].isActive = false;
        
        emit PassportDeactivated(_passportId);
    }
    
    /**
     * @dev Get passport details
     * @param _passportId ID of the passport
     */
    function getPassport(uint256 _passportId) public view returns (
        string memory passportNumber,
        string memory documentHash,
        uint256 timestamp,
        address owner,
        bool isActive
    ) {
        PassportData memory passport = passports[_passportId];
        return (
            passport.passportNumber,
            passport.documentHash,
            passport.timestamp,
            passport.owner,
            passport.isActive
        );
    }
    
    /**
     * @dev Get all passport IDs for an owner
     * @param _owner Address of the owner
     */
    function getOwnerPassports(address _owner) public view returns (uint256[] memory) {
        return ownerPassports[_owner];
    }
    
    /**
     * @dev Verify passport ownership
     * @param _passportId ID of the passport
     * @param _owner Address to verify
     */
    function verifyOwnership(uint256 _passportId, address _owner) public view returns (bool) {
        return passports[_passportId].owner == _owner && passports[_passportId].isActive;
    }
}
