// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./PassportStorage.sol";

/**
 * @title PassportAccessControl
 * @dev Advanced access control and delegation for passport management
 */
contract PassportAccessControl {
    PassportStorage public passportStorage;
    
    // Access levels
    enum AccessLevel { NONE, VIEW, EDIT, FULL }
    
    // Delegation structure
    struct Delegation {
        address delegatee;
        AccessLevel level;
        uint256 expiryTime;
        bool isActive;
        string purpose;
    }
    
    // Mapping: passport owner => delegatee => delegation
    mapping(address => mapping(address => Delegation)) public delegations;
    
    // Mapping: passport ID => authorized addresses
    mapping(uint256 => mapping(address => AccessLevel)) public passportAccess;
    
    // Events
    event AccessGranted(
        address indexed owner,
        address indexed delegatee,
        AccessLevel level,
        uint256 expiryTime
    );
    
    event AccessRevoked(
        address indexed owner,
        address indexed delegatee
    );
    
    event PassportAccessGranted(
        uint256 indexed passportId,
        address indexed grantedTo,
        AccessLevel level
    );
    
    event PassportAccessRevoked(
        uint256 indexed passportId,
        address indexed revokedFrom
    );
    
    constructor(address _passportStorageAddress) {
        passportStorage = PassportStorage(_passportStorageAddress);
    }
    
    /**
     * @dev Grant access to another address
     */
    function grantAccess(
        address _delegatee,
        AccessLevel _level,
        uint256 _durationInDays,
        string memory _purpose
    ) external {
        require(_delegatee != address(0), "Invalid delegatee address");
        require(_delegatee != msg.sender, "Cannot delegate to yourself");
        require(_level != AccessLevel.NONE, "Invalid access level");
        
        uint256 expiryTime = block.timestamp + (_durationInDays * 1 days);
        
        delegations[msg.sender][_delegatee] = Delegation({
            delegatee: _delegatee,
            level: _level,
            expiryTime: expiryTime,
            isActive: true,
            purpose: _purpose
        });
        
        emit AccessGranted(msg.sender, _delegatee, _level, expiryTime);
    }
    
    /**
     * @dev Revoke access from delegatee
     */
    function revokeAccess(address _delegatee) external {
        require(delegations[msg.sender][_delegatee].isActive, "No active delegation");
        
        delegations[msg.sender][_delegatee].isActive = false;
        
        emit AccessRevoked(msg.sender, _delegatee);
    }
    
    /**
     * @dev Grant access to specific passport
     */
    function grantPassportAccess(
        uint256 _passportId,
        address _grantTo,
        AccessLevel _level
    ) external {
        require(
            passportStorage.verifyOwnership(_passportId, msg.sender),
            "Not passport owner"
        );
        require(_grantTo != address(0), "Invalid address");
        require(_level != AccessLevel.NONE, "Invalid access level");
        
        passportAccess[_passportId][_grantTo] = _level;
        
        emit PassportAccessGranted(_passportId, _grantTo, _level);
    }
    
    /**
     * @dev Revoke access to specific passport
     */
    function revokePassportAccess(uint256 _passportId, address _revokeFrom) external {
        require(
            passportStorage.verifyOwnership(_passportId, msg.sender),
            "Not passport owner"
        );
        
        passportAccess[_passportId][_revokeFrom] = AccessLevel.NONE;
        
        emit PassportAccessRevoked(_passportId, _revokeFrom);
    }
    
    /**
     * @dev Check if address has access to owner's passports
     */
    function hasAccess(address _owner, address _delegatee) public view returns (bool) {
        Delegation memory delegation = delegations[_owner][_delegatee];
        
        if (!delegation.isActive) return false;
        if (block.timestamp > delegation.expiryTime) return false;
        
        return delegation.level != AccessLevel.NONE;
    }
    
    /**
     * @dev Get delegation details
     */
    function getDelegation(address _owner, address _delegatee) 
        external 
        view 
        returns (
            AccessLevel level,
            uint256 expiryTime,
            bool isActive,
            string memory purpose
        ) 
    {
        Delegation memory delegation = delegations[_owner][_delegatee];
        return (
            delegation.level,
            delegation.expiryTime,
            delegation.isActive,
            delegation.purpose
        );
    }
    
    /**
     * @dev Check access level for specific passport
     */
    function getPassportAccessLevel(uint256 _passportId, address _user) 
        external 
        view 
        returns (AccessLevel) 
    {
        return passportAccess[_passportId][_user];
    }
    
    /**
     * @dev Verify if user can view passport
     */
    function canView(uint256 _passportId, address _user) external view returns (bool) {
        // Owner always has access
        if (passportStorage.verifyOwnership(_passportId, _user)) {
            return true;
        }
        
        // Check specific passport access
        AccessLevel level = passportAccess[_passportId][_user];
        return level != AccessLevel.NONE;
    }
    
    /**
     * @dev Verify if user can edit passport
     */
    function canEdit(uint256 _passportId, address _user) external view returns (bool) {
        // Owner always has access
        if (passportStorage.verifyOwnership(_passportId, _user)) {
            return true;
        }
        
        // Check specific passport access
        AccessLevel level = passportAccess[_passportId][_user];
        return level == AccessLevel.EDIT || level == AccessLevel.FULL;
    }
}
