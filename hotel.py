
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
# from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

from kivymd.uix.picker import MDDatePicker
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
# from kivymd.uix.button import MDButton

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import datetime

import re
import pandas as pd
import numpy as np
import json
import ast
import math

from subprocess import Popen


def hotel_hour_round(x):
    # if greater than 0.25 hour aka 15 min add one hour
    if x%1 > 0.25:
        return math.ceil(x)
    else:
        return math.floor(x)

class MainWindow(ScreenManager):
    def __init__(self,  **kwargs):
        super(MainWindow, self).__init__(**kwargs)

class LoginWindow(Screen):
    def __init__(self, **kwargs):
        super(LoginWindow, self).__init__(**kwargs)

    def validate_user(self):
        user = self.ids.username_field
        pwd = self.ids.pwd_field
        info = self.ids.info

        uname = user.text
        passw = pwd.text

        if uname == '' or passw == '':
            # info.text = '[font=../fonts/ARIALUNI.TTF][color=#FF0000]需要帳號或密碼[/color][/font]'
            info.text = '[font=fonts/ARIALUNI.TTF][color=#FF0000]需要帳號或密碼[/color][/font]'
            self.parent.current = 'screen_primary'
        else:
            if uname == 'admin' and passw == 'admin':
                # info.text = '[font=../fonts/ARIALUNI.TTF][color=#00FF00]登入成功![/color][/font]'
                info.text = '[font=fonts/ARIALUNI.TTF][color=#00FF00]登入成功![/color][/font]'
                self.parent.current = 'screen_primary'
            else:
                # info.text = '[font=../fonts/ARIALUNI.TTF][color=#FF0000]帳號或密碼錯誤[/color][/font]'
                info.text = '[font=fonts/ARIALUNI.TTF][color=#FF0000]帳號或密碼錯誤[/color][/font]'

