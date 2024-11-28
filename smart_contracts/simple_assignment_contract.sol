  //SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.5.0 <0.9.0;

contract simpleAssignment{

address payable public operator;
uint public cost;

bool public foo = false;

constructor()  {
    operator = payable(msg.sender);
}

function setFooTrue() public {
    require(msg.sender == operator);
    foo = true;
    operator.transfer(cost);

}
}