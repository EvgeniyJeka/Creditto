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
            print(uss.user_name)