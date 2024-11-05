//SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.5.0 <0.9.0;

contract RawMaterialEscrow{
    address public buyer;
    address public supplier;
    
    uint public cost;
    
    bool public isBuyerIn;
    bool public isSupplierIn;
    
    enum TransState {NOT_INITIATED, AWAITING_PAYMENT, AWAITING_DELIVERY, COMLETE} 
    TransState public currentState;
    
    modifier isBuyer() {require(msg.sender == buyer);_; }
    modifier isCostMatched(){ require(msg.value == cost); _;}
    modifier nextState(TransState _nextState) {require(currentState == _nextState); _;}
    
    
    constructor(address _buyer, address _supplier, uint _cost) public {
        buyer = _buyer;
        supplier = _supplier;
        cost = _cost;
    }
    
    function initContract() isCostMatched nextState(TransState.NOT_INITIATED) payable public{
        if(msg.sender == buyer){
            isBuyerIn = true;
        }
        if(msg.sender == supplier){
            isSupplierIn = true;
        }
        if(isBuyerIn && isSupplierIn){
            currentState = TransState.AWAITING_PAYMENT;
        }
    }
    
    function confirmPayment() isCostMatched isBuyer nextState(TransState.AWAITING_PAYMENT) payable public{
        currentState = TransState.AWAITING_DELIVERY;
    }
    
    function confirmDelivery() isBuyer nextState(TransState.AWAITING_DELIVERY) payable public{
        payable(supplier).transfer(cost);
        payable(buyer).transfer(cost);
        currentState = TransState.COMLETE;
    }
}