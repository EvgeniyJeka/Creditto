# Creditto

The purpose of the system is to mediate between customers that would like to borrow money, borrowers,
and customers that would like to provide a loan, money lenders.

A borrower that would like to get a loan posts a request for a loan via system API - such requests is
called 'an offer'.  

Offer must contain all relevant data, including the max interest rate he is willing to pay (see models description below). 
Each offer has a unique ID assigned by the system. That offer will be available to all potential money lenders via API.

Money lenders are expected to chose an offer and propose loans that would match the offer conditions like sum, duration e.t.c.
Loan proposal is called 


The money lenders will compete - the request posted by the borrower will be matched with the best offer (usually the offer with the lowest interest rate).

 All offers must contain the ID of the loan request so they would be linked . Offers with no valid loan ID will be rejected by system API.

The sum and the loan duration in the offers placed by the borrowers are set by default so they will be identical to those in loan request.