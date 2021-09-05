from __future__ import print_function
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from libdw import pyrebase
import pyzbar.pyzbar as pyzbar
import cv2
import time
from opencv import qrcodescan
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
# initialise firebase
url = 'https://test-4f06e.firebaseio.com/'
apikey = 'AIzaSyBKnZs78dnlgJDbMRq_xmxt90oV8xf1BQ4'
config = {"apiKey": apikey,"databaseURL": url,}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
# initialising kivy screens

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=170)
        emp3 = Label(text='', size_hint_x=1)
        self.layout.add_widget(emp3)
        # title
        header = Label(text='DFL', font_size=80, size_hint_x=4)
        self.layout.add_widget(header)
        # username entry field
        username_label = Label(text='Username:')
        self.layout.add_widget(username_label)
        self.username_input = TextInput(text = '',multiline = False)
        self.layout.add_widget(self.username_input)
        # password entry field
        password_label = Label(text='Password:')
        self.layout.add_widget(password_label)
        self.password_input = TextInput(text='',multiline = False,password = True)
        self.layout.add_widget(self.password_input)
        # create new account button
        signup = Button(text='Create\nnew', on_press=self.change_to_signup, font_size=20, size_hint_x=1)
        self.layout.add_widget(signup)
        # enter button
        enter = Button(text='Enter', on_press=self.check_valid, font_size=30, size_hint_x=1)
        self.layout.add_widget(enter)
        # add layout into screen
        self.add_widget(self.layout)
    #checking if valid username and password are entered
    def check_valid(self, value):
        user_input = self.username_input.text
        pw_input = self.password_input.text
        # checks username against all usernames in firebase
        all_users = db.child("users").get()
        if user_input in all_users.val():
            # checks input password against saved password
            pw = db.child('users').child(user_input).child('pw').get().val()
            if pw_input == pw:
                # change to menu screen
                self.manager.transition.direction = 'right'
                # modify the current screen to a different "name"
                self.manager.current = 'menu'
                # set username of current user of app
                global username
                username = user_input
            else:
                self.password_input.text = 'Wrong password'
        else:
            self.username_input.text = 'Wrong Username'
    # change to create new account screen
    def change_to_signup(self, value):
        self.manager.transition.direction = 'left'
        # modify the current screen to a different "name"
        self.manager.current = 'signup'

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=170)
        emp3 = Label(text='', size_hint_x=1)
        self.layout.add_widget(emp3)
        # title
        header = Label(text='New Account', font_size=50, size_hint_x=4)
        self.layout.add_widget(header)
        # username entry field
        username_label = Label(text='Username:')
        self.layout.add_widget(username_label)
        self.username_input = TextInput(text='',multiline = False)
        self.layout.add_widget(self.username_input)
        # password entry field
        password_label = Label(text='Password:')
        self.layout.add_widget(password_label)
        self.password_input = TextInput(text='',multiline = False, password = True)
        self.layout.add_widget(self.password_input)
        # back to login screen button
        back = Button(text='back \nto \nlogin', on_press=self.change_to_login, font_size=15, size_hint_x=1)
        self.layout.add_widget(back)
        # create account button
        create = Button(text='Create Account', on_press=self.check_valid_new, font_size=30, size_hint_x=1)
        self.layout.add_widget(create)
        # add layout to screen
        self.add_widget(self.layout)
    # change to login screen
    def change_to_login(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'login'
    # checks if input username and password are valid
    def check_valid_new(self,value):
        user_input = self.username_input.text
        pw_input = self.password_input.text
        # checks username against all usernames in firebase
        all_users = db.child("users").get()
        # check if password is entered
        if len(pw_input) == 0 or pw_input == 'Password required':
            self.password_input.text = 'Password required'
        # checks if username is too long
        elif len(user_input) > 10:
            self.username_input.text = 'Username too long, please try another username'
        # check if username is takem
        elif user_input not in all_users.val():
            # creating new user in firebase
            db.child('users').child(user_input).child('pw').set(pw_input)
            db.child('users').child(user_input).child('pref').set('off')
            db.child('users').child(user_input).child('log').set('free')
            # change to menu screen
            self.manager.transition.direction = 'right'
            # modify the current screen to a different "name"
            self.manager.current = 'menu'
        else:
            self.username_input.text = 'Username taken'
# menu screen
class GuiKivy(Screen):

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        layout = GridLayout(cols=2)
        # title
        header = Label(text='DFL', font_size=120, size_hint_x=5)
        layout.add_widget(header)
        emptyspace = Label(text=' ', size_hint_x=1)
        layout.add_widget(emptyspace)
        # choose machine to use
        progresslabel = Label(text='My Laundry', font_size=50)
        layout.add_widget(progresslabel)
        self.to_progress = Button(text='>', font_size=50)
        self.to_progress.bind(on_press=self.progress_page)
        layout.add_widget(self.to_progress)
        # checks predicted usage of machines
        predlabel = Label(text='Predictive Laundry', font_size=40)
        layout.add_widget(predlabel)
        self.to_pred = Button(text='>', font_size=50)
        self.to_pred.bind(on_press=self.pred_page)
        layout.add_widget(self.to_pred)
        # host a collective washing session or join one
        hitchlabel = Label(text='Laundry Hitch', font_size=50)
        layout.add_widget(hitchlabel)
        self.to_hitch = Button(text='>', font_size=50)
        self.to_hitch.bind(on_press=self.hitch_page)
        layout.add_widget(self.to_hitch)
        # indicate if you want people to help you take out your clothes
        basket_assist = Label(text='Basket Assist', font_size=50)
        layout.add_widget(basket_assist)
        # checks current preference
        pref = db.child('users').child(username).child('pref').get()
        if pref.val() == 'on':
            self.assist_toggle = ToggleButton(text=pref.val(), font_size=50, state='down')
        elif pref.val() == 'off':
            self.assist_toggle = ToggleButton(text=pref.val(), font_size=50, state='normal')
        self.assist_toggle.bind(on_press=self.assist)
        layout.add_widget(self.assist_toggle)
        self.add_widget(layout)
        # quit button
        quitlabel = Label(text='Quit', font_size=50)
        layout.add_widget(quitlabel)
        self.to_quit = Button(text='>', font_size=50)
        self.to_quit.bind(on_press=self.quitApp)
        layout.add_widget(self.to_quit)

    # changes to laundry screen or progress screen
    def progress_page(self, instance):
        # if using a machine, go to progress screen
        if db.child('users').child(username).child('log').get().val() != 'free':
            self.manager.transition.direction = 'left'
            # modify the current screen to a different "name"
            self.manager.current = 'progress'
        # if not useing machine, go to laundry screen
        else:
            self.manager.transition.direction = 'left'
            # modify the current screen to a different "name"
            self.manager.current = 'laundry'
    # changes to prediction screen
    def pred_page(self, instance):
        self.manager.transition.direction = 'left'
        # modify the current screen to a different "name"
        self.manager.current = 'pred'
    # changes to share machine screen
    def hitch_page(self, instance):
        self.manager.transition.direction = 'left'
        # modify the current screen to a different "name"
        self.manager.current = 'hitch'
    # changes basket assist preferences on firebase
    def assist(self, instance):
        if self.assist_toggle.text == 'off':
            self.assist_toggle.text = 'on'
            db.child('users').child(username).child('pref').set('on')
        else:
            self.assist_toggle.text = 'off'
            db.child('users').child(username).child('pref').set('off')
    # QUITS THE APP
    def quitApp(self,instance):
        App.get_running_app().stop()
# laundry screen
class LaundryScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = GridLayout(cols=6, row_force_default=True, row_default_height=100)
        # row1
        # back to menu button
        back = Button(text='<', on_press=self.change_to_menu, font_size=30, size_hint_x=1)
        self.layout.add_widget(back)
        # title
        header = Label(text='   My Laundry', font_size=40, size_hint_x=4)
        self.layout.add_widget(header)
        emp6 = Label(text='', size_hint_x=1)
        self.layout.add_widget(emp6)
        emp1_2 = Label(text='')
        self.layout.add_widget(emp1_2)
        emp1_3 = Label(text='')
        self.layout.add_widget(emp1_3)
        emp1_4 = Label(text='')
        self.layout.add_widget(emp1_4)
        # function to create machine buttons
        def button_maker(machine):
            button = Button(text=machine, background_normal='')
            # checks machine status from firebase
            if len(machine) == 2:
                status = db.child('machine').child(machine[0]).child(machine[1]).child('status').get().val()
                assist = db.child('machine').child(machine[0]).child(machine[1]).child('assist').get().val()
            elif len(machine) == 3:
                status = db.child('machine').child(machine[0]).child(machine[1:3]).child('status').get().val()
                assist = db.child('machine').child(machine[0]).child(machine[1:3]).child('assist').get().val()
            # if machine is not used
            if status == 'free':
                # button is green
                button.background_color = [0.259, 0.769, 0.09, 1]
                # button will activate machine when presed
                button.bind(on_press=self.busy_machine)
            # if machine is being used
            elif 'busy' in status:
                # button is red
                button.background_color = [0.76, 0.1, 0.01, 1]
            #     button does NOT activate machine when pressed
            # if machine is done but clothes not collected
            elif status == 'not collected':
                # but user allows other to take out clothes for him
                if assist == 'on':
                    # button is yellow
                    button.background_color = [1, 0.769, 0.09, 1]
                    #     button does NOT activate machine when pressed
                elif assist == 'off':
                    # button is red
                    button.background_color = [0.76, 0.1, 0.01, 1]
                    #     button does NOT activate machine when pressed
            return button
        # creating button for each machine: W for washing machine, D for dryer
        self.d1 = button_maker('D1')
        self.layout.add_widget(self.d1)
        self.e3_3 = Label(text='')
        self.layout.add_widget(self.e3_3)
        self.w1 = button_maker('W1')
        self.layout.add_widget(self.w1)
        self.w4 = button_maker('W4')
        self.layout.add_widget(self.w4)
        self.w8 = button_maker('W8')
        self.layout.add_widget(self.w8)
        # row4
        self.e4_1 = Label(text='')
        self.layout.add_widget(self.e4_1)
        self.d2 = button_maker('D2')
        self.layout.add_widget(self.d2)
        self.e4_3 = Label(text='')
        self.layout.add_widget(self.e4_3)
        self.w2 = button_maker('W2')
        self.layout.add_widget(self.w2)
        self.w5 = button_maker('W5')
        self.layout.add_widget(self.w5)
        self.w9 = button_maker('W9')
        self.layout.add_widget(self.w9)
        # row5
        self.e5_1 = Label(text='')
        self.layout.add_widget(self.e5_1)
        self.e5_2 = Label(text='')
        self.layout.add_widget(self.e5_2)
        self.e5_3 = Label(text='')
        self.layout.add_widget(self.e5_3)
        self.w3 = button_maker('W3')
        self.layout.add_widget(self.w3)
        self.w6 = button_maker('W6')
        self.layout.add_widget(self.w6)
        self.w10 = button_maker('W10')
        self.layout.add_widget(self.w10)
        # row6
        self.e6_1 = Label(text='')
        self.layout.add_widget(self.e6_1)
        self.d3 = button_maker('D3')
        self.layout.add_widget(self.d3)
        self.e6_3 = Label(text='')
        self.layout.add_widget(self.e6_3)
        self.e6_4 = Label(text='')
        self.layout.add_widget(self.e6_4)
        self.w7 = button_maker('W7')
        self.layout.add_widget(self.w7)
        self.w11 = button_maker('W11')
        self.layout.add_widget(self.w11)
        # row7
        self.e7_1 = Label(text='')
        self.layout.add_widget(self.e7_1)
        self.d4 = button_maker('D4')
        self.layout.add_widget(self.d4)
        self.d5 = button_maker('D5')
        self.layout.add_widget(self.d5)
        self.d6 = button_maker('D6')
        self.layout.add_widget(self.d6)
        self.e7_5 = Label(text='')
        self.layout.add_widget(self.e7_5)
        self.e7_6 = Label(text='')
        self.layout.add_widget(self.e7_6)
        # add layout to screen
        self.add_widget(self.layout)
    # function to start machine
    def busy_machine(self, instance):
        # activates camera to scan qr code and returns qrcode value once scanned
        self.machine = qrcodescan()
        # set time to zero
        self.fireval = 0
        self.timer = 0
        # checks for user's basket assist preference
        ass_pref = db.child('users').child(username).child('pref').get()
        # sets machine basket assist value to user's preference (turns on or off LED light)
        db.child('machine').child(self.machine[0]).child(self.machine[1]).child('assist').set(ass_pref.val())
        # starts machine
        db.child('machine').child(self.machine[0]).child(self.machine[1]).child('status').child('busy').set(0)
        # sets the user machine is used by to current user
        db.child('machine').child(self.machine[0]).child(self.machine[1]).child('user').set(username)
        # sets user's log to using current machine
        db.child('users').child(username).child('log').set(self.machine)
        # changes to progress screen
        self.manager.transition.direction = 'left'
        # modify the current screen to a different "name"
        self.manager.current = 'progress'
    # function to change to menu screen
    def change_to_menu(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'menu'
# progress screen
class ProgressScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        # initialise progressbar value and time value as zero
        self.fireval = 0
        self.timer = 0
        # initialise check progress loop
        self.update_bar_trigger = Clock.create_trigger(self.check_progress)
        self.layout = GridLayout(cols=3, row_force_default=True, row_default_height=100)
        # row 1
        # back to menu button
        back = Button(text='<', on_press=self.change_to_menu, font_size=30, size_hint_x=1)
        self.layout.add_widget(back)
        # title
        header = Label(text='My Laundry', font_size=40, size_hint_x=4)
        self.layout.add_widget(header)
        emp6 = Label(text='', size_hint_x=1)
        self.layout.add_widget(emp6)
        # row 2
        # sub title
        emp7 = Label()
        self.layout.add_widget(emp7)
        self.subhead = Label(text='My Progress', font_size=40)
        self.layout.add_widget(self.subhead)
        emp8 = Label()
        self.layout.add_widget(emp8)
        # progress bar
        emp9 = Label()
        self.layout.add_widget(emp9)
        self.bar = ProgressBar(value=round(self.fireval, 0), max=100)
        self.layout.add_widget(self.bar)
        self.time_left = Label(text='', font_size=15)
        # checks firebase for current machine used by user
        self.machine = db.child('users').child(username).child('log').get().val()
        # checks firebase if the machine is currently washing
        if db.child('machine').child(self.machine[0]).child(self.machine[1]).child('status').get().val() == 'busy':
            # gets the time machine has been running
            self.timer = db.child('machine').child(self.machine[0]).child(self.machine[1]).child('status').child('busy').get().val()
            # in case machine just started
            if self.timer == None:
                self.timer = 0
            # updates time left on screen
            self.time_left.text = '{} min left'.format(round(2 - self.timer))
        # checks if machine is done washing but clothes not collected
        elif db.child('machine').child(self.machine[0]).child(self.machine[1]).child('status').get().val() == 'not collected':
            # updates time left on screen to washing is done
            self.time_left.text = 'Done!'
        self.layout.add_widget(self.time_left)
        # add layout to screen
        self.add_widget(self.layout)
        # counter for progress bar
        self.counter = 0
        # if machine is still in use, loop to check for new status
        if db.child('users').child(username).child('log').get().val() != 'free':
            self.update_bar_trigger()
    # check progress loop
    def check_progress(self, x):
        # check firebase for current status
        reset = db.child('machine').child(self.machine[0]).child(self.machine[1]).child('status').get()
        # if machine is still washing
        if reset.val() == 'busy':
            # check firebase for how long it has been washing
            self.timer = db.child('machine').child(self.machine[0]).child(self.machine[1]).child('status')\
                .child('busy').get().val()
            # calculates washing percentage done
            if self.timer != None:
                self.fireval = self.timer/2 * 100
                self.counter+=1
            else:
                self.fireval = 0
            # updates progress bar and time left on screen
            if self.counter % 10 ==0:
                self.bar.value = round(self.fireval, 0)
                self.time_left.text = '{} min left'.format(round(2 - self.timer))
            # loops again to check progress
            self.update_bar_trigger()
        # if machine is done washing
        elif reset.val() == 'not collected':
            # updates time left to DONE on screen
            self.time_left.text = 'Done!'
            # stays as not collected until clothes are collected
            while reset.val() == 'not collected':
                # checks if clothes are STILL NOT COLLECTED
                reset = db.child('machine').child(self.machine[0]).child(self.machine[1]).child('status').get()
            # clothes are finally collected
            if reset.val() == 'free':
                # updates user log as not using machine
                db.child('users').child(username).child('log').set('free')
                # updates machine status as noone is using it
                db.child('machine').child(self.machine[0]).child(self.machine[1]).child('user').set('nil')
                # changes back to menu screen
                self.manager.transition.direction = 'right'
                # modify the current screen to a different "name"
                self.manager.current = 'menu'
        else:
            # raising error if machine status is abnormal
            print("machine status error:"+reset.val())
            App.get_running_app().stop()
    # function to change to menu screen
    def change_to_menu(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'menu'
# prediction screen
class PredictiveScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = GridLayout(cols=3, row_force_default=True, row_default_height=70)
        # back to menu button
        back = Button(text='<', on_press=self.change_to_menu, font_size=30, size_hint_x=1)
        self.layout.add_widget(back)
        # title
        header = Label(text='Prediction', halign='left', font_size=50, size_hint_x=4)
        self.layout.add_widget(header)
        emp3 = Label(text='', size_hint_x=1)
        self.layout.add_widget(emp3)
        self.add_widget(self.layout)
        # layout for input text
        self.layin = GridLayout(cols=2, row_force_default=True, row_default_height=75)
        empty = Label(text = '', size_hint_x = 2)
        self.layin.add_widget(empty)
        empty2 = Label(text='',size_hint_x = 4)
        self.layin.add_widget(empty2)
        # text input for desired time to predict machine usage
        self.qn = Label(text='Desired Time', font_size = 20)
        self.layin.add_widget(self.qn)
        # input in terms of 24hr clock e.g. 2359 (my favorite time xD)
        self.inpbox = TextInput(text = '24 hour clock, eg 2300', font_size = 20)
        self.layin.add_widget(self.inpbox)
        empty3 = Label()
        self.layin.add_widget(empty3)
        # sends request for prediction
        self.sendreq = Button(text = 'Send', font_size = 20, on_press = self.send_request)
        self.layin.add_widget(self.sendreq)
        self.add_widget(self.layin)
    # function to change to menu screen
    def change_to_menu(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'menu'
    # function to find prediction
    def send_request(self, instance):
        # takes value of text input
        req = self.inpbox.text
        # checks if text input is a 4 digit number
        if req.isnumeric() == False or len(req) != 4:
            self.sendreq.text = 'FORMAT ERROR: needs to be 4 numbers in a row'
        # checks if text input is a valid time
        elif int(req[0]) > 2 or int(req[2]) > 5 or int(req[:1]) not in range(24):
            self.sendreq.text = 'NUM ERROR: this is not a proper time'
        # starts prediction code
        else:
            # changes 24hr time to minutes in a day (0-1440 minutes)
            num_min = 0
            num_min += int(req[2:4])
            num_min += 60*(int(req[:2]))
            # list of machines to be checked
            mach_list = ['W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','D1','D2','D3','D4','D5','D6']
            mach_dict = {}
            # set up layout for prediction result
            self.layup = GridLayout(cols=5, row_force_default=True, row_default_height=80)
            # add empty labels for formatting
            for i in range(15):
                emptylol = Label()
                self.layup.add_widget(emptylol)
            # taking data from firebase for prediction
            for mach in mach_list:
                m_status = db.child('zpred').child(num_min).child(mach).get()
                # if chance of being used is larger than 66% (confirm used == red colour)
                if m_status.val() > 1:
                    result = [0.76, 0.1, 0.01, 1]
                # if chance of being used is 33% to 66% (maybe used == yellow colour)
                elif m_status.val()>0:
                    result = [0.87, 0.659, 0.02, 1]
                # if chances of being used is 0% to 33% (confirm free == green colour)
                else:
                    result = [0.259,0.769,0.09,1]
                # append result into dictionary
                mach_dict[mach] = result
                # add coloured buttons for each machine
                self.mach_butt = Button(text = mach, background_normal = '', background_color = result)
                self.layup.add_widget(self.mach_butt)
            # updates screen when prediction is done
            self.sendreq.text = 'Prediction done'
            self.add_widget(self.layup)
# Laundry Hitch screen (laundry sharing service)
class HitchScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs, on_enter = self.initialise)
        self.layout = GridLayout(cols=3, row_force_default=True, row_default_height=100)
        # back to menu button
        back = Button(text='<', on_press=self.change_to_menu, font_size=30, size_hint_x=1)
        self.layout.add_widget(back)
        # title
        header = Label(text='Laundry Hitch', font_size=40, size_hint_x=4)
        self.layout.add_widget(header)
        emp3 = Label(text='', size_hint_x=1)
        self.layout.add_widget(emp3)
        # add layout to screen
        self.add_widget(self.layout)
        # layout for looking for group/ host group buttons
        self.layin = GridLayout(cols=2, row_force_default=True, row_default_height=100)
        empty = Label()
        self.layin.add_widget(empty)
        empty2 = Label()
        self.layin.add_widget(empty2)
        # button to look for existing groups to join
        self.look = Button(text='Looking for Group', font_size =20, on_press=self.change_to_look)
        self.layin.add_widget(self.look)
        # button to create a group for others to join
        self.host = Button(text='Host Group', font_size = 20, on_press=self.change_to_host)
        self.layin.add_widget(self.host)
        # add layout to screen
        self.add_widget(self.layin)
    # (initialised on_enter of screen) changes buttons to looking for group/ hosting group
    def initialise(self,instance):
        self.look.text = 'Looking for Group'
        self.host.text = 'Hosting Group'
    # sets user to looking for group
    def change_to_look(self, value):
        # will call error if user is currently hosting a group
        if db.child('users').child(username).child('log').get().val() == 'host':
            self.look.text = 'ERROR: Currently Host'
            self.host.text='Hosting Group'
        #     changes screen to looking for group screen
        else:
            self.manager.transition.direction = 'left'
            # modify the current screen to a different "name"
            self.manager.current = 'look'
    # sets user to host of group
    def change_to_host(self, value):
        # stops those who are already in a group from going into another one
        if db.child('users').child(username).child('log').get().val() != 'host' and db.child('users').child(username).child('log').get().val() != 'free':
            self.look.text = 'Looking for Group'
            self.host.text = 'ERROR: Existing Lobby'
        # changes screen to host screen
        else:
            self.manager.transition.direction = 'left'
            # modify the current screen to a different "name"
            self.manager.current = 'host'
    # function to change back to menu screen
    def change_to_menu(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'menu'
# looking for group screen
class LookScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs, on_enter= self.start_looking)
        self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=100)
        # back to laundry hitch screen
        back = Button(text='<', on_press=self.back_to_hitch, font_size=30, size_hint_x=1)
        self.layout.add_widget(back)
        # title
        header = Label(text='Looking for Group', font_size=40, size_hint_x=5)
        self.layout.add_widget(header)
        # initialise check for group loop
        self.look_trigger = Clock.create_trigger(self.start_looking)
        self.add_widget(self.layout)
    # (initialised on_enter of screen) checks for creation of new groups and creates buttons for them
    def start_looking(self,instance):
        self.laylook = GridLayout(cols=2, row_force_default=True, row_default_height=50)
        # empty labels for formatting
        for i in range(2):
            e = Label(size_hint_x=1)
            e2 = Label(size_hint_x=5)
            self.laylook.add_widget(e)
            self.laylook.add_widget(e2)
        # checks firebase for list of groups available
        host_list = list(db.child('LFG').get().val())
        # creates a button for each group, updates amount of people who are inside and how many more to full group
        for i in host_list:
            emp = Label()
            self.laylook.add_widget(emp)
            loki = int(db.child('LFG').child(i).child('look').get().val())
            thor = int(db.child('LFG').child(i).child('present').get().val())
            host_inv = Button(id=i, text='{} is looking for {}/{}'.format(i, loki, loki + thor), size_hint_x=5)
            host_inv.bind(on_press=self.change_to_join)
            self.laylook.add_widget(host_inv)
        self.add_widget(self.laylook)
        # activates check for group loop for next update
        self.look_trigger()
    # updates user log to 'joined group'
    def change_to_join(self,instance):
        # updates log with group's host username (used as placeholder for the group's name)
        db.child('users').child(username).child('log').set(instance.id)
        # changes screen to joined screen
        self.manager.transition.direction = 'left'
        # modify the current screen to a different "name"
        self.manager.current = 'join'
    # function to change back to LaundryHitch screen
    def back_to_hitch(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'hitch'
# join group screen
class JoinLobbyScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs, on_enter=self.add_to_party)
        self.join_new = True
        # initialise check for full group loop
        self.join_trigger = Clock.create_trigger(self.add_to_party)
    # loop to check for full group
    def add_to_party(self,instance):
        # gets group host's username from firebase
        self.host_id = db.child('users').child(username).child('log').get().val()
        if self.host_id != 'free':
            # checks how many people are in the group
            if db.child('LFG').child(self.host_id).child('present').get().val() == None:
                current_party = 0
            else:
                current_party = int(db.child('LFG').child(self.host_id).child('present').get().val())
            # checks how many people still required for a full group
            if db.child('LFG').child(self.host_id).child('look').get().val() == None:
                left_party = 0
            else:
                left_party = int(db.child('LFG').child(self.host_id).child('look').get().val())
            # when user just enters group
            if self.join_new == True:
                # adds user into group
                db.child('LFG').child(self.host_id).child('members').child(username).set('join')
                # updates group status
                current_party += 1
                left_party -= 1
                db.child('LFG').child(self.host_id).child('present').set(current_party)
                db.child('LFG').child(self.host_id).child('look').set(left_party)
                # creates layout to display group 1
                self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=100)
                # button to change back to looking for group screen
                back = Button(text='<', on_press=self.back_to_look, font_size=30, size_hint_x=1)
                self.layout.add_widget(back)
                # title
                header = Label(text='''{}'s party'''.format(self.host_id), font_size=30, size_hint_x=5)
                self.layout.add_widget(header)
                # add layout to screen
                self.add_widget(self.layout)
            # create layout to display group 2
            self.layjoin = GridLayout(cols=3, row_force_default=True, row_default_height=100)
            self.layjoin.clear_widgets()
            # empty labels for formatting
            em = Label(size_hint_x=1)
            self.layjoin.add_widget(em)
            em2 = Label(size_hint_x=2.5)
            self.layjoin.add_widget(em2)
            em3 = Label(size_hint_x=2.5)
            self.layjoin.add_widget(em3)
            # leave group button
            self.leave = Button(text='Leave', on_press=self.leave_group)
            self.layjoin.add_widget(self.leave)
            # label to show current number of people in group
            self.currentp = Label(text='Current: {}/{}'.format(current_party, current_party + left_party))
            self.layjoin.add_widget(self.currentp)
            # label to show how many people left to form full group
            self.leftp = Label(text='Left with: {}/{}'.format(left_party, current_party + left_party))
            self.layjoin.add_widget(self.leftp)
            # add layout to screen
            self.add_widget(self.layjoin)
            # create layout to display group 3
            self.laypend = GridLayout(cols=2, row_force_default=True, row_default_height=50)
            self.laypend.clear_widgets()
            # empty labels for formatting
            for i in range(4):
                e = Label(size_hint_x=1)
                self.laypend.add_widget(e)
                e2 = Label(size_hint_x=5)
                self.laypend.add_widget(e2)
            # gets list of group members from firebase
            party_members = list(db.child('LFG').child(self.host_id).child('members').get().val())
            # displays all members currently in group
            for i in party_members:
                self.part_empty = Label()
                self.laypend.add_widget(self.part_empty)
                self.p_member = Label(text=i)
                self.laypend.add_widget(self.p_member)
            # checks if host proceeds with group meetup after full group
            # (host will gain the option to proceed after group is full)
            if db.child('LFG').child(self.host_id).child('full').get().val() == 'True':
                em = Label()
                self.laypend.add_widget(em)
                # displays notification to members to meet at laundry room
                self.LEGGO = Label(text='AUTOBOTS, ROLL OUT to Laundry Room in 5 min!')
                self.laypend.add_widget(self.LEGGO)
            # adds layout to screen
            self.add_widget(self.laypend)
            # changes after user enters group for first time
            self.join_new = False
        # activate check for full group loop
        self.join_trigger()
    # function to change back to looking for group screen
    def back_to_look(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'look'
    # function to leave group
    def leave_group(self, instance):
        # gets number of people in group from firebase
        current_party = int(db.child('LFG').child(self.host_id).child('present').get().val())
        left_party = int(db.child('LFG').child(self.host_id).child('look').get().val())
        # updates number of people in group after leaving
        current_party-=1
        left_party+=1
        db.child('LFG').child(self.host_id).child('present').set(current_party)
        db.child('LFG').child(self.host_id).child('look').set(left_party)
        # removes user from group list
        db.child('LFG').child(self.host_id).child('members').child(username).remove()
        # sets user's log back to free
        db.child('users').child(username).child('log').set('free')
        self.laypend.clear_widgets()
        self.remove_widget(self.laypend)
        self.layjoin.clear_widgets()
        self.remove_widget(self.layjoin)
        self.join_new = True
        # changes back to looking for group screen
        self.manager.transition.direction = 'left'
        # modify the current screen to a different "name"
        self.manager.current = 'look'
# host screen
class HostScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs, on_enter = self.initialise)
        self.host_new = True
        # initialise loop to check if user is host or not
        self.host_trigger = Clock.create_trigger(self.initialise)
    # (initialised on_enter of screen) loop to check if user is host or not
    def initialise(self, instance):
        # if user enters screen for the first time
        if self.host_new == True:
            # initialise layout 1
            self.layout = GridLayout(cols=3, row_force_default=True, row_default_height=100)
            # back to laundry hitch screen
            back = Button(text='<', on_press=self.back_to_hitch, font_size=30, size_hint_x=1)
            self.layout.add_widget(back)
            # title
            header = Label(text='Hosting Group', font_size=40, size_hint_x=4)
            self.layout.add_widget(header)
            emp3 = Label(text='', size_hint_x=1)
            self.layout.add_widget(emp3)
            self.add_widget(self.layout)
            # initialise layout 2
            self.layhost = GridLayout(cols=3, row_force_default=True, row_default_height=100)
            self.layhost.clear_widgets()
            # empty labels for formatting
            emp1 = Label(size_hint_x=1)
            self.layhost.add_widget(emp1)
            emp2 = Label(size_hint_x=2.5)
            self.layhost.add_widget(emp2)
            emp3 = Label(size_hint_x=2.5)
            self.layhost.add_widget(emp3)
            emp4 = Label()
            self.layhost.add_widget(emp4)
            # dropdown list for how many people already present
            person_host_present = DropDown()
            self.p1 = Button(text='{}'.format(1), size_hint_y=None)
            self.p2 = Button(text='{}'.format(2), size_hint_y=None)
            self.p3 = Button(text='{}'.format(3), size_hint_y=None)
            self.l1 = Button(text='{}'.format(1), size_hint_y=None)
            self.l2 = Button(text='{}'.format(2), size_hint_y=None)
            self.l3 = Button(text='{}'.format(3), size_hint_y=None)
            present_list = [self.p1, self.p2, self.p3]
            look_list = [self.l1, self.l2, self.l3]
            # set how many people in group
            self.howmany = Button(text='number present?')
            self.howmany.bind(on_release=person_host_present.open)
            for idx in range(3):
                x = present_list[idx]
                x.bind(on_release=lambda x: person_host_present.select(x.text))
                person_host_present.add_widget(x)
            person_host_present.bind(on_select=lambda instance, x: setattr(self.howmany, 'text', x))
            self.layhost.add_widget(self.howmany)
            # dropdown list for how many people you are looking for
            person_host_look = DropDown()
            self.lookfor = Button(text='looking for?')
            self.lookfor.bind(on_release=person_host_look.open)
            for idx in range(3):
                x = look_list[idx]
                x.bind(on_release=lambda x: person_host_look.select(x.text))
                person_host_look.add_widget(x)
            person_host_look.bind(on_select=lambda instance, x: setattr(self.lookfor, 'text', x))
            self.layhost.add_widget(self.lookfor)
            # add layout to screen
            self.add_widget(self.layhost)
        # initialise layout 3
        self.laybutt = GridLayout(cols=2, row_force_default=True, row_default_height=100)
        self.laybutt.clear_widgets()
        # empty labels for formatting
        for i in range(2):
            em = Label(size_hint_x=3.5)
            self.laybutt.add_widget(em)
            em2 = Label(size_hint_x=2.5)
            self.laybutt.add_widget(em2)
        em3 = Label()
        self.laybutt.add_widget(em3)
        # set user to become host on press if not already host
        if db.child('users').child(username).child('log').get().val() == 'free':
            self.send_base = Button(text='Send Request', on_press=self.change_to_hobby)
        #     if already host, then returns user to his group
        elif db.child('users').child(username).child('log').get().val() == 'host':
            self.send_base = Button(text='Back to Lobby', on_press=self.back_to_hobby)
            self.lookfor.text = '-'
            self.howmany.text = '-'
        self.laybutt.add_widget(self.send_base)
        self.host_new = False
        # loops to check if user is host or not
        self.host_trigger()
        # add layout to screen
        self.add_widget(self.laybutt)
    # function to change back to host lobby screen
    def back_to_hobby(self,instance):
        self.manager.transition.direction = 'left'
        # modify the current screen to a different "name"
        self.manager.current = 'hobby'
    # function to change back to laundry hitch screen
    def back_to_hitch(self,instance):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'hitch'
    # function to create host lobby and change to that screen
    def change_to_hobby(self, instance):
        present = self.howmany.text
        looking = self.lookfor.text
        # check if user seleced 2 numbers
        if present == 'how many?' or looking == 'looking for?':
            self.send_base.text = 'ERROR: select two numbers'
        #    creating host lobby
        else:
            # change user log to host
            db.child('users').child(username).child('log').set('host')
            # removes user from member list
            db.child('LFG').child(username).child('members').remove()
            # if creating group with more then 1 person
            if int(present) > 1:
                # updating the amount of people in the created group
                db.child('LFG').child(username).child('members').child(
                    '{} + {} more'.format(username, int(present) - 1)).set('host')
            else:
                # creating group with one person only
                db.child('LFG').child(username).child('members').child(username).set('host')
            # setting parameters for a group
            db.child('LFG').child(username).child('full').set('False')
            db.child('LFG').child(username).child('present').set(present)
            db.child('LFG').child(username).child('look').set(looking)
            # changes to host lobby screen
            self.manager.transition.direction = 'left'
            # modify the current screen to a different "name"
            self.manager.current = 'hobby'
# host lobby screen
class HostLobbyScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs, on_enter=self.start_lobby)
        self.hobby_new = True
        # initialising loop to check if group is full
        self.hobby_trigger = Clock.create_trigger(self.start_lobby)
    # (initialised on_enter of screen) loop to update group status
    def start_lobby(self,instance):
        # if it is the first loop
        if self.hobby_new == True:
            # layout 1
            self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=100)
            # back to host screen button
            back = Button(text='<', on_press=self.back_to_host, font_size=30, size_hint_x=1)
            self.layout.add_widget(back)
            # title
            header = Label(text='''{}'s party'''.format(username), font_size=30, size_hint_x=5)
            self.layout.add_widget(header)
            self.add_widget(self.layout)
        # layout 2
        self.layhobby = GridLayout(cols=3, row_force_default=True, row_default_height=100)
        self.layhobby.clear_widgets()
        # empty labels for formatting
        em = Label(size_hint_x=1)
        self.layhobby.add_widget(em)
        em2=Label(size_hint_x=2.5)
        self.layhobby.add_widget(em2)
        em3=Label(size_hint_x=2.5)
        self.layhobby.add_widget(em3)
        # cancel group button
        self.cancel = Button(text='Cancel', font_size=15, on_press=self.cancel_group)
        self.layhobby.add_widget(self.cancel)
        # getting group data from firebase
        current_party = db.child('LFG').child(username).child('present').get().val()
        left_party = db.child('LFG').child(username).child('look').get().val()
        # correcting for NoneType error
        if current_party == None or left_party == None:
            current_party = 0
            left_party = 0
        if current_party != 0:
            # creating label to display how many currently people in group
            self.current = Label(text='Current: {}/{}'.format(int(current_party), int(current_party) + int(left_party)))
            self.layhobby.add_widget(self.current)
            self.left = Label(text='Left with: {}/{}'.format(int(left_party), int(current_party) + int(left_party)))
            self.layhobby.add_widget(self.left)
        self.add_widget(self.layhobby)
        # layout 3
        self.laywait = GridLayout(cols=2, row_force_default=True, row_default_height=50)
        self.laywait.clear_widgets()
        # empty labels for formatting
        for i in range(4):
            e = Label(size_hint_x = 1)
            self.laywait.add_widget(e)
            e2 = Label(size_hint_x=5)
            self.laywait.add_widget(e2)
        # crating list of group members from firebase
        if db.child('LFG').child(username).child('members').get().val() != None:
            party_members = list(db.child('LFG').child(username).child('members').get().val())
        else:
            party_members = ['']
        for i in party_members:
            emp = Label()
            self.laywait.add_widget(emp)
            slot = Label(text = i)
            self.laywait.add_widget(slot)
        # if the group is full, host will see this
        if int(left_party) == 0 and int(current_party) != 0:
            em = Label()
            self.laywait.add_widget(em)
            # button to proceed to call for group meetup
            self.proceed = Button(text='Proceed! Meet at the Laundry Room in 5min!', on_press=self.proceeding)
            self.laywait.add_widget(self.proceed)
        # host will press this once everybody has met and put in their laundry
        if db.child('LFG').child(username).child('full').get().val() == 'True':
            em2 = Label()
            self.laywait.add_widget(em2)
            self.done = Button(text='Press when everyone is done!', on_press=self.cancel_group)
            self.laywait.add_widget(self.done)
        self.hobby_new = False
        # loop to update host lobby
        self.hobby_trigger()
        # add layout to screen
        self.add_widget(self.laywait)
    # sets group capacity to full
    def proceeding(self, instance):
        db.child('LFG').child(username).child('full').set('True')
    # function to cancel group
    def cancel_group(self, instance):
        # deletes group and resets user's log to free
        db.child('LFG').child(username).remove()
        db.child('users').child(username).child('log').set('free')
        self.laywait.clear_widgets()
        self.remove_widget(self.laywait)
        self.hobby_new = True
        # changes back to host screen
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'host'
    # function to change back to host screen
    def back_to_host(self, value):
        self.manager.transition.direction = 'right'
        # modify the current screen to a different "name"
        self.manager.current = 'host'
# initialise App
class SwitchScreenApp(App):
    global username
    username = 'ID'
    # compile all screens
    def build(self):
        sm = ScreenManager()
        ls = LoginScreen(name='login')
        ss = SignupScreen(name='signup')
        ms = GuiKivy(name='menu')
        st = ProgressScreen(name='progress')
        pr = PredictiveScreen(name='pred')
        ht = HitchScreen(name='hitch')
        laundry = LaundryScreen(name='laundry')
        lk = LookScreen(name='look')
        lb = JoinLobbyScreen(name='join')
        hs = HostScreen(name='host')
        hl = HostLobbyScreen(name='hobby')
        sm.add_widget(ls)
        sm.add_widget(ss)
        sm.add_widget(ms)
        sm.add_widget(laundry)
        sm.add_widget(st)
        sm.add_widget(pr)
        sm.add_widget(ht)
        sm.add_widget(lk)
        sm.add_widget(lb)
        sm.add_widget(hs)
        sm.add_widget(hl)
        sm.current = 'login'
        return sm

# run App
if __name__ == '__main__':
    SwitchScreenApp().run()
