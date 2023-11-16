# Creditto

<b>Note: DB structure was recently changed, new column was added to the 'users' table. If you are not cloning this repo from scratch, but updating an 
existing project it is strongly recommended to delete the MySQL DB volumes.</b>

# 1 General product description

The purpose of the system is to mediate between customers that would like to borrow money, borrowers,
and customers that would like to provide a loan, moneylenders.

A borrower that would like to get a loan posts a request for a loan via system API - such request is
called an 'offer'.  

Offer must contain all relevant data, including the max interest rate the borrower is willing to pay (see models description below). 
Each offer has a unique ID assigned by the system. Placed offer will be available to all potential moneylenders via API.

Moneylenders are expected to choose an offer and propose loans that would match the offer conditions like sum, duration e.t.c.
Loan proposal is called a 'bid'. Bid interest rate must be lower than offer interest rate, since the former is
the max interest rate the borrower is willing to pay. Bids can be placed only on existing and active offers - 
lender is to select an offer and to place a bid on it, offering the lowest interest he can so his bid will be selected
to match with the targeted offer. Bids can't be placed on 'matched' and 'cancelled' offers.

Several bids can be placed on each offer - the best one will be selected and a match will be created.
The offer and the bid statuses will be changed to 'matched' (see statuses below),
all other bids on that offer will expire and their status will be changed to 'cancelled'.
A lender can place only one bid on each offer (to prevent abuse).

Matching criteria used by the system is defined by the operator (see matching logic list below) - by default
the bid with the lowest interest rate is selected when the fifth bid is received on the given offer. 
If there are several bids with identical interest rate the bid that was placed first is selected.

# Use Case:

Albert needs to borrow 10000 USD for 3 years. He is an authorized customer, his customer type is 'borrower',
and he can place offers. Albert places an offer - he is willing to pay up to 7% annual interest rate.

Bill is also an authorized customer, customer type - 'lender', he can place bids. He is looking for new attractive offers. 
He is sending a request for all available offers and see Albert's offer. 
He decides to lend the required sum to Albert, and he is willing to do so for 6.8% annual interest rate. 
Bill places a bid. 

Bill's bid is the 5th bid on Albert's offer. His bid placement triggers the matcher, and it checks all
bids placed on Albert's offer to find the best one for match. Since Sally's bid, that was placed earlier, 
has 6.4% annual interest rate it is selected, and it's status changes to MATCHED, all other bids, including Bill's, expire 
and their status is changed to CANCELLED.  Offer status is changed to MATCHED as well.

Sally (the lender) and Albert (the borrower) are both notified via email by the system on a match.

# 2 Authorization and Permissions

Customer needs to sign in with his/here credentials to place offers or bids. 
The credentials are sent in sign-in request headers. 
JSON Web Token is generated on sign-in, saved to DB and returned to the customer.
The JWT is sent in customer's request headers, it is used to identify the customer.

JWT expires when the customer sends a "sign out" request or after a certain amount of time
defined by system configuration (JWT Time To Live). 

All requests that contain an invalid JWT, an expired JWT or no token at all are rejected.

Customer's role defines the action he/she is authorized to perform.

Customer Roles:

  a. Lender - authorized to place Bids
  
  b. Borrower - authorized to place Offers
  
  c. Admin - authorized to place both Bids and Offers

Authorization module is integrated into the Gateway component.

# 3 System components
Each component is a microservice. Components communicate with each other via Kafka topics. 

Offer, Bid and Match models, tools needed for Google protobuf serialization/deserialization and loan monthly
payment calculation are taken from "credittomodels" python package:

https://pypi.org/project/credittomodels/

System chart:

<img src="https://github.com/EvgeniyJeka/Creditto/blob/main/creditto_flow.jpg" alt="Screenshot" width="1000" />
________


1. Kafka queue manager, topics:
    
    a. Offers

    b. Bids

    c. Matches
 
2. MySQL DB, database name: "creditto", tables:
    
    a. offers

    b. bids

    c. matches

    d. local_config

    e. users

    f. roles

