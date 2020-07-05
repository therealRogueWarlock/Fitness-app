import requests
import json
import datetime
import ast
from firebase import FireBase
import calculations as cal
from inspect import currentframe
debug = True

def debug_print(str):
    cf = currentframe()
    if debug:
        try:
            print(str, "Moduel:" + __name__, "Line:" + str(cf.f_back.f_lineno))
        except:
            pass


class DataBase:
    def __init__(self):
        self.filename = "user_data.txt"
        self.data = {}
        self.current_date = self.get_date()
        self.logged_in_as = ""
        self.id_token = ""

    def load_data_online(self, local_id, id_token):
        debug_print("loading data from firebase")
        self.logged_in_as = local_id
        self.id_token = id_token

        debug_print("logged in as:" + self.logged_in_as)

        try:
            # get data from online database
            debug_print("loading data from online server")
            result = requests.get("https://fitness-app-17a53.firebaseio.com/users/" + self.logged_in_as + ".json")
            debug_print("got data?" + str(result.ok))

            # decode data into dict
            self.data = {self.logged_in_as: json.loads(result.content.decode())}

            self.add_today_to_database()
            debug_print("data loaded from online firebare" + str(self.data))
            self.save_data_local()

        except requests.exceptions.ConnectionError:
            debug_print("Failed loading data from server")
            debug_print("load data from local file")
            self.load_data_local()
            debug_print("data loaded from local file:" + str(self.data))

    def load_data_local(self):
        debug_print("loading data from local file")
        with open(self.filename, "r") as file:
            for line in file:  # there should only be one line
                self.data = ast.literal_eval(line)
                debug_print(self.data)

        login_list = []
        for id in self.data.keys():
            login_list.append(id)

        self.logged_in_as = login_list[0]
        debug_print("logged i as " + self.logged_in_as)
        self.add_today_to_database()

    def add_today_to_database(self):

        dates = []
        for date in self.data[self.logged_in_as]['dates'].keys():  # getting all the dates from dict
            dates.append(date)

        if self.get_date() not in dates:  # had to put into a difrent dict to check for date
            debug_print("adding todays date to data base. ")
            name, height, weight, arms, \
            calfmuscles, chest, hip, neck, \
            quads, shoulders, underarms, waist, \
            abdomen, midaxilla, pectoral, quadriceps, \
            subscapular, suprailiac, triceps, \
            goal_weight, goal_body_fat, body_fat, age, \
            gender, wrist, head, ankle = self.get_user_data(self.get_latest_date())

            self.data[self.logged_in_as]['dates'][self.get_date()] = {'height': height, 'weight': weight,
                                                                      'body_fat': body_fat,
                                                                      'measuring_tape':
                                                                          {'arms': arms, 'calfmuscles': calfmuscles,
                                                                           'chest': chest, 'hip': hip, 'neck': neck,
                                                                           'quads': quads,
                                                                           'shoulders': shoulders,
                                                                           'underarms': underarms, 'waist': waist},
                                                                      'skinfold': {'abdomen': abdomen,
                                                                                   'midaxilla': midaxilla,
                                                                                   'pectoral': pectoral,
                                                                                   'quadriceps': quadriceps,
                                                                                   'subscapular': subscapular,
                                                                                   'suprailiac': suprailiac,
                                                                                   'triceps': triceps}
                                                                      }

            debug_print(self.data[self.logged_in_as]['dates'][self.get_date()])
        else:
            debug_print("todays date is already in database")

    def save_data_local(self):  # saving the data locally in a text file.
        debug_print("saving data locally")
        with open(self.filename, "a+") as file:
            file.truncate(0)
            file.write(str(self.data))

    def get_user_data(self, date):
        debug_print('getting user data form:' + date)

        get_from_dates = self.data[self.logged_in_as]['dates'][date]
        get_from_profile = self.data[self.logged_in_as]['profile']

        name = get_from_profile['name']
        age = get_from_profile['age']
        height = get_from_profile['body_statics']["height"]
        ankle = get_from_profile['body_statics']["ankle"]
        head = get_from_profile['body_statics']["head"]
        wrist = get_from_profile['body_statics']["wrist"]
        weight = get_from_dates['weight']
        arms = get_from_dates['measuring_tape']['arms']
        calfmuscles = get_from_dates['measuring_tape']['calfmuscles']
        chest = get_from_dates['measuring_tape']['chest']
        hip = get_from_dates['measuring_tape']['hip']
        neck = get_from_dates['measuring_tape']['neck']
        quads = get_from_dates['measuring_tape']['quads']
        shoulders = get_from_dates['measuring_tape']['shoulders']
        underarms = get_from_dates['measuring_tape']['underarms']
        waist = get_from_dates['measuring_tape']['waist']
        abdomen = get_from_dates['skinfold']['abdomen']
        midaxilla = get_from_dates['skinfold']['midaxilla']
        pectoral = get_from_dates['skinfold']['pectoral']
        quadriceps = get_from_dates['skinfold']['quadriceps']
        subscapular = get_from_dates['skinfold']['subscapular']
        suprailiac = get_from_dates['skinfold']['suprailiac']
        triceps = get_from_dates['skinfold']['triceps']
        goal_weight = get_from_profile['goals']['goal_weight']
        goal_body_fat = get_from_profile['goals']['goal_body_fat']
        body_fat = get_from_dates['body_fat']
        gender = get_from_profile['gender']

        return name, height, weight, arms, calfmuscles, \
               chest, hip, neck, quads, shoulders, underarms, \
               waist, abdomen, midaxilla, pectoral, quadriceps, subscapular, suprailiac, triceps, goal_weight, \
               goal_body_fat, body_fat, age, gender, wrist, head, ankle

    def update_data_dict(self, measuring_type, body_part, value):
        debug_print('putting value at body part' + value + body_part)
        if measuring_type == 'simple':
            self.data[self.logged_in_as]['dates'][self.get_date()][body_part] = str(value)

        elif measuring_type == 'tape':
            self.data[self.logged_in_as]['dates'][self.get_date()]['measuring_tape'][body_part] = str(value)

        elif measuring_type == 'caliper':
            self.data[self.logged_in_as]['dates'][self.get_date()]['skinfold'][body_part] = str(value)

            # calculate new bodyfat
            name, height, weight, arms, \
            calfmuscles, chest, hip, neck, \
            quads, shoulders, underarms, waist, \
            abdomen, midaxilla, pectoral, quadriceps, \
            subscapular, suprailiac, triceps, \
            goal_weight, goal_body_fat, body_fat, age, \
            gender,  wrist, head, ankle = self.get_user_data(self.get_latest_date())

            body_fat = cal.seven_skin_fold(age, pectoral, abdomen, quadriceps, triceps, subscapular, suprailiac,
                                           midaxilla)

            self.data[self.logged_in_as]['dates'][self.get_latest_date()]['body_fat'] = body_fat

        elif measuring_type == 'goal':
            self.data[self.logged_in_as]['profile']['goals'][body_part] = str(value)

        elif measuring_type == 'tape_statics':
            self.data[self.logged_in_as]['profile']['body_statics'][body_part] = str(value)

        elif measuring_type == 'years':
            self.data[self.logged_in_as]['profile'][body_part] = str(value)

        debug_print("new data added" + str(self.data))

    def upload_to_firebase(self):
        debug_print('database sending data to firebase.')
        FireBase().upload_data_to_firebase(self.logged_in_as, self.id_token, self.data)

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]

    def get_latest_date(self):
        latest_date = datetime.datetime.strptime("2020-02-04", "%Y-%m-%d")

        for date in self.data[self.logged_in_as]['dates'].keys():
            if latest_date < datetime.datetime.strptime(date, "%Y-%m-%d"):
                latest_date = datetime.datetime.strptime(date, "%Y-%m-%d")

        return str(latest_date).split(" ")[0]