class PrimaryWindow(Screen):
    def __init__(self, **kwargs):
        super(PrimaryWindow, self).__init__(**kwargs)
        Clock.schedule_interval(self.validate_room_entry, 0.5)
        Clock.schedule_interval(self.room_layout,0.5)

        #checking room entry is right or not
        room_state = False

    def room_layout(self,dt):
        # black = (0,0,0,1)
        # blue =  (0,0,1,1)
        # red = (1,0,0,1)
        # yellow = (1,1,0,1)

        #get today's date in y/m/d hour/minute
        now = datetime.datetime.now()
        now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)

        #refresh room status
        self.ids.content.clear_widgets()

        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
       'checkout_time', 'etc', 'color']].fillna('').applymap(str)
        fifteen_min_til_checkout_lst = []
        for row_tup in rooms.iterrows():
            i = row_tup[0]
            room = row_tup[1]

            #check 15 min before checkout
            if (room['checkout_time'] != '') & (room['color'] != '(0.7,0.7,0,1)'):
                checkout_time = datetime.datetime.strptime(room['checkout_time'], '%Y/%m/%d %H:%M')
                fifteen_min_til_checkout = now + datetime.timedelta(minutes = 15)

                if (fifteen_min_til_checkout >= checkout_time) & (checkout_time >= now):
                    min_left = 15 - ((fifteen_min_til_checkout - checkout_time).total_seconds()/60)
                    #update room within rooms database
                    room['time_reminder'] = "剩{}分".format(int(min_left))

                #if past checkout time
                elif checkout_time < now:
                    min_over = (now - checkout_time).total_seconds()/60
                    room['time_reminder'] = '超{}分'.format(int(min_over))
                    #if overtime by more than 15 min add additional hour
                    if min_over > 15:
                        #to see how many hours over
                        hours_to_add = hotel_hour_round(min_over/60)
                        room['checkout_time'] = (checkout_time + datetime.timedelta(hours = hours_to_add)).strftime("%Y/%m/%d %H:%M")

                        if room['overtime'] == '':
                            room['overtime'] = str(int(float(hours_to_add)))
                        else:
                            room['overtime'] = str(int(float(room['overtime'])) + hours_to_add)

                        #when past more than 15 min checkout time remove time_reminder and add overtime
                        room['time_reminder'] = ''


            #keep track of hours when its being cleaned
            if room['color'] == '(0.7,0.7,0,1)':
                cleaned_checkin_time = datetime.datetime.strptime(room['checkin_time'], '%Y/%m/%d %H:%M')

                #total_seconds instead of seconds to grab the days too
                cleaned_time = (now - cleaned_checkin_time).total_seconds()
                cleaned_hour = math.floor(cleaned_time/60/60)
                cleaned_min = int(cleaned_time/60%60)

                room['checkout_time'] = (str(cleaned_hour)+ '時' + str(cleaned_min) + '分')

            if room['present'] == '1':
                chinese_present = '有'
            else:
                chinese_present = '無'

            if room['overtime'] == '':
                chinese_overtime = ''
            else:
                chinese_overtime = '加' + str(room['overtime']) + '時'

            text_to_add = str(room['id']
            + chinese_present
            + ','
            + room['time_reminder']
            + chinese_overtime
            +'\n'
            + room['name'] + '\n'
            + room['checkin_time']+ '\n'
            + room['checkout_time'] + '\n'
            + room['etc'])

            button = Button(text = text_to_add,
            background_color = ast.literal_eval(room['color']))
            self.ids.content.add_widget(button)

    def validate_room_entry(self,dt):

        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
       'checkout_time', 'etc', 'color']].fillna('').applymap(str)
        room = self.ids.room_selected.text

        room_exist = list(rooms['id'])

        if room in room_exist:
            room_state = True
            room_color = rooms[rooms['id'] == room].iloc[0]['color']

            #if rest or overnight
            if (room_color == '(1,0,0,1)') | (room_color == '(0,0,1,1)'):
                self.ids.rest_button.disabled = True
                self.ids.overnight_button.disabled = True
                self.ids.checkout_button.disabled = False
                self.ids.additional_hour_button.disabled = False
                self.ids.cleaned_button.disabled = True
                self.ids.finished_cleaning_button.disabled = True
            #if room is being cleaned
            elif room_color == '(0.7,0.7,0,1)':
                self.ids.rest_button.disabled = True
                self.ids.overnight_button.disabled = True
                self.ids.checkout_button.disabled = True
                self.ids.additional_hour_button.disabled = True
                self.ids.cleaned_button.disabled = True
                self.ids.finished_cleaning_button.disabled = False
            else:
                self.ids.rest_button.disabled = False
                self.ids.overnight_button.disabled = False
                self.ids.checkout_button.disabled = True
                self.ids.additional_hour_button.disabled = True
                self.ids.cleaned_button.disabled = False
                self.ids.finished_cleaning_button.disabled = True
        else:
            room_state = False
            self.ids.rest_button.disabled = True
            self.ids.overnight_button.disabled = True
            self.ids.checkout_button.disabled = True
            self.ids.additional_hour_button.disabled = True
            self.ids.cleaned_button.disabled = True
            self.ids.finished_cleaning_button.disabled = True

    def wipe_room_check(self):
        content = BoxLayout(orientation = 'horizontal')
        button_yes = Button(text = '確認', on_press = self.wipe_room)
        button_no = Button(text = '取消')
        content.add_widget(button_yes)
        content.add_widget(button_no)
        popup = Popup(content = content, title_font= 'fonts/ARIALUNI.TTF',
        title = '確認' + self.ids.room_selected.text + '要退房?',
        auto_dismiss=True, size_hint = (0.6,0.2))
        button_no.bind(on_release = popup.dismiss)
        button_yes.bind(on_release = popup.dismiss)
        popup.open()

    def wipe_room(self, *args):
        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
       'checkout_time', 'etc', 'color']].fillna('').applymap(str)
        room = self.ids.room_selected.text
        now = datetime.datetime.now()
        now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
        t_started_clean = now.strftime("%Y/%m/%d %H:%M")

        #grab index of where room is
        temp_i = rooms[rooms['id'] == room].index[0]
        room_to_clean = {'id': room,
        'present': '0',
        'time_reminder': '',
        'overtime': '',
        'name': '',
        'checkin_time': t_started_clean,
        'checkout_time': '',
        'etc': '',
        'color': '(0.7,0.7,0,1)'}

        rooms.loc[temp_i,rooms.columns] = room_to_clean
        rooms.to_csv('hotel_screen.csv',encoding='utf-8-sig')

    def clean_room(self):
        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
       'checkout_time', 'etc', 'color']].fillna('').applymap(str)
        room = self.ids.room_selected.text
        now = datetime.datetime.now()
        now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
        t_started_clean = now.strftime("%Y/%m/%d %H:%M")

        #grab index of where room is
        temp_i = rooms[rooms['id'] == room].index[0]
        room_to_clean = {'id': room,
        'present': '0',
        'time_reminder': '',
        'overtime': '',
        'name': '',
        'checkin_time': t_started_clean,
        'checkout_time': '',
        'etc': '',
        'color': '(0.7,0.7,0,1)'}

        rooms.loc[temp_i,rooms.columns] = room_to_clean
        rooms.to_csv('hotel_screen.csv',encoding='utf-8-sig')

    def finished_cleaning_room(self):
        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
       'checkout_time', 'etc', 'color']].fillna('').applymap(str)
        room = self.ids.room_selected.text

        #grab index of where room is
        temp_i = rooms[rooms['id'] == room].index[0]
        room_to_clean = {'id': room,
        'present': '0',
        'time_reminder': '',
        'overtime': '',
        'name': '',
        'checkin_time': '',
        'checkout_time': '',
        'etc': '',
        'color': '(0,0,0,1)'}

        rooms.loc[temp_i,rooms.columns] = room_to_clean
        rooms.to_csv('hotel_screen.csv',encoding='utf-8-sig')

    def shiftchange_check(self):
        content = BoxLayout(orientation = 'horizontal')
        button_yes = Button(text = '確認', on_press = self.shiftchange)
        button_no = Button(text = '取消')
        content.add_widget(button_yes)
        content.add_widget(button_no)
        popup = Popup(content = content, title_font= 'fonts/ARIALUNI.TTF',
        title = '確認要交班?',
        auto_dismiss=True, size_hint = (0.6,0.2))
        button_no.bind(on_release = popup.dismiss)
        button_yes.bind(on_release = popup.dismiss)
        popup.open()

    def shiftchange(self, *args):
        self.parent.current = "screen_login"

    def fill_data_to_add_change_screen(self, root_manager):
        '''rootmanager are for kivy button access screen manager'''
        #used id_add_change to access id from the add_change screen
        root_manager.id_add_change.add_change_room.text = self.ids.room_selected.text

        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
        'checkout_time', 'etc', 'color']].fillna('').applymap(str)
        room = rooms[rooms['id'] == self.ids.room_selected.text].iloc[0]

        overnight_color =  '(0,0,1,1)'
        rest_color = '(1,0,0,1)'

        if room['color'] == overnight_color:
            customer_data = pd.read_csv('overnight_customer_data.csv')[['id',
            'checkInDate', 'checkOutDate', 'dob', 'email', 'etc', 'person_id','name',
            'phone_number','price','rest_or_overnight',
            'days']].fillna('').applymap(str).reset_index(drop = True)
        elif room['color'] == rest_color:
            customer_data = pd.read_csv('rest_customer_data.csv')[['id',
            'checkInDate', 'checkOutDate','hour','dob','email','etc',
            'person_id', 'name', 'phone_number','price',
            'rest_or_overnight']].fillna('').applymap(str).reset_index(drop = True)

        #grab most recently entered room
        index_of_room = customer_data[customer_data['id'] == self.ids.room_selected.text].index[-1]

        #fill in pre-existing information to gui
        customer_data_spec_room = customer_data.iloc[index_of_room]
        root_manager.id_add_change.ids.add_change_room_checkInDate.text = customer_data_spec_room['checkInDate']
        root_manager.id_add_change.ids.add_change_room_checkOutDate.text = customer_data_spec_room['checkOutDate']
        root_manager.id_add_change.ids.add_change_room_dob.text = customer_data_spec_room['dob']
        root_manager.id_add_change.ids.add_change_room_email.text = customer_data_spec_room['email']
        root_manager.id_add_change.ids.add_change_room_etc.text = customer_data_spec_room['etc']
        root_manager.id_add_change.ids.add_change_room_id.text = customer_data_spec_room['person_id']
        root_manager.id_add_change.ids.add_change_room_name.text = customer_data_spec_room['name']
        root_manager.id_add_change.ids.add_change_room_phone_number.text = customer_data_spec_room['phone_number']
        root_manager.id_add_change.ids.add_change_room_price.text = customer_data_spec_room['price']

    def get_report(self):
        rest_customer_data = pd.read_csv('rest_customer_data.csv')[['id', 'checkInDate', 'checkOutDate','hour','dob','email','etc',
        'person_id', 'name', 'phone_number','price','rest_or_overnight']].fillna('').applymap(str).reset_index(drop = True)
        overnight_customer_data = pd.read_csv('overnight_customer_data.csv')[['id', 'checkInDate', 'checkOutDate', 'dob', 'email', 'etc',
        'person_id', 'name', 'phone_number','price','rest_or_overnight','days']].fillna('').applymap(str)

        #drop test first row test data
        overnight_to_merge = overnight_customer_data.iloc[1:]
        rest_to_merge = rest_customer_data.iloc[1:]

        report = overnight_to_merge.merge(rest_to_merge,how = 'outer').fillna('')
        report['checkInDate'] = report['checkInDate'].astype('datetime64')
        report['checkOutDate'] = report['checkOutDate'].astype('datetime64')
        report['price'] = report['price'].apply(lambda x: 0 if x == '' else int(float(x)))
        report = report.sort_values(by = 'checkInDate')
        now = datetime.datetime.now()

        daily_boo = report['checkInDate'].apply(lambda x: (x.year, x.month, x.day) == (now.year, now.month, now.day))
        daily_report = report[daily_boo].reset_index(drop = True)
        daily_report[['id','checkInDate','checkOutDate','price','rest_or_overnight','days','hour']].to_csv('daily_report.csv',encoding='utf-8-sig')

        #open excel
        p = Popen('daily_report.csv', shell=True)

    def rest_room_selected(self,root_manager):
        now = datetime.datetime.now()
        root_manager.id_rest.ids.rest_room.text = self.ids.room_selected.text
        root_manager.id_rest.ids.rest_room_checkInDate.text = now.strftime("%Y/%m/%d %H:%M")

    def overnight_room_selected(self,root_manager):
        now = datetime.datetime.now()
        root_manager.id_overnight.ids.overnight_room.text = self.ids.room_selected.text
        root_manager.id_overnight.ids.overnight_room_checkInDate.text = now.strftime("%Y/%m/%d %H:%M")

