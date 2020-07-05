from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from math import sin
from kivy.uix.carousel import Carousel
from kivy_garden.graph import Graph, MeshLinePlot
from firebase import FireBase
from kivy.app import App
from kivy.uix.popup import Popup
import calculations as cal
from kivy.uix.widget import Widget
from inspect import currentframe

debug = True


def debug_print(string):
    cf = currentframe()
    if debug:
        print(string, "Moduel:" + __name__, "Line:" + str(cf.f_back.f_lineno))


class UserProfile:
    def __init__(self):
        self.name = ''
        self.height = ''
        self.weight = ''
        self.arms = ''
        self.calfmuscles = ''
        self.chest = ''
        self.hip = ''
        self.neck = ''
        self.quads = ''
        self.shoulders = ''
        self.underarms = ''
        self.waist = ''
        self.abdomen = ''
        self.midaxilla = ''
        self.pectoral = ''
        self.quadriceps = ''
        self.subscapular = ''
        self.suprailiac = ''
        self.triceps = ''
        self.goal_weight = ''
        self.goal_body_fat = ''
        self.body_fat = ''
        self.age = ''
        self.gender = ''
        self.wrist = ''
        self.head = ''
        self.ankle = ''

    def update(self):  # getting stats from database store in profile class.
        self.name, self.height, self.weight, self.arms, \
        self.calfmuscles, self.chest, self.hip, self.neck, \
        self.quads, self.shoulders, self.underarms, self.waist, \
        self.abdomen, self.midaxilla, self.pectoral, self.quadriceps, \
        self.subscapular, self.suprailiac, self.triceps, self.goal_weight, \
        self.goal_body_fat, self.body_fat, self.age, self.gender, self.wrist, \
        self.head, self.ankle = database.get_user_data(database.get_latest_date())


class PopupInputWidget(Popup):
    data_value = ObjectProperty(None)
    display_body_title = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.body_part = ''
        self.measuring_type = ''

    def input_to_database(self):
        print("storing data with today's date")
        if self.data_value.text != '':
            database.update_data_dict(self.measuring_type, self.body_part, self.data_value.text)

    def open_with_info(self, body_part):
        display_text = ''

        if body_part == 'weight':
            display_text = 'Weight in kg'
            self.measuring_type = 'simple'

        if body_part in ['arms', 'calfmuscles', 'chest', 'hip', 'neck',
                         'quads', 'shoulders', 'underarms', 'waist']:
            display_text = f'{body_part} in cm'
            self.measuring_type = 'tape'

        if body_part in ['ankle', 'wrist', 'head', 'height']:
            display_text = f'{body_part} in cm'
            self.measuring_type = 'tape_statics'

        if body_part in ['abdomen', 'midaxilla', 'pectoral', 'quadriceps', 'subscapular', 'suprailiac', 'triceps']:
            display_text = f'{body_part} in mm'
            self.measuring_type = 'caliper'

        if body_part == 'goal_body_fat':
            display_text = 'input a %'
            self.measuring_type = 'goal'

        if body_part == 'goal_weight':
            display_text = 'Weight in kg'
            self.measuring_type = 'goal'

        if body_part == 'age':
            display_text = "Age in years"
            self.measuring_type = 'years'

        self.display_body_title.text = display_text
        self.body_part = body_part

        self.open()


class LoginScreen(Screen):
    Window.clearcolor = (0, 1, 1, 1)


class HomeScreen(Screen):
    # weight
    body_weight = ObjectProperty(None)
    body_goal_weight = ObjectProperty(None)
    body_weight_dif = ObjectProperty(None)

    # Body fat
    body_body_fat = ObjectProperty(None)
    body_goal_body_fat = ObjectProperty(None)
    body_body_fat_dif = ObjectProperty(None)

    # Bmi
    body_bmi = ObjectProperty(None)

    def update_stats(self):
        debug_print('updating stats on screen')
        user.update()

        # weight
        self.body_weight.text = "Weight: \n   " + str(user.weight) + " Kg"
        self.body_goal_weight.text = str(user.goal_weight) + " Kg"
        self.body_weight_dif.text = str(round((float(user.goal_weight) - float(user.weight)), 2)) + " kg \nto go!"

        # Body fat
        self.body_body_fat.text = "bodyfat: \n " + str(user.body_fat) + "%"
        self.body_goal_body_fat.text = str(user.goal_body_fat) + "%"
        self.body_body_fat_dif.text = str(round((float(user.goal_body_fat) - float(user.body_fat)), 2)) + " % \nto go!"

        # Bmi
        self.body_bmi.text = 'Bmi: \n ' + str(cal.culate_bmi(user.height, user.weight))

    def on_enter(self, *args):
        self.update_stats()

    def input_popup(self, body_part):
        PopupInputWidget().open_with_info(body_part)