4. <b>Gateway</b> : API exposed to end customers. Responsible for verifying received data (against DB).

     Receives: JSON from parsed POST and GET requests. 
     
     Parses data sent in requests, validates it and produces Kafka messages to the relevant topics basing on extracted data.
     
     Message content is serialized to Google Protobuf.
     
     Gateway accesses SQL DB to validate received data. 
     
     The Authorization module is integrated into Gateway.
     
     API methods:
     
     a. place_offer: add new offer to the system. Offer data is validated. 
     
     b. place_bid: add new bid to the system. Bid data ais validated. 
     
     c. get_offers_by_status: get all offers in given status. 
     
     d. get_all_offers: get all existing offers disregarding of their status. 
     
     e. get_my_bids: get all bids placed by given customer (the former is identified by provided owner_id in request).
     
     f. get_my_offers: get all offers placed by given customer.
     
     g. get_my_matches: get all matches related to given customer - the former can be either lender or borrower.
     
     h. sign_in: customer sends his credentials in request headers, JSON Web Token is sent in response.
     
     i. sign_out: expires the JSON Web Token sent in request headers.
     
     j. get_token_ttl: returns JWT Time To Live, providing the token is valid.
     
     Gateway produces 'offer' messages to Kafka topic 'Offers' and 'bid' messages to Kafka topic 'bids'.
     
     Receiving data via API = > Parsing data => Validating data against SQL DB => Producing Kafka message
     
     
 

5. <b>SQL Writer</b>: the component responsible for updating the data in MySQL DB.

    Consumes: offers from 'Offers' Kafka topic, bids from 'Bids' Kafka topic, matches from 'Matches' Kafka topic.
    Inserts and updated data in MySQL DB.
    
    a. Once new 'offer' message is received it's decoded.
    If Offer status is OPEN the retrieved offer is inserted to 'offers' SQL table.
   
    
    b. Once new 'bid' message is received it's decoded.
    If Bid status is PLACED the retrieved bid is inserted to 'bids' SQL table.
   
    
    c. Once new 'match' message is received it's decoded.
    The match is added to the 'matches' SQL table, the status of the matched Offer and the matched Bid
    are changed to MATCHED, the statuses of all other bids on that given offer changed to CANCELLED.
    
6. <b>Matcher</b>: the component responsible for matching between offers and bids. All offers and bids, that are currently 
   available for matching are kept in service cache, in a pool of offers and bids, the Matcher Pool.
   When the service starts it fetches all offers in status OPEN and all bids in status PLACED from MySQL DB.
   
   Consumes: offers from 'Offers' Kafka topic, bids from 'Bids' Kafka topic.
   Adds all received offers and bids to the Matcher Pool.
   
   Consumed Offer is added to the pool.
   Consumed Bid is added to the pool as well, 
   and if the amount of bids placed on given offer is sufficient it triggers a matching check, 
   the service checks if one of the Bids placed on that offer meets the match criteria. 
   
   Matching algorithm ID is taken from 'local_config' SQL table, the selected algorithm is applied
   to determine if there is a match. 
   
   New Offer = > Added to the pool;     
   
   New Bid = > Added to the pool => Checking for a match = > 
   => In case of a match produce a 'match' message to "Matches" Kafka topic.
   
   Message content is serialized to Google Protobuf.
   
   Once the offer is matched with one of the bids it's status changes to MATCHED and it is no longer presented
   in 'available offers' list and no bids can be placed one it. Matching bid status is changed to MATCHED as well.

6. <b> Messenger </b>: the component is responsible for notifying the lender and the borrower on a match.
   Currently they both are notified only via email, additional channels may be added in the future (for ex. Telegram).
   
   Consumes: matches from 'Matches' Kafka topic.
   Message content is deserialized.
   Both parties, the lender and the borrower, are notified via email on the match. The template files contain 
   the email text, match details and users personal details are fetched from the Match message and from SQL DB. 
   
   NOTE: this component uses Gmail an external email server. Valid username (EMAIL_APP_LOGIN) 
   and gmail app password (EMAIL_APP_PASSWORD) must be provided in environment variables. 




 
# 4 Models description:

