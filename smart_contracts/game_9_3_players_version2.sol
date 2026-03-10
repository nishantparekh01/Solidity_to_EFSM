//SPDX-License-Identifier: GPL-3.0


pragma solidity >=0.5.0 <0.9.0;

contract NineGame {
    address payable public player1;
    address payable public player2;
    address payable public player3;
    uint256 public betAmount;
    bool public gameOver;

    struct GameState {
        uint8 total;
        address whoseTurn;
    }
    GameState public state;

        // Setup methods

    constructor() public payable {
        player1 = payable(msg.sender);
        betAmount = msg.value;
    }

    function join() public payable {
        // replacing requires within if statements with bigger boolean formula in if condition
            require(!gameOver, "Game was canceled.");
            require(msg.value == betAmount, "Wrong bet amount.");

            if (player2 == address(0) && (msg.sender != player1)){
                //require(msg.sender != player1);
                player2 = payable(msg.sender);
            }
            else if (player3 == address(0) && (msg.sender != player1 && msg.sender != player2)){
                //require(msg.sender != player1 && msg.sender != player2);
                player3 = payable(msg.sender);

                state.whoseTurn = player1;
            }
    }


    // Play methods

    function move(uint8 num, uint8 numeruno) public {
        require(!gameOver, "Game has ended");
        require(msg.sender == state.whoseTurn, "Not your turn");
        require(num >= 1 && num <= 3, "Out of range");
        require(state.total + num <= 9, "Move would exceed 9");

        state.total += num;
        state.total += numeruno;

        if (msg.sender == player1) {
            state.whoseTurn = player2;
        }
        if (msg.sender == player2) {
            state.whoseTurn = player3;
        }
        if (msg.sender == player3){
            state.whoseTurn = player1;
        }


        if (state.total == 9) {
           gameOver = true;
           payable(msg.sender).transfer(address(this).balance);
           //player1.transfer(address(this).balance);
        }

    }

}