class LabelButton(ButtonBehavior, Label):
    pass


class ImageButton(ButtonBehavior, Image):
    pass


class StatsScreen(Screen):
    body_weight = ObjectProperty(None)
    # measuring tape
    body_arms = ObjectProperty(None)
    body_calfmuscles = ObjectProperty(None)
    body_chest = ObjectProperty(None)
    body_shoulders = ObjectProperty(None)
    body_neck = ObjectProperty(None)
    body_quads = ObjectProperty(None)
    body_underarms = ObjectProperty(None)
    body_waist = ObjectProperty(None)
    body_hip = ObjectProperty(None)
    # skin fold
    body_abdomen = ObjectProperty(None)
    body_midaxilla = ObjectProperty(None)
    body_pectoral = ObjectProperty(None)
    body_quadriceps = ObjectProperty(None)
    body_subscapular = ObjectProperty(None)
    body_suprailiac = ObjectProperty(None)
    body_triceps = ObjectProperty(None)
    # date
    date = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.dates = []
        self.carousel_updated = False

    def update_carousel(self):
        debug_print(database.data[database.logged_in_as]['dates'].keys())
        for date in database.data[database.logged_in_as]['dates'].keys():
            if date != database.get_latest_date():
                self.dates.insert(0, date)
        debug_print(self.dates)

        for date in self.dates:
            debug_print('updating stats in carousel')
            name, height, weight, arms, \
            calfmuscles, chest, hip, neck, \
            quads, shoulders, underarms, waist, \
            abdomen, midaxilla, pectoral, quadriceps, subscapular, suprailiac, triceps, \
            goal_weight, goal_body_fat, body_fat, age, gender, wrist, head, ankle = database.get_user_data(date)

            self.body_weight.text = "Weight: \n   " + str(weight) + " Kg"
            # measuring tape
            self.body_arms.text = "Arms: \n" + str(arms) + " cm"
            self.body_calfmuscles.text = "Calfmuscles: \n" + str(calfmuscles) + " cm"
            self.body_chest.text = "Chest: \n" + str(chest) + " cm"
            self.body_shoulders.text = "Shoulders: \n" + str(shoulders) + " cm"
            self.body_neck.text = "Neck: \n" + str(neck) + " cm"
            self.body_quads.text = "Quads: \n" + str(quads) + " cm"
            self.body_underarms.text = "Underarms: \n" + str(underarms) + " cm"
            self.body_waist.text = "Waist: \n" + str(waist) + " cm"
            self.body_hip.text = "Hip: \n" + str(hip) + " cm"
            # skin fold
            self.body_abdomen.text = "Abdomen: \n" + str(abdomen) + " mm"
            self.body_midaxilla.text = "Midaxilla: \n" + str(midaxilla) + " mm"
            self.body_pectoral.text = "Pectoral: \n" + str(pectoral) + " mm"
            self.body_quadriceps.text = "Quadriceps: \n" + str(quadriceps) + " mm"
            self.body_subscapular.text = "Subscapular: \n" + str(subscapular) + " mm"
            self.body_suprailiac.text = "Suprailiac: \n" + str(suprailiac) + " mm"
            self.body_triceps.text = "Triceps: \n" + str(triceps) + " mm"
            stats = Builder.load_string(f'''FloatLayout:
    ScrollView:
        GridLayout:
            rows: 3

            size_hint_y: None
            height: self.minimum_height
            row_default_height: "300dp"
            row_force_default: True

            GridLayout:
                rows: 2


                ImageButton:
                    size_hint: 1, 0.4
                    source: "icons/006-weight-scale.png"
                    on_release:
                        print("weight")


                Button:

                    text: "Weight: \\n{str(weight)} "
                    font_size: .15 * (self.width + self.height)/2


            GridLayout:
                rows: 2
                ImageButton:
                    size_hint: 1, 0.4
                    source: "icons/001-ruler.png"
                    on_release:
                        print("Messurement")

                GridLayout:
                    cols: 3
                    Button:
                        text: "Arms: \\n{str(arms)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Calfmuscles: \\n{str(calfmuscles)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Chest: \\n{str(chest)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Shoulders: \\n{str(shoulders)}"
                        font_size: .15 * (self.width + self.height)/2
                        on_release:
                            root.input_popup('shoulders')

                    Button:
                        text: "Neck: \\n{str(neck)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Quads: \\n{str(quads)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Underarms: \\n{str(underarms)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Waist: \\n{str(weight)}"
                        font_size: .15 * (self.width + self.height)/2



                    Button:

                        text: "Hip: \\n{str(hip)}"
                        font_size: .15 * (self.width + self.height)/2


            GridLayout:
                rows: 2

                ImageButton:
                    size_hint: 1, .4
                    source: "icons/003-caliper-1.png"


                GridLayout:
                    cols: 3

                    Button:

                        text: "Abdomen: \\n{str(abdomen)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Midaxilla: \\n{str(midaxilla)}"
                        font_size: .15 * (self.width + self.height)/2



                    Button:

                        text: "Pectoral: \\n{str(pectoral)}"
                        font_size: .15 * (self.width + self.height)/2



                    Button:

                        text: "Quadriceps: \\n{str(quadriceps)}"
                        font_size: .15 * (self.width + self.height)/2


                    Button:

                        text: "Subscapular: \\n{str(subscapular)}"
                        font_size: .15 * (self.width + self.height)/2



                    Button:

                        text: "Suprailiac. \\n{str(suprailiac)}"
                        font_size: .15 * (self.width + self.height)/2



                    Button:

                        text: "Triceps: \\n{str(triceps)}"
                        font_size: .15 * (self.width + self.height)/2''')
            self.carousel.add_widget(stats)
            self.carousel_updated = True

        self.dates.insert(0, database.get_latest_date())

    def update_stats(self):
        debug_print('updating stats on screen, ' + database.get_latest_date())
        user.update()
        # self.body_height.text = "Height: \n  " + str(height) + " cm"
        self.body_weight.text = "Weight: \n   " + str(user.weight) + " Kg"
        # measuring tape
        self.body_arms.text = "Arms: \n" + str(user.arms) + " cm"
        self.body_calfmuscles.text = "Calfmuscles: \n" + str(user.calfmuscles) + " cm"
        self.body_chest.text = "Chest: \n" + str(user.chest) + " cm"
        self.body_shoulders.text = "Shoulders: \n" + str(user.shoulders) + " cm"
        self.body_neck.text = "Neck: \n" + str(user.neck) + " cm"
        self.body_quads.text = "Quads: \n" + str(user.quads) + " cm"
        self.body_underarms.text = "Underarms: \n" + str(user.underarms) + " cm"
        self.body_waist.text = "Waist: \n" + str(user.waist) + " cm"
        self.body_hip.text = "Hip: \n" + str(user.hip) + " cm"
        # skin fold
        self.body_abdomen.text = "Abdomen: \n" + str(user.abdomen) + " mm"
        self.body_midaxilla.text = "Midaxilla: \n" + str(user.midaxilla) + " mm"
        self.body_pectoral.text = "Pectoral: \n" + str(user.pectoral) + " mm"
        self.body_quadriceps.text = "Quadriceps: \n" + str(user.quadriceps) + " mm"
        self.body_subscapular.text = "Subscapular: \n" + str(user.subscapular) + " mm"
        self.body_suprailiac.text = "Suprailiac: \n" + str(user.suprailiac) + " mm"
        self.body_triceps.text = "Triceps: \n" + str(user.triceps) + " mm"

        self.body_weight.canvas.ask_update()
        # measuring tape
        self.body_arms.canvas.ask_update()
        self.body_calfmuscles.canvas.ask_update()
        self.body_chest.canvas.ask_update()
        self.body_shoulders.canvas.ask_update()
        self.body_neck.canvas.ask_update()
        self.body_quads.canvas.ask_update()
        self.body_underarms.canvas.ask_update()
        self.body_waist.canvas.ask_update()
        self.body_hip.canvas.ask_update()
        # skin fold
        self.body_abdomen.canvas.ask_update()
        self.body_midaxilla.canvas.ask_update()
        self.body_pectoral.canvas.ask_update()
        self.body_quadriceps.canvas.ask_update()
        self.body_subscapular.canvas.ask_update()
        self.body_suprailiac.canvas.ask_update()
        self.body_triceps.canvas.ask_update()

    def on_index(self):
        index = self.carousel.index
        debug_print("index:" + str(index))
        self.update_date_label(index)

    def update_date_label(self, index):
        self.date.text = self.dates[index]
        self.date.canvas.ask_update()

    def on_enter(self, *args):
        if not self.carousel_updated:
            self.update_carousel()
        self.update_stats()
        self.update_date_label(0)

    def input_popup(self, body_part):
        PopupInputWidget().open_with_info(body_part)