1. <b>Offer</b>:
   owner_id: the ID of the borrowing customer in the system. Only authorized customers can place offers (T.B.D)
   
   sum: loan sum in USD
   
   duration: loan duration
   
   offered_interest: the max interest rate the borrower is willing to offer
   
   final_interest: the interest taken from the selected bid, the final interest that will be paid on the loan
   
   status: current offer status (see statuses list below)
   
   matching_bid: the ID of the bid that was matched with given offer, 'NULL' by default 

3. <b>Bid</b>:
   owner_id: the ID of the lending customer in the system. Only authorized customers can place bids (T.B.D)
   
   bid_interest: the interest asked by the lender
   
   status: current bid status (see statuses list below)
   
   target_offer: the offer that current bid seeks to match
   
   partial_only: an optional flag (T.B.D.)
   
   partial_sum: an option (T.B.D.)

3. <b>Match</b>:
   offer_id: matched offer ID
   
   bid_id: matching bid ID
   
   offer_owner_id: the ID of the borrower
   
   bid_owner_id: the ID of the lender
   
   match_time: indicated when the offer was matched 
   
   partial: an option (T.B.D.)
   
   final_interest: the interest taken from the selected bid, the final interest that will be paid on the loan
   
   monthly_payment: calculation based on interest rate and loan duration 
    
 

   
   
# 5 Statuses

1. Offer:

    <b>OPEN</b>: the offer is available for matching
    
    <b>MATCHED</b>: the offer is matched
    
    Will be added in feature versions:
    
    -PARTIALLY_MATCHED: the offer is partially matched and available for matching (T.B.D.)
    
    -CANCELLED: the offer was cancelled by the customer that has placed the offer (T.B.D.)
    
    -REMOVED: the offer was removed by the admin (T.B.D.)
    
    -HIDDEN: the offer was temporary hidden by the admin (T.B.D.)
    
2. Bid:

    <b>PLACED</b>: the bid was placed, waiting for matching algorithm to be applied
    
    <b>MATCHED</b> : the bid was matched with the targeted offer
    
    Will be added in feature versions:
    
    -CANCELLED : the bid was cancelled since other bid was matched with the target offer
    
    -REMOVED: the bid was removed by the admin (T.B.D.)
    
    -HIDDEN: the bid was temporary hidden by the admin (T.B.D.)
    
  
  # 6 Matching logic - available algorithms:
  
    1. Bid with the lowest interest is selected when 5 bids are placed on one given offer. 
    If there are several bids with equally low interest the OLDEST bid is selected.
    
    2. Bid with the lowest interest is selected when 10 bids are placed on one given offer.
    If there are several bids with equally low interest the NEWEST bid is selected.
    
    
  # 7 Requirements:
  
  - Docker client
  - Python v3.9 or above
  
  Clone the project and run 'docker-compose up -d' command to build Gateway, MySQL, Matcher and tests container images and run the project. 
  In current version Gateway listens to HTTP requests on port 5000 (see Postman collection in 'creditto_postman_collection' folder). 
  
  Project config can be changed in 'local_config' SQL table.
  
  
  1. matching_logic : responsible for selecting Matching Logic. Change the value to '2' to make the Matcher to apply Matching Logic #2 (see description above).
  2. tail_digits: max allowed tail digits. Used to round calculation results, for ex. loan monthly payment. 
    
    
  
# 8 Future Development Options

The project architecture allows to add additional functionalities.

-Currently the user (the lender and the borrower) have no option to cancel their order. It is possibly to add 'offer cancellation' functionality - 
Gateway will process the request, validate that given offer can be cancelled and the user that have sent the request is the owner of the offer.
After that 'offer cancellation' message will be produced to Kafka, consumed by Matcher (it will remove the offer and all related bids from Matcher Pool) 
and by SQL Writer (it will modify the status of the offer and all related bids in SQL DB). Bid cancellation functionality also can be added. It is also safe to assume,
that an 'admin' user should be able to cancel, hide or remove a bid or an offer - the same logic can be applied to add that functionality.

-It is possible to add more channels, in addition to email, to notify the lender and the borrower on a match. 


                                                     
   
    
   
   
 
 
 
 
 
 

 