class OvernightWindow(Screen):
    # date_selected = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(OvernightWindow, self).__init__(**kwargs)
        Clock.schedule_interval(self.check_checkout_n_total, 0.1)

    def check_checkout_n_total(self,dt):

        try:
            #update total price
            if (self.ids.overnight_room_days.text != '') & (self.ids.overnight_room_price.text != ''):
                self.ids.overnight_total.text = str(int(self.ids.overnight_room_days.text) * int(self.ids.overnight_room_price.text))
            else:
                self.ids.overnight_total.text = ''

            #disable button if no checkout date
            if self.ids.overnight_room_checkOutDate.text == '':
                self.ids.overnight_confirm.disabled = True
            else:
                self.ids.overnight_confirm.disabled = False
        #if chinese char typed stop info from being entered
        except:
            self.ids.overnight_confirm.disabled = True

    def show_datepicker(self):
        picker = MDDatePicker(callback = self.got_date)
        picker.open()

    def got_date(self, the_date):

        date_selected = datetime.date(the_date.year,the_date.month,the_date.day)
        now = datetime.datetime.now()

        if now.date() >= date_selected:
            #3 pm to 11:59pm
            if now.time() >= datetime.time(15,0,0):
                self.text = (now.date() + datetime.timedelta(days = 1)).strftime("%Y/%m/%d") + ' 12:00'
            #12 am to 3 pm
            else:
                self.text = (now + datetime.timedelta(hours = 12)).strftime("%Y/%m/%d %H:%M")
            temp_day = 1

        else:
            self.text = date_selected.strftime("%Y/%m/%d") + ' 12:00'
            if now.time() >= datetime.time(15,0,0):
                temp_day = (date_selected - now.date()).days
            #12 am to 3 pm
            else:
                temp_day = (date_selected - now.date()).days + 1


        self.ids.overnight_room_checkOutDate.text = self.text
        self.ids.overnight_room_days.text = str(temp_day)

    def store_info(self):
        # reading in screen and customer data
        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
       'checkout_time', 'etc', 'color']].fillna('').applymap(str)

       # in case overnight_customer_data is deleted, create one from csv from scratch
        try:
            overnight_customer_data = pd.read_csv('overnight_customer_data.csv')[['id',
            'checkInDate', 'checkOutDate', 'dob', 'email', 'etc', 'person_id','name',
            'phone_number','price','rest_or_overnight',
            'days']].fillna('').applymap(str).reset_index(drop = True)
        except:
            overnight_customer_data = pd.DataFrame([{'id':'R000',
            'checkInDate':'2021/06/01 14:14',
            'checkOutDate':'2021/06/01 14:14',
            'days':'0',
            'dob':'1/2/1999',
            'email':'temp@gmail.com',
            'etc':'測試',
            'person_id':'A123456789',
            'name':'王王王',
            'phone_number':'0987-123-123',
            'price':'1000',
            'rest_or_overnight':'過夜/休息'}])
            overnight_customer_data.to_csv('overnight_customer_data.csv',encoding='utf-8-sig')
            overnight_customer_data = pd.read_csv('overnight_customer_data.csv')[['id',
            'checkInDate', 'checkOutDate', 'dob', 'email', 'etc', 'person_id','name',
            'phone_number','price','rest_or_overnight','days']].fillna('').applymap(str).reset_index(drop = True)

        #grab index of where room is
        temp_i = rooms[rooms['id'] == self.ids.overnight_room.text].index[0]

        #save customer info
        update_room = {'id': self.ids.overnight_room.text,
        'present': '0',
        'time_reminder': '',
        'overtime': '',
        'name': self.ids.overnight_room_name.text,
        'checkin_time': self.ids.overnight_room_checkInDate.text,
        'checkout_time': self.ids.overnight_room_checkOutDate.text,
        'etc': self.ids.overnight_room_etc.text,
        'color': '(0,0,1,1)'}

        #update hotel_screen to csv
        rooms.loc[temp_i,rooms.columns] = update_room
        rooms.to_csv('hotel_screen.csv',encoding='utf-8-sig')

        #input overnight customer to data
        update_customer_data = {}
        update_customer_data['id'] = self.ids.overnight_room.text
        update_customer_data['name'] = self.ids.overnight_room_name.text
        update_customer_data['person_id'] = self.ids.overnight_room_id.text
        update_customer_data['dob'] = self.ids.overnight_room_dob.text
        update_customer_data['etc'] = self.ids.overnight_room_etc.text
        update_customer_data['phone_number'] = self.ids.overnight_room_phone_number.text
        update_customer_data['email'] = self.ids.overnight_room_email.text
        update_customer_data['price'] = self.ids.overnight_room_price.text
        update_customer_data['checkInDate'] = self.ids.overnight_room_checkInDate.text
        update_customer_data['checkOutDate'] = self.ids.overnight_room_checkOutDate.text
        update_customer_data['days'] = self.ids.overnight_room_days.text
        update_customer_data['rest_or_overnight'] = '過夜'
        overnight_customer_data = overnight_customer_data.append(update_customer_data, ignore_index = True)
        overnight_customer_data.to_csv('overnight_customer_data.csv',encoding='utf-8-sig')

        #wipe input boxes
        self.ids.overnight_room.text = ''
        self.ids.overnight_room_name.text = ''
        self.ids.overnight_room_id.text = ''
        self.ids.overnight_room_dob.text = ''
        self.ids.overnight_room_etc.text = ''
        self.ids.overnight_room_phone_number.text = ''
        self.ids.overnight_room_email.text = ''
        self.ids.overnight_room_price.text = ''
        self.ids.overnight_room_checkInDate.text = ''
        self.ids.overnight_total.text = ''
        self.ids.overnight_room_checkOutDate.text = ''
        self.ids.overnight_room_days.text = ''

    def wipe_input_boxes(self):
        #wipe input boxes
        self.ids.overnight_room.text = ''
        self.ids.overnight_room_name.text = ''
        self.ids.overnight_room_id.text = ''
        self.ids.overnight_room_dob.text = ''
        self.ids.overnight_room_etc.text = ''
        self.ids.overnight_room_phone_number.text = ''
        self.ids.overnight_room_email.text = ''
        self.ids.overnight_room_price.text = ''
        self.ids.overnight_room_checkInDate.text = ''
        self.ids.overnight_total.text = ''
        self.ids.overnight_room_checkOutDate.text = ''
        self.ids.overnight_room_days.text = ''

