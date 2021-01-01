
# Create one 'matcher' instance
# Create one 'producer_from_matcher' instance

# Once new Offer is received:
    #Call matcher.add_offer method

#Once new Bid is received:
    #Call matcher.add_bid method
    # If response = True - see it as confirmation
    # Else if response = Match object:
        #call producer_from_matcher.send and send the received Match object to 'matches' Kafka topic