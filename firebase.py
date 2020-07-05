import requests
import json
from kivy.app import App
from inspect import currentframe
debug = True


def debug_print(string):
    cf = currentframe()
    if debug:
        print(string, "moduel:" + __name__, "line:" + str(cf.f_back.f_lineno))


# wep api key: AIzaSyCqAA3gAMaiC_URf6udmhh8esdEnfMIPIo


class FireBase:
    def __init__(self):
        self.wep_api_key = "AIzaSyCqAA3gAMaiC_URf6udmhh8esdEnfMIPIo"
        self.app = App.get_running_app()

    def sign_up(self, email, password):

        # send the email and the password to firebase
        # Firebase will return localid, authToken, refreshToken
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wep_api_key
        signup_data = {"email": email, "password": password, "return_secure_token": True}
        signup_request = requests.post(signup_url, data=signup_data)

        signup_tokens = json.loads(signup_request.content.decode())
        if signup_request.ok:
            # remove error message if one was displayed.
            self.app.root.ids["login_screen"].ids["login_message"].text = ""

            debug_print("adding new user to database")

            refresh_token = signup_tokens["refreshToken"]
            localId = signup_tokens["localId"]
            idToken = signup_tokens["idToken"]

            # Save the refresh token to automatically login back in
            with open("refresh_token.txt", "w") as file:
                file.write(refresh_token)

            # save localid to a variable in the running app (this session)
            self.app.local_id = localId
            # save id token to a variable in the running app
            self.app.id_token = idToken

            # create new key in database for new user. setting up default json for new user.

            # new_user = '{"dates": {"2020-02-28": {"body_fat": "00","height": "00", "measuring_tape": {"arms": "00",' \
            #            '"calfmuscles": "00","chest": "00","hip": "00","neck": "00","quads": "00","shoulders": "00",' \
            #            '"underarms": "00","waist": "00"},"skinfold": {"abdomen": "00","midaxilla": "00","pectoral": ' \
            #            '"00","quadriceps": "00","subscapular": "00","suprailiac": "00","triceps": "00"},' \
            #            '"weight": "00"}},"profile": {"body_statics": {"ankle": "00","head": "00","height": "00",' \
            #            '"wrist": "00"},"goals": {"goal_body_fat": "00","goal_weight": "00"},"profilepic": "user.png" ' \
            #            ',"name": "noname"}} '

            new_user = {
                "dates": {
                    "2020-02-28": {
                        "body_fat": "00",
                        "measuring_tape": {
                            "arms": "00",
                            "calfmuscles": "00",
                            "chest": "00",
                            "hip": "00",
                            "neck": "00",
                            "quads": "00",
                            "shoulders": "00",
                            "underarms": "00",
                            "waist": "00"
                        },
                        "skinfold": {
                            "abdomen": "00",
                            "midaxilla": "00",
                            "pectoral": "00",
                            "quadriceps": "00",
                            "subscapular": "00",
                            "suprailiac": "00",
                            "triceps": "00"
                        },
                        "weight": "00"
                    }
                },
                "profile": {
                    "age": "00",
                    "body_statics": {
                        "ankle": "00",
                        "head": "00",
                        "height": "170",
                        "wrist": "00"
                    },
                    "gender": "male",
                    "goals": {
                        "goal_body_fat": "00",
                        "goal_weight": "00"
                    },
                    "name": "noname",
                    "profilepic": "user.png"
                }
            }

            check = requests.patch("https://fitness-app-17a53.firebaseio.com/users/"
                                   + localId + ".json?auth=" + idToken,
                                   data=json.dumps(new_user))

            debug_print("adding new user" + str(check.ok))
            debug_print("what happend" + str(check.content.decode()))

        if not signup_request.ok:
            error_data = json.loads(signup_request.content.decode())
            error_message = error_data["error"]["message"]
            self.app.root.ids["login_screen"].ids["login_message"].text = error_message

    def sign_in(self, email, password):
        debug_print("sign_in")
        signin_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.wep_api_key
        signin_data = {"email": email, "password": password, "return_secure_token": True}
        signin_request = requests.post(signin_url, data=signin_data)

        signin_tokens = json.loads(signin_request.content.decode())

        debug_print(signin_request.ok)
        debug_print(signin_tokens)

        if signin_request.ok:
            debug_print("sign in ok")
            # remove error message if one was displayed.
            self.app.root.ids["login_screen"].ids["login_message"].text = ""

            refresh_token = signin_tokens["refreshToken"]
            localId = signin_tokens["localId"]
            idToken = signin_tokens["idToken"]

            # Save the refresh token to automatically login back in
            with open("refresh_token.txt", "w") as file:
                file.write(refresh_token)

            # save localid to a variable in the running app (this session)
            self.app.local_id = localId
            # save id token to a variable in the running app ( not working
            self.app.id_token = idToken

            debug_print("calling function in app to load data")
            self.app.load_data_firebase()
            self.app.change_screen("home_screen")

        if not signin_request.ok:
            error_data = json.loads(signin_request.content.decode())
            error_message = error_data["error"]["message"]
            self.app.root.ids["login_screen"].ids["login_message"].text = error_message

    def exhange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wep_api_key
        refresh_data = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_request = requests.post(refresh_url, data=refresh_data)
        debug_print("ok refresh?" + refresh_request.ok)
        id_token = refresh_request.json()['id_token']
        local_id = refresh_request.json()['user_id']
        return id_token, local_id

    def upload_data_to_firebase(self, local_id, id_token, user_data):
        debug_print("sending request to load data to firebase")
        # uploading data to firebase at user. useing local, and token id.
        # id local id is included in user data dict.
        check = requests.patch("https://fitness-app-17a53.firebaseio.com/users/.json?auth=" + id_token,
                               data=json.dumps(user_data))

        debug_print("upload data to firebase" + str(check.ok))
        debug_print("what happend" + check.content.decode())
