// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./PassportStorage.sol";

/**
 * @title PassportMarketplace
 * @dev Decentralized marketplace for passport verification services
 */
contract PassportMarketplace {
    
    PassportStorage public passportStorage;
    
    // Service listing structure
    struct ServiceListing {
        uint256 listingId;
        address provider;
        string serviceName;
        string description;
        uint256 priceInWei;
        uint256 completionTime; // in seconds
        bool isActive;
        uint256 totalOrders;
        uint256 rating; // out of 100
        uint256 ratingCount;
    }
    
    // Service order structure
    struct ServiceOrder {
        uint256 orderId;
        uint256 listingId;
        address customer;
        uint256 passportId;
        uint256 paidAmount;
        uint256 createdAt;
        uint256 completedAt;
        OrderStatus status;
        string deliveryHash; // IPFS hash of delivered service
    }
    
    enum OrderStatus { PENDING, IN_PROGRESS, COMPLETED, CANCELLED, DISPUTED }
    
    // State variables
    uint256 private listingIdCounter;
    uint256 private orderIdCounter;
    uint256 public platformFeePercent = 5; // 5% platform fee
    address public platformWallet;
    
    mapping(uint256 => ServiceListing) public listings;
    mapping(uint256 => ServiceOrder) public orders;
    mapping(address => uint256[]) public providerListings;
    mapping(address => uint256[]) public customerOrders;
    
    // Events
    event ListingCreated(uint256 indexed listingId, address indexed provider, string serviceName, uint256 price);
    event ListingUpdated(uint256 indexed listingId, uint256 newPrice, bool isActive);
    event OrderCreated(uint256 indexed orderId, uint256 indexed listingId, address indexed customer, uint256 passportId);
    event OrderCompleted(uint256 indexed orderId, string deliveryHash);
    event OrderCancelled(uint256 indexed orderId);
    event ServiceRated(uint256 indexed listingId, uint256 rating);
    event FundsWithdrawn(address indexed provider, uint256 amount);
    
    constructor(address _passportStorageAddress, address _platformWallet) {
        passportStorage = PassportStorage(_passportStorageAddress);
        platformWallet = _platformWallet;
        listingIdCounter = 1;
        orderIdCounter = 1;
    }
    
    /**
     * @dev Create service listing
     */
    function createListing(
        string memory _serviceName,
        string memory _description,
        uint256 _priceInWei,
        uint256 _completionTime
    ) external returns (uint256) {
        require(bytes(_serviceName).length > 0, "Service name required");
        require(_priceInWei > 0, "Price must be greater than 0");
        
        uint256 listingId = listingIdCounter++;
        
        listings[listingId] = ServiceListing({
            listingId: listingId,
            provider: msg.sender,
            serviceName: _serviceName,
            description: _description,
            priceInWei: _priceInWei,
            completionTime: _completionTime,
            isActive: true,
            totalOrders: 0,
            rating: 0,
            ratingCount: 0
        });
        
        providerListings[msg.sender].push(listingId);
        
        emit ListingCreated(listingId, msg.sender, _serviceName, _priceInWei);
        
        return listingId;
    }
    
    /**
     * @dev Update listing
     */
    function updateListing(
        uint256 _listingId,
        uint256 _newPrice,
        bool _isActive
    ) external {
        ServiceListing storage listing = listings[_listingId];
        require(listing.provider == msg.sender, "Not listing owner");
        
        if (_newPrice > 0) {
            listing.priceInWei = _newPrice;
        }
        listing.isActive = _isActive;
        
        emit ListingUpdated(_listingId, _newPrice, _isActive);
    }
    
    /**
     * @dev Order service
     */
    function orderService(uint256 _listingId, uint256 _passportId) external payable returns (uint256) {
        ServiceListing storage listing = listings[_listingId];
        require(listing.isActive, "Listing not active");
        require(msg.value >= listing.priceInWei, "Insufficient payment");
        require(
            passportStorage.verifyOwnership(_passportId, msg.sender),
            "Not passport owner"
        );
        
        uint256 orderId = orderIdCounter++;
        
        orders[orderId] = ServiceOrder({
            orderId: orderId,
            listingId: _listingId,
            customer: msg.sender,
            passportId: _passportId,
            paidAmount: msg.value,
            createdAt: block.timestamp,
            completedAt: 0,
            status: OrderStatus.PENDING,
            deliveryHash: ""
        });
        
        customerOrders[msg.sender].push(orderId);
        listing.totalOrders++;
        
        emit OrderCreated(orderId, _listingId, msg.sender, _passportId);
        
        return orderId;
    }
    
    /**
     * @dev Complete order (provider)
     */
    function completeOrder(uint256 _orderId, string memory _deliveryHash) external {
        ServiceOrder storage order = orders[_orderId];
        ServiceListing storage listing = listings[order.listingId];
        
        require(listing.provider == msg.sender, "Not service provider");
        require(order.status == OrderStatus.PENDING || order.status == OrderStatus.IN_PROGRESS, "Invalid status");
        require(bytes(_deliveryHash).length > 0, "Delivery hash required");
        
        order.status = OrderStatus.COMPLETED;
        order.completedAt = block.timestamp;
        order.deliveryHash = _deliveryHash;
        
        // Calculate fees
        uint256 platformFee = (order.paidAmount * platformFeePercent) / 100;
        uint256 providerAmount = order.paidAmount - platformFee;
        
        // Transfer funds
        payable(platformWallet).transfer(platformFee);
        payable(listing.provider).transfer(providerAmount);
        
        emit OrderCompleted(_orderId, _deliveryHash);
    }
    
    /**
     * @dev Cancel order
     */
    function cancelOrder(uint256 _orderId) external {
        ServiceOrder storage order = orders[_orderId];
        require(order.customer == msg.sender, "Not order customer");
        require(order.status == OrderStatus.PENDING, "Cannot cancel");
        
        order.status = OrderStatus.CANCELLED;
        
        // Refund customer
        payable(order.customer).transfer(order.paidAmount);
        
        emit OrderCancelled(_orderId);
    }
    
    /**
     * @dev Rate service
     */
    function rateService(uint256 _orderId, uint256 _rating) external {
        require(_rating > 0 && _rating <= 100, "Rating must be 1-100");
        
        ServiceOrder storage order = orders[_orderId];
        require(order.customer == msg.sender, "Not order customer");
        require(order.status == OrderStatus.COMPLETED, "Order not completed");
        
        ServiceListing storage listing = listings[order.listingId];
        
        // Update average rating
        uint256 totalRating = (listing.rating * listing.ratingCount) + _rating;
        listing.ratingCount++;
        listing.rating = totalRating / listing.ratingCount;
        
        emit ServiceRated(order.listingId, _rating);
    }
    
    /**
     * @dev Get provider listings
     */
    function getProviderListings(address _provider) external view returns (uint256[] memory) {
        return providerListings[_provider];
    }
    
    /**
     * @dev Get customer orders
     */
    function getCustomerOrders(address _customer) external view returns (uint256[] memory) {
        return customerOrders[_customer];
    }
    
    /**
     * @dev Get listing details
     */
    function getListing(uint256 _listingId) external view returns (
        address provider,
        string memory serviceName,
        string memory description,
        uint256 priceInWei,
        uint256 completionTime,
        bool isActive,
        uint256 totalOrders,
        uint256 rating
    ) {
        ServiceListing memory listing = listings[_listingId];
        return (
            listing.provider,
            listing.serviceName,
            listing.description,
            listing.priceInWei,
            listing.completionTime,
            listing.isActive,
            listing.totalOrders,
            listing.rating
        );
    }
    
    /**
     * @dev Get order details
     */
    function getOrder(uint256 _orderId) external view returns (
        uint256 listingId,
        address customer,
        uint256 passportId,
        uint256 paidAmount,
        uint256 createdAt,
        OrderStatus status,
        string memory deliveryHash
    ) {
        ServiceOrder memory order = orders[_orderId];
        return (
            order.listingId,
            order.customer,
            order.passportId,
            order.paidAmount,
            order.createdAt,
            order.status,
            order.deliveryHash
        );
    }
    
    /**
     * @dev Update platform fee (owner only)
     */
    function updatePlatformFee(uint256 _newFeePercent) external {
        require(msg.sender == platformWallet, "Not authorized");
        require(_newFeePercent <= 10, "Fee too high");
        
        platformFeePercent = _newFeePercent;
    }
}
