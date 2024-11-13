//SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.5.0 <0.9.0;

contract Casino {

address payable public operator;
address payable public player ;
enum State {IDLE , GAME_AVAILABLE, BET_PLACED}
State private state ;

bytes32 public hashedNumber ;
uint public timeout;
uint256 public pot;
uint256 public tmp;
// uint constant DEFAULT_TIMEOUT = 30 minutes;
enum Coin { HEADS, TAILS }
struct Wager { uint bet ; Coin guess ; }
Wager private wager;

// Modifier to check state
modifier inState(State _state) {
    require (_state == state);
    _;
  }

modifier byOperator() {
require (msg.sender == operator);
    _;
}

modifier noActiveBet() {
require (state == State.IDLE || state == State.GAME_AVAILABLE);
    _;
}

constructor()  {
    operator = payable(msg.sender);
    state = State.IDLE;
    // timeout = DEFAULT_TIMEOUT;
    pot = 0;
    wager.bet = 0;
}

function createGame ( bytes32 hashNum ) public
byOperator
inState ( State.IDLE ) {
hashedNumber = hashNum;
state = State.GAME_AVAILABLE; }

function placeBet ( Coin _guess ) public payable
inState ( State.GAME_AVAILABLE) {
require (msg.sender != operator ) ;
require (msg.value > 0 && msg.value <= pot ) ;
player = payable(msg.sender);
wager = Wager ( {
bet : msg.value ,
guess : _guess
 } ) ;
state = State.BET_PLACED ; }

function decideBet ( uint secretNumber ) public
byOperator
inState ( State.BET_PLACED) {
require ( hashedNumber == keccak256 ( abi.encodePacked(secretNumber) ) ) ;
Coin secret = ( secretNumber % 2 == 0 ) ? Coin .HEADS : Coin . TAILS ;
if ( secret == wager.guess) {
playerWins ( ) ;
} else {
operatorWins ( ) ;
}
state = State.IDLE ; }

function playerWins( ) private {
tmp = wager.bet;
wager.bet = 0 ;
pot = pot - tmp ;
player.transfer( tmp * 2 ) ; }

function operatorWins( ) private {
pot = pot + wager.bet ;
wager.bet = 0 ; }

function addToPot ( ) public payable
byOperator {
pot = pot + msg.value ; }

function removeFromPot ( uint amount ) public
byOperator
noActiveBet{
pot = pot - amount ;
operator.transfer(amount) ; }
 }