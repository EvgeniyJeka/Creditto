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
If there are several bids with identical interest rate the bid that was placed first is selected.

# Use Case:

Albert needs to borrow 10000 USD for 3 years. He is an authorized customer and can place both offers and bids.
Albert places an offer - he is willing to pay up to 7% annual interest rate.

Bill is also an authorized customer, he is looking for new attractive offers. He is sending a request 
for all available offers and see Albert's offer. He decides to lend the required sum to Albert and he
is willing to do so for 6.8% annual interest rate. Bill places a bid. 

Bill's bid is the 5th bid on Albert's offer. His bid placement triggers the matcher, and it checks all
bids placed on Albert's offer to find the best one for match. Since Sally's bid, that was placed earlier, 
has 6.4% annual interest rate it is selected and it's status changes to MATCHED, all other bids, including Bill's, expire 
and their status is changed to CANCELLED.  Offer status is changed to MATCHED as well.




 
#2 Models description:

1. Offer:
   owner_id: the ID of the borrowing customer in the system. Only authorized customers can place offers (T.B.D)
   
   sum: loan sum in USD
   
   duration: loan duration
   
   offered_interest: the max interest rate the borrower is willing to offer
   
   status: current offer status (see statuses list below)
   
   matching_bid: the ID of the bid that was matched with given offer, 'NULL' by default (T.B.D.)

3. Bid:
   owner_id: the ID of the lending customer in the system. Only authorized customers can place bids (T.B.D)
   
   bid_interest: the interest asked by the lender
   
   status: current bid status (see statuses list below)
   
   target_offer: the offer that current bid seeks to match
   
   partial_only: an optional flag (T.B.D.)
   
   partial_sum: an option (T.B.D.)

3. Match:
   offer_id: matched offer ID
   
   bid_id: matching bid ID
   
   offer_owner_id: the ID of the borrower
   
   bid_owner_id: the ID of the lender
   
   match_time: indicated when the offer was matched 
   
   partial: an option (T.B.D.)
   
   monthly_payment: calculation based on interest rate and loan duration (T.B.D.)
    
 
#System components
Each component is a micro service. Components communicate with each other via Kafka topics. 

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
 

4. SQL Writer: the component responsible for updating the data in MySQL DB.

    Consumes: offers from 'Offers' Kafka topic, bids from 'Bids' Kafka topic, matches from 'Matches' Kafka topic.
    Inserts and updated data in MySQL DB.
    
    a. Once new 'offer' message is received it's decoded.
    If Offer status is OPEN the retrieved offer is inserted to 'offers' SQL table.
    Else - existing offer status is updated (T.B.D.)
    
    b. Once new 'bid' message is received it's decoded.
    If Bid status is PLACED the retrieved bid is inserted to 'bids' SQL table.
    Else - existing bid status is updated (T.B.D.)
    
    c. Once new 'match' message is received it's decoded.
    The match is added to the 'matches' SQL table, the status of the matched Offer and the matched Bid
    are changed to MATCHED, the statuses of all other bids on that given offer changed to CANCELLED.
    
5. Matcher: the component responsible for matching between offers and bids. All offers and bids, that are currently 
   available for matching are kept in service cache, in a pool of offers and bids. 
   When the service starts it fetches all offers in status OPEN and all bids in status PLACED from MySQL DB.
   
   Consumes: offers from 'Offers' Kafka topic, bids from 'Bids' Kafka topic, matches from 'Matches' Kafka topic.
   Adds all received offers and bids to the pool kept in service cache.
   
   Consumed Offer is added to the pool. Consumed Bid is added to the pool as well and triggers matching check - 
   the service checks if one of the Bids placed on that offer meets the match criteria. 
   
   Matching algorithm ID is taken from service config file (will be moved to SQL - T.B.D.), the selected algorithm is applied
   to determine if there is a match. 
   
   New Offer = > Added to the pool;     
   
   New Bid = > Added to the pool => Checking for a match = > 
   => In case of a match produce a 'match' message to "Matches" Kafka topic.
   
   Once the offer is matched with one of the bids it's status changes to MATCHED and it is no longer presented
   in 'available offers' list and no bids can be placed one it. Matching bid status is changed to MATCHED as well.
   
   
# Statuses

1. Offer:
    OPEN: the offer is available for matching
    MATCHED: the offer is matched
    PARTIALLY_MATCHED: the offer is partially matched and available for matching (T.B.D.)
    CANCELLED: the offer was cancelled by the customer that has placed the offer (T.B.D.)
    REMOVED: the offer was removed by the admin (T.B.D.)
    HIDDEN: the offer was temporary hidden by the admin (T.B.D.)
    
2. Bid:
    PLACED: the bid was placed, waiting for matching algorithm to be applied
    MATCHED : the bid was matched with the target offer
    CANCELLED : the bid was cancelled since other bid was matched with the target offer
    REMOVED: the bid was removed by the admin (T.B.D.)
    HIDDEN: the bid was temporary hidden by the admin.
   
                                                     
   
    
   
   
 
 
 
 
 
 

 
