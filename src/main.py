from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
import json 
from kivymd.toast import toast
from plyer import gps
from kivy.clock import Clock,mainthread
from kivy.animation import Animation
import time
import requests
#the url value-useful for requests.
url="http://trackitdev.herokuapp.com"
# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
# Declare both screens
kv="""
<login>:
    MDFloatLayout:
        MDToolbar:
            title: "Login"
            pos_hint: {"top":1}
        MDTextField:
            id:user
            hint_text:"ID"
            helper_text:"ID"
            helper_text_mode:"on_error"
            md_bg_color:app.theme_cls.accent_color
            pos_hint: {"top":.7}
            required:True
        MDTextField:
            id:pwd
            hint_text:"Password"
            helper_text:"Password"
            password:True
            max_text_length:30
            helper_text_mode:"on_error"
            icon_left: 'key'
            pos_hint: {"top":.5}
            required:True
        MDRectangleFlatButton:
            text:"Login"
            pos_hint:{'center_x':.5 ,'top':.4}
            on_release:root.validate()
<main>:
    MDFloatLayout:
        MDRectangleFlatButton:
            id:track
            pos_hint:{'center_x':.5,'center_y':.5}
            text:"[b]Start[/b]"
            on_release:root.start()
"""
class login(MDScreen):
    def __init__(self,*args,**kwargs):
        super(MDScreen,login).__init__(self,*args,**kwargs)
    def validate(self):
        def val(user,pwd):
            #Check if password is correct.
            try:
                resp=requests.post(url+"/login",data={'id':user,'password':pwd})

                if(resp.json().get("success")==1):
                    return True
                return False
            except:
                toast("Check your internet connection!")

        pwd=self.ids.pwd.text
        user=self.ids.user.text
        print(user,pwd)
        if(self.l()):
            #try to run a spinner.
            if(val(user,pwd)):
                 self.manager.current='main'
            else:
                toast('Wrong password/Username!')
    def l(self):
        if(len(self.ids.user.text)<1):
            self.ids.user.error=True
            toast("Input your username")
            return False
        if(len(self.ids.pwd.text)<1):
            self.ids.pwd.error=True
            toast("Input your password")
            return False
        return True
class main(MDScreen):
    on=False
    def __init__(self,**args):
        super().__init__(**args)
    @mainthread
    def on_location(self,**kwargs):
        #tryna put the location on the website
        print(kwargs['lon'],kwargs['lat'])
        lon=kwargs['lon']
        lat=kwargs['lat']
        try:
            resp=requests.post(url+"/stream",data={'lat':lat,'lon':lon})
            print(resp.text)
            if(resp.json.get("success")==0):
            	toast('An error occured!')
        except:
            toast("Check your internet connection!")
    @mainthread
    def on_status(self,*args,**kwargs):
        #for now.
        print(args,kwargs)
        pass
    def get_data(self,dt):
        pass
        #get the open heavens info and put the results in global variables
    def on_enter(self):
        Clock.schedule_once(self.get_data,1)
    def start(self):
        if(self.on== False):
            #if tracking is yet to start.
            toast("""Tracking;
        Do have a nice trip.""")
            self.ids.track.text="[b]Stop[/b]"
            self.on=True
            try:
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                gps.start()
            except:
            	toast('GPS not available for your device')
            	time.sleep(5)
            	exit(0)
        else:
            #tracking has started.
            toast("Thanks for using TrackIT.Do buy me a coffee.")
            self.ids.track.text="[b]Start[/b]"
            self.on=False
            gps.stop()
            return

        #start tracking
class TrackitApp(MDApp):
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')
    def build(self):
        #check if  gps is  available.
# Create the screen manager
        Builder.load_string(kv)
        sm = ScreenManager()
        sm.add_widget(login(name='login'))
        sm.add_widget(main(name='main'))
        sm.current='login'
        return sm
if __name__ == '__main__':
    TrackitApp().run()