class BodyStaticsScreen(Screen):
    body_height = ObjectProperty(None)
    # measuring tape
    body_ankle = ObjectProperty(None)
    body_wrist = ObjectProperty(None)
    body_head = ObjectProperty(None)
    # profile
    age = ObjectProperty(None)
    gender = ObjectProperty(None)

    def update_stats(self):
        debug_print('updating stats on screen, ' + database.get_latest_date())
        user.update()

        self.body_height.text = "Height:\n " + str(user.height) + " Cm"
        # measuring tape
        self.body_ankle.text = "Ankle:\n " + str(user.ankle) + " Cm"
        self.body_wrist.text = "Wrist:\n " + str(user.wrist) + " Cm"
        self.body_head.text = "Head:\n " + str(user.head) + " Cm"
        # profile
        self.age.text = "Age:\n " + str(user.age) + "\nYears"
        self.gender.text = "Gender:\n " + str(user.gender)

    def input_popup(self, body_part):
        PopupInputWidget().open_with_info(body_part)

    def on_enter(self, *args):
        self.update_stats()


class GraphScreen(Screen):
    graph = ObjectProperty(None)

    def update_graph(self):
        self.graph.ymax = 10
        # plot = MeshLinePlot(color=[1, 1, 0, 1])
        # plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
        #
        # plot1 = MeshLinePlot(color=[1, 0, 0, 1])
        # plot1.points = [(x, sin(x / 5.)) for x in range(0, 101)]

        plot2 = MeshLinePlot(color=[0, 0, 0, 1])

        plot2.points = [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                        (1, 7), (1, 8)]

        self.graph.add_plot(plot2)

    def on_enter(self, *args):
        self.update_graph()


class FitnessApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase = FireBase()
        self.local_id = ""
        self.id_token = ""

    def build(self):
        return gui

    def on_start(self):
        self.login()

    def on_stop(self):
        debug_print("app is shutting down")
        debug_print("upload data to firebase")
        database.upload_to_firebase()

    def login(self):
        # try logging in on online server
        try:
            debug_print("trying refresh token")
            with open("refresh_token.txt", "r") as file:
                refresh_token = file.read()

            # getting a new idToken using the refresh token
            id_token, local_id = self.firebase.exhange_refresh_token(refresh_token)
            self.id_token = id_token
            self.local_id = local_id

            self.load_data_firebase()

            debug_print("changing screen")
            self.change_screen('home_screen')
        except:
            debug_print("an error with refresh")
            # will go to login screen
            try:
                debug_print('Trying to load data from local file.')
                self.load_data_from_local_file_offlien()
                self.change_screen('home_screen')

            except:
                debug_print('cant load data from local file.')

    def logout(self):
        debug_print("logging out, saving data in firebase.")
        database.upload_to_firebase()

    def load_data_firebase(self):
        debug_print("function in app called to load data")
        database.load_data_online(self.local_id, self.id_token)

    def load_data_from_local_file_offlien(self):
        database.load_data_local()

    def change_screen(self, screen_name):
        # get screen manager form kv
        screen_manger = self.root.ids['screen_manager']
        screen_manger.current = screen_name
        debug_print("screen changed to" + screen_name)

    def update_layout(self):
        current_screen = self.root.ids['screen_manager'].current
        debug_print(current_screen)
        if current_screen == 'stats_screen':
            stats_screen.update_stats()
        if current_screen == 'home_screen':
            home_screen.layout.do_layout()


if __name__ == "__main__":
    from database import DataBase
    from inspect import currentframe

    debug = True


    def debug_print(string):
        cf = currentframe()
        if debug:
            print(string, "moduel:" + __name__, "line:" + str(cf.f_back.f_lineno))


    gui = Builder.load_file("main.kv")
    Window.size = (1440 / 4, 2560 / 4)  # setting the screen to same aspect ratio as galaxy s7

    database = DataBase()
    user = UserProfile()
    fitnessapp = FitnessApp()
    stats_screen = StatsScreen()
    home_screen = HomeScreen()
    fitnessapp.run()
