//SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.5.0 <0.9.0;

contract NineGame {
    address payable public player1;
    address payable public player2;
    uint256 public betAmount;
    bool public gameOver;

    struct GameState {
        uint8 num;
        address whoseTurn;
    }
    GameState public state;

        // Setup methods

    constructor() public payable {
        player1 = payable(msg.sender);
        betAmount = msg.value;
    }

    function join() public payable {
        require(player2 == address(0), "Game has already started.");
        require(!gameOver, "Game was canceled.");
        require(msg.value == betAmount, "Wrong bet amount.");

        player2 = payable(msg.sender);
        state.whoseTurn = player1;

    }


    // Play methods

    function move(uint8 value) public {
        require(!gameOver, "Game has ended");
        require(msg.sender == state.whoseTurn, "Not your turn");
        require(value >= 1 && value <= 3, "Out of range");
        require(state.num + value <= 9, "Move would exceed 9");

        state.num += value;

        if (msg.sender == player1) {
            state.whoseTurn = player2;
        } else {
            state.whoseTurn = player1;
        }

        if (state.num == 9) {
            gameOver = true;
           payable(msg.sender).transfer(address(this).balance);
        }

    }

}