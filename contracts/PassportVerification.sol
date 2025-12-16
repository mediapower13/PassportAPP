// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./PassportStorage.sol";

/**
 * @title PassportVerification
 * @dev Verification and authentication layer for passports
 */
contract PassportVerification {
    
    PassportStorage public passportStorage;
    
    struct VerificationRequest {
        uint256 passportId;
        address requester;
        address owner;
        uint256 timestamp;
        bool approved;
        bool processed;
    }
    
    mapping(uint256 => VerificationRequest) public verificationRequests;
    mapping(uint256 => uint256[]) public passportVerifications;
    uint256 private verificationCounter;
    
    event VerificationRequested(uint256 indexed requestId, uint256 indexed passportId, address requester);
    event VerificationApproved(uint256 indexed requestId, uint256 indexed passportId);
    event VerificationRejected(uint256 indexed requestId, uint256 indexed passportId);
    
    constructor(address _passportStorageAddress) {
        passportStorage = PassportStorage(_passportStorageAddress);
    }
    
    /**
     * @dev Request verification for a passport
     */
    function requestVerification(uint256 _passportId) public returns (uint256) {
        (,, uint256 timestamp, address owner, bool isActive) = passportStorage.getPassport(_passportId);
        
        require(isActive, "Passport is not active");
        require(owner != address(0), "Passport does not exist");
        require(owner != msg.sender, "Cannot verify own passport");
        
        verificationCounter++;
        
        verificationRequests[verificationCounter] = VerificationRequest({
            passportId: _passportId,
            requester: msg.sender,
            owner: owner,
            timestamp: block.timestamp,
            approved: false,
            processed: false
        });
        
        passportVerifications[_passportId].push(verificationCounter);
        
        emit VerificationRequested(verificationCounter, _passportId, msg.sender);
        
        return verificationCounter;
    }
    
    /**
     * @dev Approve verification request
     */
    function approveVerification(uint256 _requestId) public {
        VerificationRequest storage request = verificationRequests[_requestId];
        
        require(!request.processed, "Request already processed");
        require(request.owner == msg.sender, "Only owner can approve");
        
        request.approved = true;
        request.processed = true;
        
        emit VerificationApproved(_requestId, request.passportId);
    }
    
    /**
     * @dev Reject verification request
     */
    function rejectVerification(uint256 _requestId) public {
        VerificationRequest storage request = verificationRequests[_requestId];
        
        require(!request.processed, "Request already processed");
        require(request.owner == msg.sender, "Only owner can reject");
        
        request.approved = false;
        request.processed = true;
        
        emit VerificationRejected(_requestId, request.passportId);
    }
    
    /**
     * @dev Get verification request details
     */
    function getVerificationRequest(uint256 _requestId) public view returns (
        uint256 passportId,
        address requester,
        address owner,
        uint256 timestamp,
        bool approved,
        bool processed
    ) {
        VerificationRequest memory request = verificationRequests[_requestId];
        return (
            request.passportId,
            request.requester,
            request.owner,
            request.timestamp,
            request.approved,
            request.processed
        );
    }
    
    /**
     * @dev Get all verification requests for a passport
     */
    function getPassportVerifications(uint256 _passportId) public view returns (uint256[] memory) {
        return passportVerifications[_passportId];
    }
    
    /**
     * @dev Check if verification was approved
     */
    function isVerified(uint256 _requestId) public view returns (bool) {
        VerificationRequest memory request = verificationRequests[_requestId];
        return request.processed && request.approved;
    }
}
