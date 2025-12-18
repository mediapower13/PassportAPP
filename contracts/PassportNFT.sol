// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PassportNFT
 * @dev NFT representation of passports with metadata
 */
contract PassportNFT {
    
    // Token counter
    uint256 private _tokenIdCounter;
    
    // Token ownership
    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;
    mapping(uint256 => address) private _tokenApprovals;
    mapping(address => mapping(address => bool)) private _operatorApprovals;
    
    // Token metadata
    mapping(uint256 => string) private _tokenURIs;
    mapping(uint256 => PassportMetadata) private _passportMetadata;
    
    struct PassportMetadata {
        string passportNumber;
        string countryCode;
        uint256 issueDate;
        uint256 expiryDate;
        string ipfsHash;
        bool isActive;
    }
    
    // Events
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);
    event MetadataUpdate(uint256 indexed tokenId);
    
    // ERC721 Metadata
    string public name = "PassportNFT";
    string public symbol = "PNFT";
    
    constructor() {
        _tokenIdCounter = 1;
    }
    
    /**
     * @dev Mint new passport NFT
     */
    function mint(
        address to,
        string memory passportNumber,
        string memory countryCode,
        uint256 issueDate,
        uint256 expiryDate,
        string memory ipfsHash
    ) external returns (uint256) {
        require(to != address(0), "Cannot mint to zero address");
        
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        _owners[tokenId] = to;
        _balances[to]++;
        
        _passportMetadata[tokenId] = PassportMetadata({
            passportNumber: passportNumber,
            countryCode: countryCode,
            issueDate: issueDate,
            expiryDate: expiryDate,
            ipfsHash: ipfsHash,
            isActive: true
        });
        
        emit Transfer(address(0), to, tokenId);
        
        return tokenId;
    }
    
    /**
     * @dev Burn passport NFT
     */
    function burn(uint256 tokenId) external {
        require(_isApprovedOrOwner(msg.sender, tokenId), "Not authorized");
        
        address owner = _owners[tokenId];
        
        _tokenApprovals[tokenId] = address(0);
        _balances[owner]--;
        delete _owners[tokenId];
        delete _passportMetadata[tokenId];
        
        emit Transfer(owner, address(0), tokenId);
    }
    
    /**
     * @dev Transfer token
     */
    function transferFrom(address from, address to, uint256 tokenId) external {
        require(_isApprovedOrOwner(msg.sender, tokenId), "Not authorized");
        require(ownerOf(tokenId) == from, "From address is not owner");
        require(to != address(0), "Cannot transfer to zero address");
        
        _tokenApprovals[tokenId] = address(0);
        
        _balances[from]--;
        _balances[to]++;
        _owners[tokenId] = to;
        
        emit Transfer(from, to, tokenId);
    }
    
    /**
     * @dev Safe transfer with data
     */
    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
    ) external {
        require(_isApprovedOrOwner(msg.sender, tokenId), "Not authorized");
        require(ownerOf(tokenId) == from, "From address is not owner");
        require(to != address(0), "Cannot transfer to zero address");
        
        _tokenApprovals[tokenId] = address(0);
        
        _balances[from]--;
        _balances[to]++;
        _owners[tokenId] = to;
        
        emit Transfer(from, to, tokenId);
    }
    
    /**
     * @dev Approve address to transfer token
     */
    function approve(address to, uint256 tokenId) external {
        address owner = ownerOf(tokenId);
        require(msg.sender == owner || isApprovedForAll(owner, msg.sender), "Not authorized");
        
        _tokenApprovals[tokenId] = to;
        emit Approval(owner, to, tokenId);
    }
    
    /**
     * @dev Set approval for all tokens
     */
    function setApprovalForAll(address operator, bool approved) external {
        require(operator != msg.sender, "Cannot approve self");
        
        _operatorApprovals[msg.sender][operator] = approved;
        emit ApprovalForAll(msg.sender, operator, approved);
    }
    
    /**
     * @dev Get token owner
     */
    function ownerOf(uint256 tokenId) public view returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "Token does not exist");
        return owner;
    }
    
    /**
     * @dev Get balance of owner
     */
    function balanceOf(address owner) external view returns (uint256) {
        require(owner != address(0), "Zero address query");
        return _balances[owner];
    }
    
    /**
     * @dev Get approved address for token
     */
    function getApproved(uint256 tokenId) external view returns (address) {
        require(_owners[tokenId] != address(0), "Token does not exist");
        return _tokenApprovals[tokenId];
    }
    
    /**
     * @dev Check if operator is approved for all
     */
    function isApprovedForAll(address owner, address operator) public view returns (bool) {
        return _operatorApprovals[owner][operator];
    }
    
    /**
     * @dev Get passport metadata
     */
    function getPassportMetadata(uint256 tokenId) external view returns (
        string memory passportNumber,
        string memory countryCode,
        uint256 issueDate,
        uint256 expiryDate,
        string memory ipfsHash,
        bool isActive
    ) {
        require(_owners[tokenId] != address(0), "Token does not exist");
        
        PassportMetadata memory metadata = _passportMetadata[tokenId];
        
        return (
            metadata.passportNumber,
            metadata.countryCode,
            metadata.issueDate,
            metadata.expiryDate,
            metadata.ipfsHash,
            metadata.isActive
        );
    }
    
    /**
     * @dev Update passport metadata
     */
    function updateMetadata(
        uint256 tokenId,
        string memory ipfsHash
    ) external {
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        
        _passportMetadata[tokenId].ipfsHash = ipfsHash;
        
        emit MetadataUpdate(tokenId);
    }
    
    /**
     * @dev Deactivate passport
     */
    function deactivatePassport(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        
        _passportMetadata[tokenId].isActive = false;
        
        emit MetadataUpdate(tokenId);
    }
    
    /**
     * @dev Check if passport is expired
     */
    function isExpired(uint256 tokenId) external view returns (bool) {
        require(_owners[tokenId] != address(0), "Token does not exist");
        
        return block.timestamp > _passportMetadata[tokenId].expiryDate;
    }
    
    /**
     * @dev Internal function to check if address is approved or owner
     */
    function _isApprovedOrOwner(address spender, uint256 tokenId) internal view returns (bool) {
        address owner = ownerOf(tokenId);
        return (spender == owner || 
                _tokenApprovals[tokenId] == spender || 
                isApprovedForAll(owner, spender));
    }
    
    /**
     * @dev Get total supply
     */
    function totalSupply() external view returns (uint256) {
        return _tokenIdCounter - 1;
    }
}
