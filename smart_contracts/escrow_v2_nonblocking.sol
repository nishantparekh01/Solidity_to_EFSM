//SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.5.0 <0.9.0;

contract RawMaterialEscrow{
    address public buyer;
    address public supplier;

    uint public cost;

    bool public isBuyerIn;
    bool public isSupplierIn;

    enum State {NOT_INITIATED, AWAITING_PAYMENT, AWAITING_DELIVERY, COMPLETE}
    State public state;

    // Withdrawable balances
    mapping (address => uint) withdrawable;

    modifier isBuyer() {require(msg.sender == buyer);_; }
    modifier isCostMatched(){ require(msg.value == cost); _;}
    modifier currentState(State _state) {require(state == _state); _;}


    constructor(address _buyer, address _supplier, uint _cost) public {
        buyer = _buyer;
        supplier = _supplier;
        cost = _cost;
    }

    function initContract() isCostMatched currentState(State.NOT_INITIATED) payable public{
        if(msg.sender == buyer){
            withdrawable[buyer] = withdrawable[buyer] + cost;
            isBuyerIn = true;
        }
        if(msg.sender == supplier){
            withdrawable[supplier] = withdrawable[supplier] + cost;
            isSupplierIn = true;
        }
        if(isBuyerIn){
            state = State.AWAITING_PAYMENT;
        }


    }

    function confirmPayment() isCostMatched isBuyer currentState(State.AWAITING_PAYMENT) payable public{
        withdrawable[supplier] = withdrawable[supplier] + cost;
        state = State.AWAITING_DELIVERY;
    }

    function confirmDelivery() isBuyer currentState(State.AWAITING_DELIVERY) payable public{
        // payable(supplier).transfer(2 * cost);
        // payable(buyer).transfer(cost);
        state = State.COMPLETE;
    }

    // Anyone can withdraw, i.p. operator and (current/former) players
    function withdraw() public{
        uint tmp = withdrawable[msg.sender];
        withdrawable[msg.sender] = 0;
        payable(msg.sender).transfer(tmp);
    }


}