class RestWindow(Screen):
    # rest_room_selected = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(RestWindow, self).__init__(**kwargs)

    def rest_spinner_clicked(self,value):
        if self.ids.rest_room_hour.text == '':
            self.ids.rest_confirm.disabled = True
        else:
            now = self.ids.rest_room_checkInDate.text
            now = datetime.datetime.strptime(now, '%Y/%m/%d %H:%M')
            hour = int(self.ids.rest_room_hour.text)
            self.ids.rest_room_checkOutDate.text = (now + datetime.timedelta(hours = hour)).strftime("%Y/%m/%d %H:%M")
            self.ids.rest_confirm.disabled = False

    def store_info(self):
        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
       'checkout_time', 'etc', 'color']].fillna('').applymap(str)

        # in case rest_customer_data is deleted, create one from csv from scratch
        try:
            rest_customer_data = pd.read_csv('rest_customer_data.csv')[['id', 'checkInDate', 'checkOutDate','hour','dob','email','etc',
            'person_id', 'name', 'phone_number','price','rest_or_overnight']].fillna('').applymap(str).reset_index(drop = True)
        except:
            rest_customer_data = pd.DataFrame([{'id':'R000',
            'checkInDate':'2021/06/01 14:14',
            'checkOutDate':'2021/06/01 14:14',
            'hour':'1',
            'dob':'12/26/1999',
            'email':'temp@gmail.com',
            'etc':'你好',
            'person_id':'A123456789',
            'name':'張張張',
            'phone_number':'0987-123-123',
            'price':'500',
            'rest_or_overnight':'過夜/休息'}])
            rest_customer_data.to_csv('rest_customer_data.csv',encoding='utf-8-sig')
            rest_customer_data = pd.read_csv('rest_customer_data.csv')[['id', 'checkInDate', 'checkOutDate','hour','dob','email','etc',
            'person_id', 'name', 'phone_number','price','rest_or_overnight']].fillna('').applymap(str).reset_index(drop = True)

        #grab index of where room is
        temp_i = rooms[rooms['id'] == self.ids.rest_room.text].index[0]

        #save customer info
        update_room = {'id': self.ids.rest_room.text,
        'present': '0',
        'time_reminder': '',
        'overtime': '',
        'name': self.ids.rest_room_name.text,
        'checkin_time': self.ids.rest_room_checkInDate.text,
        'checkout_time': self.ids.rest_room_checkOutDate.text,
        'etc': self.ids.rest_room_etc.text,
        'color': '(1,0,0,1)'}

        #update hotel_screen to csv
        rooms.loc[temp_i,rooms.columns] = update_room
        rooms.to_csv('hotel_screen.csv',encoding='utf-8-sig')


        #save rest_customer info
        update_customer_data = {}
        update_customer_data['id'] = self.ids.rest_room.text
        update_customer_data['name'] = self.ids.rest_room_name.text
        update_customer_data['person_id'] = self.ids.rest_room_id.text
        update_customer_data['dob'] = self.ids.rest_room_dob.text
        update_customer_data['etc'] = self.ids.rest_room_etc.text
        update_customer_data['phone_number'] = self.ids.rest_room_phone_number.text
        update_customer_data['email'] = self.ids.rest_room_email.text
        update_customer_data['price'] = self.ids.rest_room_price.text
        update_customer_data['checkInDate'] = self.ids.rest_room_checkInDate.text
        update_customer_data['checkOutDate'] = self.ids.rest_room_checkOutDate.text
        update_customer_data['hour'] = self.ids.rest_room_hour.text
        update_customer_data['rest_or_overnight'] = '休息'

        rest_customer_data = rest_customer_data.append(update_customer_data, ignore_index = True)
        rest_customer_data.to_csv('rest_customer_data.csv',encoding='utf-8-sig')

        self.ids.rest_room.text = ''
        self.ids.rest_room_name.text = ''
        self.ids.rest_room_id.text = ''
        self.ids.rest_room_dob.text = ''
        self.ids.rest_room_etc.text = ''
        self.ids.rest_room_phone_number.text = ''
        self.ids.rest_room_email.text = ''
        self.ids.rest_room_price.text = ''
        self.ids.rest_room_checkInDate.text = ''
        self.ids.rest_room_checkOutDate.text = ''
        self.ids.rest_room_hour.text = ''

    def wipe_input_boxes(self):
        #wipe input boxes
        self.ids.rest_room.text = ''
        self.ids.rest_room_name.text = ''
        self.ids.rest_room_id.text = ''
        self.ids.rest_room_dob.text = ''
        self.ids.rest_room_etc.text = ''
        self.ids.rest_room_phone_number.text = ''
        self.ids.rest_room_email.text = ''
        self.ids.rest_room_price.text = ''
        self.ids.rest_room_checkInDate.text = ''
        self.ids.rest_room_checkOutDate.text = ''
        self.ids.rest_room_hour.text = ''

