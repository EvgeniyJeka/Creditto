import pytest

from Tests.conftest import sign_in_user, test_users_passwords
from credittomodels import User


try:
    from Requests import postman
    from Tools import reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import reporter

postman = postman.Postman()
reporter = reporter.Reporter()


class TestBidSanity(object):

    def test_user_signed_in(self):
        ussr = User.User(202, 'Joe Anderson', 'cc3a062a97bf2935e0e12e1aee3bed944a81e1f4e4ca21eaa03b07be38628686',
                         'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiSm9lIEFuZGVyc29uIiwicGFzc3dvcmQiOiJUcnV0aCJ9.I4wjJ4COVHjXaJuqCWUOA87kvRtm6vWIYRngxpoVAbo',
                         'key4790', '1651420544.7691257', 2)

        ussr.password = test_users_passwords()[ussr.user_name]
        rt = sign_in_user(ussr)
        print(rt.user_name)
        print(rt.jwt_token)

    def test_get_lenders(self):
        lenders_raw = reporter.get_users_by_role(2)

        for lender in lenders_raw:
            uss = User.User(*lender)
            uss.password = test_users_passwords()[uss.user_name]

            uss_signed_in = sign_in_user(uss)
            print(f"Name: {uss_signed_in.user_name}, token: {uss_signed_in.jwt_token}")


    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_get_borrowers(self, get_authorized_borrowers):
        for user in get_authorized_borrowers:
            print(f"Username: {user.user_name}, token: {user.jwt_token}")



    test_offer_owner = 1312
    test_offer_interest = 0.06

    test_sum = 5000
    test_duration = 13

    test_bid_owner_1 = 911
    test_bid_owner_2 = 582
    test_bid_owner_3 = 781
    test_bid_owner_4 = 343
    test_bid_owner_5 = 216

    test_bid_owners_list = [test_bid_owner_1, test_bid_owner_2, test_bid_owner_3, test_bid_owner_4, test_bid_owner_5]
    test_bid_interest = 0.056



    match_input = {'offer_sum': test_sum, 'offer_duration': test_duration,
                   'offer_interest': test_offer_interest, 'bid_owners_list': test_bid_owners_list,
                   'bid_interest': test_bid_interest}

    @pytest.mark.parametrize('match_ready', [[match_input]], indirect=True)
    def test_verifying_match(self, match_ready):
        print("Test")


