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
    status: current offer status (see statuses list below)
    matching_bid: the ID of the bid that was matched with given offer, 'NULL' by default
    
3. Bid:
    owner_id: the ID of the lending customer in the system. Only authorized customers can place bids (T.B.D)
    bid_interest: the interest asked by the lender
    status: current bid status (see statuses list below)
    target_offer: the offer that current bid seeks to match
    sum: bid sum - taken from the offer by default
    partial_only: an optional flag (T.B.D.)
    partial_sum: an option (T.B.D.)

3. Match:
    offer_id: matched offer ID
    bid_id: matching bid ID
    offer_owner_id: the ID of the borrower
    bid_owner_id: the ID of the lender
    match_time: indicated when the offer was matched (T.B.D)
    partial: an option (T.B.D.)
    monthly_payment: calculation based on interest rate and loan duration (T.B.D.)
    
 
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
 Receives: JSON from parsed POST and GET requests. 
 Parses data sent in requests and produces Kafka messages to the relevant topics basing on extracted data.
 Access SQL DB to validate received data. 
 
 API methods:
 a. place_offer: add new offer to the system. Offer data is validated
 b. place_bid: add new bid to the system. Bid data ais validated
 c. get_offer_status: get offer status by provided ID (T.B.D.)
 d. get_bid_status: get bid status by provided ID (T.B.D.)
 e. get_available_offers: returns data on all offers in status OPEN (T.B.D.)
 
 Gateway produces 'offer' messages to Kafka topic 'Offers' and 'bid' messages to Kafka topic 'bids'.
 Receiving data via API = > Parsing data => Validating data against SQL DB => Producing Kafka message
 
 
 
 
 
 

 
