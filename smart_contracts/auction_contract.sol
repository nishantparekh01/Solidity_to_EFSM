  //SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.5.0 <0.9.0;

contract Auction {

    bool public auctionOpen = true;

    uint public currentBid = 0;

    address private auctionOwner;

    address private currentBidder;

    constructor() public {
      auctionOwner = msg.sender;

    }

function placeBid() public payable {

      require (msg.sender != auctionOwner);

      // The auction must still be open
      require (auctionOpen);

      // The new bid must be higher than the current one
      require (msg.value > currentBid);

      // Remember the new bidder
      address oldBidder = currentBidder;
      uint oldBid = currentBid;
      currentBidder = msg.sender;
      currentBid = msg.value;

      // Return the money to current bidder (if there is any)
      if (oldBid != 0) {
        payable(oldBidder).transfer(oldBid);
      }

    }

function closeAuction() public {

      require (msg.sender == auctionOwner);

      // The auction must still be open
      require (auctionOpen);

      auctionOpen = false;
      payable(auctionOwner).transfer(currentBid);

    }


  }
