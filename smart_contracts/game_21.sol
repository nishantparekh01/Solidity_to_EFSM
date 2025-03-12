//SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.5.0 <0.9.0;

contract TwentyOneGame {
    address payable public player1;
    address payable public player2;
    uint256 public betAmount;
    bool public gameOver;

    struct GameState {
        uint8 num;
        address whoseTurn;
    }
    GameState public state;

    //uint256 public timeoutInterval;
    //uint256 public timeout = 2**256 - 1;

    event GameStarted();
    event TimeoutStarted();
    event MoveMade(address player, uint8 value);


    // Setup methods

    constructor() public payable {
        player1 = payable(msg.sender);
        betAmount = msg.value;
        //timeoutInterval = _timeoutInterval;
    }

    function join() public payable {
        require(player2 == address(0), "Game has already started.");
        require(!gameOver, "Game was canceled.");
        require(msg.value == betAmount, "Wrong bet amount.");

        player2 = payable(msg.sender);
        state.whoseTurn = player1;

        emit GameStarted();
    }

    function cancel() public {
        require(msg.sender == player1, "Only first player may cancel.");
        require(player2 == address(0), "Game has already started.");

        gameOver = true;
        payable(msg.sender).transfer(address(this).balance);
    }


    // Play methods

    function move(uint8 value) public {
        require(!gameOver, "Game has ended.");
        require(msg.sender == state.whoseTurn, "Not your turn.");
        require(value >= 1 && value <= 3,
            "Move out of range. Must be between 1 and 3.");
        require(state.num + value <= 21, "Move would exceed 21.");

        state.num += value;
        state.whoseTurn = opponentOf(msg.sender);

        // Clear timeout
        //timeout = 2**256 - 1;

        if (state.num == 21) {
            gameOver = true;
           payable(msg.sender).transfer(address(this).balance);
        }

        emit MoveMade(msg.sender, value);
    }

    function opponentOf(address player) internal view returns (address) {
        require(player2 != address(0), "Game has not started.");
    //    return player2;
        if (player == player1) {
            return player2;
        } else if (player == player2) {
            return player1;
        } else {
            revert("Invalid player.");
        }
    }


    // Timeout methods

    //function startTimeout() public {
    //    require(!gameOver, "Game has ended.");
    //    require(state.whoseTurn == opponentOf(msg.sender),
    //       "Cannot start a timeout on yourself.");

    //    timeout = block.timestamp + timeoutInterval;
    //    emit TimeoutStarted();
    //}

    //function claimTimeout() public {
    //    require(!gameOver, "Game has ended.");
    //    require(block.timestamp >= timeout);

    //    gameOver = true;
    //    payable(opponentOf(state.whoseTurn)).transfer(address(this).balance);
    //}
}