# Creditto

#1. General product description

The purpose of the system is to mediate between customers that would like to borrow money, borrowers,
and customers that would like to provide a loan, money lenders.

A borrower that would like to get a loan posts a request for a loan via system API - such requests is
called 'an offer'.  

Offer must contain all relevant data, including the max interest rate he is willing to pay (see models description below). 
Each offer has a unique ID assigned by the system. That offer will be available to all potential money lenders via API.

Money lenders are expected to chose an offer and propose loans that would match the offer conditions like sum, duration e.t.c.
Loan proposal is called 'a bid'. Bid interest rate must be lower then offer interest rate, since the former is
the max interest rate the borrower is willing to pay. All bids must contain the ID of the loan request so they would be linked . 
Bids with no valid loan ID will be rejected by system API.

Several bids can be placed on each offer - the best one will be selected and a match will be created.
Both parties will be notified, the offer and the bid status will be changed from 'active' to 'matched' (see statuses below),
all other bids on that offer will become 'expired'.

Matching criteria used by the system is defined by the operator (see matching logic list below) - by default
the bid with the lowest interest rate is selected when the fifth bid is received on the given offer. 
 
#2 Models description:

1. Offer:
    owner_id: the ID of the borrowing customer in the system. Only authorized customers can place offers (T.B.D)
    sum: loan sum in USD
    duration: loan duration
    offered_interest: the max interest rate the borrower is willing to offer
    status: current loan status (see statuses list below)
    matching_bid: the ID of the bid that was matched with given offer, 'NULL' by default




System components:

1. Kafka queue manager, topics:
 a. Offers
 b. Bids
 c. Matches
 
2. MySQL DB, database name: "creditto", tables:
 a. offers
 b. bids
 c. matches

3. Gateway : API exposed to end customers. Responsible for verifying received data (against DB).
 Parses data sent in requests and produces Kafka messages to the relevant topics basing on extracted data.