class OneIntInput(TextInput):
    min_value = NumericProperty()
    max_value = NumericProperty()
    def __init__(self, *args, **kwargs):
        TextInput.__init__(self, *args, **kwargs)
        self.input_filter = 'int'
        self.multiline = False
    def insert_text(self, string, from_undo=False):
        new_text = self.text + string
        if new_text != "":
            regexp = re.compile(r'^[0-9]$')
            if regexp.search(new_text):
                if self.min_value <= float(new_text) <= self.max_value:
                    TextInput.insert_text(self, string, from_undo=from_undo)

class AddChangeWindow(Screen):
    #have ObjectProperty here to allow other screen to access widgets on this
    #screen
    add_change_room = ObjectProperty(None)
    add_change_room_checkInDate = ObjectProperty(None)
    add_change_room_checkOutDate = ObjectProperty(None)
    add_change_room_dob = ObjectProperty(None)
    add_change_room_email = ObjectProperty(None)
    add_change_room_etc = ObjectProperty(None)
    add_change_room_id = ObjectProperty(None)
    add_change_room_name = ObjectProperty(None)
    add_change_room_phone_number = ObjectProperty(None)
    add_change_room_price = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(AddChangeWindow, self).__init__(**kwargs)

    def add_time(self):
        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
        'checkout_time', 'etc', 'color']].fillna('').applymap(str)
        hotel_room_id = self.manager.get_screen('screen_primary').ids.room_selected.text
        #check if room id exist, because when exist screen room id will be wiped
        if len(rooms[rooms['id'] == hotel_room_id]) != 0:
            room = rooms[rooms['id'] == hotel_room_id].iloc[0]

            #user room['checkout_time'] to ensure the default checkout date doesn't change with different inputs
            checkOutDate = datetime.datetime.strptime(room['checkout_time'], '%Y/%m/%d %H:%M')

            #have 0 here in case one of the field is ''
            day = 0
            hour = 0
            if (self.ids.add_change_room_hour.text != ''):
                hour = int(self.ids.add_change_room_hour.text)
            if (self.ids.add_change_room_days.text != ''):
                day = int(self.ids.add_change_room_days.text)
            self.ids.add_change_room_checkOutDate.text = (checkOutDate + datetime.timedelta(days = day, hours = hour)).strftime("%Y/%m/%d %H:%M")

    def update_info(self):
        rooms = pd.read_csv('hotel_screen.csv')[['id', 'present', 'time_reminder', 'overtime', 'name', 'checkin_time',
        'checkout_time', 'etc', 'color']].fillna('').applymap(str)

        #grab room id from primary screen
        hotel_room_id = self.manager.get_screen('screen_primary').ids.room_selected.text
        room = rooms[rooms['id'] == hotel_room_id].iloc[0]

        overnight_color =  '(0,0,1,1)'
        rest_color = '(1,0,0,1)'

        #to see if its rest or overnight
        if room['color'] == overnight_color:
            customer_data = pd.read_csv('overnight_customer_data.csv')[['id',
            'checkInDate', 'checkOutDate', 'dob', 'email', 'etc', 'person_id','name',
            'phone_number','price','rest_or_overnight',
            'days']].fillna('').applymap(str).reset_index(drop = True)
        elif room['color'] == rest_color:
            customer_data = pd.read_csv('rest_customer_data.csv')[['id',
            'checkInDate', 'checkOutDate','hour','dob','email','etc',
            'person_id', 'name', 'phone_number','price',
            'rest_or_overnight']].fillna('').applymap(str).reset_index(drop = True)


        #SEE IF NEED TO SWITCH ROOM OR NOT
        if hotel_room_id == self.ids.add_change_room.text:
            #save customer info
            update_room = {'id': hotel_room_id,
            'present': '0',
            'time_reminder': '',
            'overtime': '',
            'name': self.ids.add_change_room_name.text,
            'checkin_time': self.ids.add_change_room_checkInDate.text,
            'checkout_time': self.ids.add_change_room_checkOutDate.text,
            'etc': self.ids.add_change_room_etc.text,
            'color': room['color']}

            #grab index of where room is
            temp_i = rooms[rooms['id'] == hotel_room_id].index[0]

            #update hotel_screen to csv
            rooms.loc[temp_i,rooms.columns] = update_room
            rooms.to_csv('hotel_screen.csv',encoding='utf-8-sig')

            #grab most recently entered room
            index_of_room = customer_data[customer_data['id'] == hotel_room_id].index[-1]

            #input changed data
            update_customer_data = {}
            update_customer_data['id'] = hotel_room_id
            update_customer_data['checkInDate'] = self.ids.add_change_room_checkInDate.text
            update_customer_data['checkOutDate'] = self.ids.add_change_room_checkOutDate.text
            update_customer_data['dob'] = self.ids.add_change_room_dob.text
            update_customer_data['email'] = self.ids.add_change_room_email.text
            update_customer_data['etc'] = self.ids.add_change_room_etc.text
            update_customer_data['person_id'] = self.ids.add_change_room_id.text
            update_customer_data['name'] = self.ids.add_change_room_name.text
            update_customer_data['phone_number'] = self.ids.add_change_room_phone_number.text
            update_customer_data['price'] = self.ids.add_change_room_price.text

            #to see if its rest or overnight
            if room['color'] == overnight_color:
                update_customer_data['rest_or_overnight'] = '過夜'
                update_customer_data['days'] = ''
                customer_data.iloc[index_of_room] = update_customer_data
                customer_data.to_csv('overnight_customer_data.csv',encoding='utf-8-sig')
            elif room['color'] == rest_color:
                update_customer_data['rest_or_overnight'] = '休息'
                update_customer_data['hour'] = ''
                customer_data.iloc[index_of_room] = update_customer_data
                customer_data.to_csv('rest_customer_data.csv',encoding='utf-8-sig')

        else:
            #change customer room and info
            update_room = {'id': self.ids.add_change_room.text,
            'present': '0',
            'time_reminder': '',
            'overtime': '',
            'name': self.ids.add_change_room_name.text,
            'checkin_time': self.ids.add_change_room_checkInDate.text,
            'checkout_time': self.ids.add_change_room_checkOutDate.text,
            'etc': self.ids.add_change_room_etc.text,
            'color': room['color']}

            #grab index of where room is
            original_room_i = rooms[rooms['id'] == self.ids.add_change_room.text].index[0]
            rooms.loc[original_room_i,rooms.columns] = update_room

            #change old room to clean
            now = datetime.datetime.now()
            now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
            t_started_clean = now.strftime("%Y/%m/%d %H:%M")

            #change old room to clean
            room_to_clean = {'id': hotel_room_id,
            'present': '0',
            'time_reminder': '',
            'overtime': '',
            'name': '',
            'checkin_time': t_started_clean,
            'checkout_time': '',
            'etc': '',
            'color': '(0.7,0.7,0,1)'}

            old_room_i = rooms[rooms['id'] == hotel_room_id].index[0]
            rooms.loc[old_room_i,rooms.columns] = room_to_clean
            rooms.to_csv('hotel_screen.csv',encoding='utf-8-sig')

            #change index of changed room (grabbing id from current scren)
            index_of_changed_customer_data = customer_data[customer_data['id'] == hotel_room_id].index[-1]

            #input changed data
            update_changed_room_customer_data = {}
            update_changed_room_customer_data['id'] = self.ids.add_change_room.text
            update_changed_room_customer_data['checkInDate'] = self.ids.add_change_room_checkInDate.text
            update_changed_room_customer_data['checkOutDate'] = self.ids.add_change_room_checkOutDate.text
            update_changed_room_customer_data['dob'] = self.ids.add_change_room_dob.text
            update_changed_room_customer_data['email'] = self.ids.add_change_room_email.text
            update_changed_room_customer_data['etc'] = self.ids.add_change_room_etc.text
            update_changed_room_customer_data['person_id'] = self.ids.add_change_room_id.text
            update_changed_room_customer_data['name'] = self.ids.add_change_room_name.text
            update_changed_room_customer_data['phone_number'] = self.ids.add_change_room_phone_number.text
            update_changed_room_customer_data['price'] = self.ids.add_change_room_price.text

            #to see if its rest or overnight
            if room['color'] == overnight_color:
                update_changed_room_customer_data['rest_or_overnight'] = '過夜'
                update_changed_room_customer_data['days'] = ''
                customer_data.iloc[index_of_changed_customer_data] = update_changed_room_customer_data
                customer_data.to_csv('overnight_customer_data.csv',encoding='utf-8-sig')
            elif room['color'] == rest_color:
                update_changed_room_customer_data['rest_or_overnight'] = '休息'
                update_changed_room_customer_data['hour'] = ''
                customer_data.iloc[index_of_changed_customer_data] = update_changed_room_customer_data
                customer_data.to_csv('rest_customer_data.csv',encoding='utf-8-sig')

        #wipe all input field
        self.ids.add_change_room.text = ''
        self.ids.add_change_room_name.text = ''
        self.ids.add_change_room_id.text = ''
        self.ids.add_change_room_dob.text = ''
        self.ids.add_change_room_etc.text = ''
        self.ids.add_change_room_phone_number.text = ''
        self.ids.add_change_room_email.text = ''
        self.ids.add_change_room_price.text = ''
        self.ids.add_change_room_checkInDate.text = ''
        self.ids.add_change_room_checkOutDate.text = ''
        self.ids.add_change_room_hour.text = ''
        self.ids.add_change_room_days.text = ''

    def wipe_input_boxes(self):
        #wipe all input field
        self.ids.add_change_room.text = ''
        self.ids.add_change_room_name.text = ''
        self.ids.add_change_room_id.text = ''
        self.ids.add_change_room_dob.text = ''
        self.ids.add_change_room_etc.text = ''
        self.ids.add_change_room_phone_number.text = ''
        self.ids.add_change_room_email.text = ''
        self.ids.add_change_room_price.text = ''
        self.ids.add_change_room_checkInDate.text = ''
        self.ids.add_change_room_checkOutDate.text = ''
        self.ids.add_change_room_hour.text = ''
        self.ids.add_change_room_days.text = ''

# kv = Builder.load_file('hotel.kv')

class HotelApp(MDApp):
    #need this global var here so both calender class and overnightWindow class
    #can access it. This is the only way I have found so far.
    #app.get_running_app, self.maanger both do not work
    checkOutDate = ''
    overnight_days = ''

    def build(self):
        return MainWindow()
    # sm = MainWindow()
    # def build(self):
    #   HotelApp.sm.add_widget(LoginWindow(name='screen_login'))
    #   HotelApp.sm.add_widget(PrimaryWindow(name='screen_primary'))
    #   HotelApp.sm.add_widget(OvernightWindow(name='screen_overnight'))
    #   HotelApp.sm.add_widget(RestWindow(name='screen_rest'))
    #   HotelApp.sm.add_widget(AddChangeWindow(name='screen_add_change', id = 'id_add_change'))
    #   return HotelApp.sm

if __name__ == '__main__':
    HotelApp().run()
