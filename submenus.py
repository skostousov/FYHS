from menu import Menu
import rich
import time
import os  #
import copy
import map
from database import Database
from datetime import datetime
import requests
import random

profile_name = None


class MainMenu(Menu):#main menu which provides two options, posts and map

  def __init__(self, queue, classname):
    self.choices = {"1": ("Posts", self.posts), "2": ("Map", self.map)}
    super().__init__(self.choices, queue, classname)
    self.database = Database()

  def posts(self):#calls the Post Menu class when posts is selected
    self.postsmenu = PostsMenu(self.que, "Posts Menu", self.database)
    self.postsmenu.run()

  def process_for_map(self):#this processes sql data into a list of dictionaries for display on the map
    self.entry_data = self.database.fetch_all_entries()
    addresses = [
        f"{entry[4]}, {entry[6]}, {entry[7]}, {entry[8]}, {entry[5]}"
        for entry in self.entry_data
    ]
    lat_lngs = self.convert_addresses_to_coords(
        addresses, "AIzaSyCmkfd90413qg-nCV3wKeHBHw7QPP7d8uM")#arg includes the address and api key for google api to fetch coordinates
    self.redacted_points = []
    for entry, (lat, lng) in zip(self.entry_data, lat_lngs):
      self.extrainfoentrydict = {}
      self.extrainfoentrydict["date"] = entry[11]
      self.extrainfoentrydict["time"] = entry[12]
      self.entrydict = {}
      self.entrydict["transparency"] = self.convert_to_transparency(
          entry[11], entry[12])#age of post is converted to transparency
      self.entrydict["radius"] = self.convert_to_radius(entry[9])#amount of upvotes/severity is converted to radius
      self.entrydict["type"] = entry[10]
      self.entrydict["lat"], self.entrydict["long"] = lat, lng
      self.entrydict["id"] = entry[0]
      self.entrydict["title"] = entry[2]
      self.redacted_points.append((self.entrydict, self.extrainfoentrydict))
    return self.redacted_points

  def convert_addresses_to_coords(self, addresses, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    lat_lngs = []
    for address in addresses:
      params = {"address": address, "key": api_key}
      response = requests.get(base_url, params=params)
      try:
        result = response.json()["results"][0]
        lat = result["geometry"]["location"]["lat"]
        lng = result["geometry"]["location"]["lng"]
        lat_lngs.append((lat, lng))
      except KeyError:
        print("Error: 'results' key not found in response")
        print("Response:", response.json())
        lat_lngs.append((None, None))
    return lat_lngs

  def convert_to_radius(self, upvotes):  #generated with the help of AI
    base_radius = 6
    max_radius = 15
    expected_upvotes_for_max_radius = 100

    if int(upvotes) <= 0:
      return base_radius
    elif int(upvotes) >= expected_upvotes_for_max_radius:
      return max_radius
    else:
      return int(base_radius + (upvotes / expected_upvotes_for_max_radius) *
                 (max_radius - base_radius))

  def convert_to_transparency(self, date, time):  #generated with the help of AI
    # Convert date and time to a single datetime object
    self.datetime_object = datetime.strptime(date + " " + time, "%d/%m/%Y %H")
    # Calculate the time difference between now and the datetime object
    self.time_difference = datetime.now() - self.datetime_object
    self.transparency = max(0, min((180 - self.time_difference.days) / 180, 1))
    return self.transparency

  def map(self):
    x, y, zm = self.get_details()
    self.data = self.process_for_map()
    self.dataformap = []
    for i in self.data:
      self.dataformap.append(i[0])
    self.mapobject = map.Map(self.dataformap, x, y, zm)
    self.mapobject.update_html()
    self.mapobject.run()#runs the map
    mapmenu = MapMenu(self.que, "Map Menu", self.data)
    mapmenu.run()#opens map menu to filter various values (like type, earliest data) 

  def get_details(self):#sets the start x and y vaues and zoom value for map
    start_x = 0
    start_y = 0
    zoom = 2
    return start_x, start_y, zoom


class MapMenu(Menu):

  def __init__(self, queue, classname, data):
    self.choices = {
        "1": ("filter by type", self.filter_by_type),
        "2": ("filter by date", self.filter_by_date),
        "3": ("display all", self.display_all)
    }
    self.data = data
    super().__init__(self.choices, queue, classname)

  def filter_by_type(self):
    self.type = PostsMenu(self.que, "temp posts menu", None).get_type()#borrows post menu function to get user input for type (stored as color value)
    self.filtered_data = [
        entry[0] for entry in self.data if entry[0]["type"] == self.type
    ]
    self.mapobject = map.Map(self.filtered_data, 0, 0, 2)
    self.mapobject.update_html()
    self.mapobject.run()

  def filter_by_date(self):
    input_date = input("Enter the most recent date (format: 'DD/MM/YYYY'): ")
    self.filtered_data = [
        entry[0] for entry in self.data
        if datetime.strptime(entry[1]["date"], "%d/%m/%Y") > datetime.strptime(
            input_date, "%d/%m/%Y")#converts date to value that can be compared to other date values
    ]
    self.mapobject = map.Map(self.filtered_data, 0, 0, 2)
    self.mapobject.update_html()
    self.mapobject.run()#opens the map again

  def display_all(self):
    self.filtered_data = [entry[0] for entry in self.data]
    self.mapobject = map.Map(self.filtered_data, 0, 0, 2)
    self.mapobject.update_html()
    self.mapobject.run()


class PostsMenu(Menu):#menu for posting or viewing posts

  def __init__(self, queue, classname, database):
    self.choices = {
        "1": ("display posts", self.display_posts),
        "2": ("add post", self.add_post)
    }
    super().__init__(self.choices, queue, classname)
    self.database = database

  def display_posts(self):

    self.display_posts = DisplayPosts(self.que, "Posts", self.database)
    self.display_posts.run()# runs the Display posts menu to view posts

  def add_post(self):
    self.login = Login(self.que, "Authentication", self.database)
    if profile_name:
      self.post = self.postentry()
      if not self.post:#False is returned if user banned for posting too much
        print(
            "Sorry, user banned for the day"
        )  #this runs a function in database.py that detects trolls and if it detects a troll it prints this
      else:
        self.database.add_entry(self.post)
    elif self.login.run():
      self.post = self.postentry()
      if not self.post:
        print("Sorry, user banned for the day")
      else:
        self.database.add_entry(self.post)

  def get_type(self):
    while True:
      try:
        self.incident = input(
            "Enter incident type: \n1. Altercation\n2. Vandalism\n3. Protest\n"
        )
        if self.incident == "1":
          return "blue"
        if self.incident == "2":
          return "red"
        if self.incident == "3":
          return "green"
      except:
        rich.print(
            f"[yellow2]'{self.incident}' is an invalid option.[/yellow2] [italic]please try again"
        )

  def postentry(self):
    #[[profile_id, title, details, address, zipcode, city, state, country, upvotes, type, date, time, datetime]]
    #####TO BE EDITED#####
    #get values from input values and put them into list that will be entered into add_entry function in database.py
    self.post_author = profile_name
    self.profile_id = self.database.fetch_id_by_username(self.post_author)
    #self.date = DateMenu(self.que, "Date Menu").run()
    self.title = input("Enter title: ")
    self.day, self.month, self.year = input("Enter Day of month: "), input(
        "Enter Month as 2 digit number: "), input("Enter Year (4 digits): ")
    self.details = input("Enter incident details: ")
    self.address = input("Enter address: ")
    self.country = input("Enter country: ")
    self.state = input("Enter state: ")
    self.city = input("Enter city: ")
    self.zipcode = input("Enter zipcode: ")
    self.type = self.get_type()
    self.time = input("Enter time: ")
    if not self.database.check_user(#check if user is a troll, this function is explained in database.py
        self.post_author, f"{self.day}/{self.month}/{self.year}",#put in arguements for function
        self.database.fetch_id_by_username(self.post_author)):
      return False #make sure that troll doesn't go through, if it returns false the user sees a message that they are locked out
    return [
        self.profile_id, self.title, self.details, self.address, self.zipcode,
        self.city, self.state, self.country, 0, self.type,
        f"{self.day}/{self.month}/{self.year}", self.time
    ]


class DisplayPosts(Menu):  #used AI for autocomplete and generating small peices of code

  def __init__(self, queue, classname, database):
    self.cleaning = False
    self.choices = {
        "1": ("next", self.next),
        "2": ("previous", self.previous),
        "3": ("upvote", self.upvote),
        "4": ("filter by type",
              self.filter_by_type),  # Added option to filter by type
        "5": ("clean up vandalism", self.clean_up_vandalism),
        "6": ("display all", self.refetch)
    }
    self.database = database
    super().__init__(self.choices, queue, classname)
    self.allposts = self.database.fetch_all_entries()
    self.allposts.sort(key=lambda entry: datetime.strptime(
        entry[11] + " " + str(entry[12]), "%d/%m/%Y %H"),
                       reverse=True)  #AI
    self.currentpost_index = 0
    #[[id, profile_id, title, details, address, zipcode, city, state, country, upvotes, type, date, time, datetime, cleaned_up],...]
  def refetch(self):
    self.allposts = self.database.fetch_all_entries()
    self.allposts.sort(key=lambda entry: datetime.strptime(
        entry[11] + " " + str(entry[12]), "%d/%m/%Y %H"),
                       reverse=True)  #AI
    self.currentpost_index = 0

  def clean_up_vandalism(self):#allows user to volunteer cleanup
    self.refetch()
    self.type = "red"
    self.filtered_data = [
        entry for entry in self.allposts
        if entry[10] == self.type and entry[14] == 0
    ]
    self.filtered_data.sort(key=lambda entry: datetime.strptime(
        entry[11] + " " + str(entry[12]), "%d/%m/%Y %H"),
                            reverse=True)
    self.allposts = self.filtered_data
    self.currentpost_index = 0
    self.cleaning = True

  def filter_by_type(self):
    self.refetch()
    self.type = PostsMenu(self.que, "temp posts menu", None).get_type()
    self.filtered_data = [
        entry for entry in self.allposts if entry[10] == self.type
    ]
    self.filtered_data.sort(key=lambda entry: datetime.strptime(
        entry[11] + " " + str(entry[12]), "%d/%m/%Y %H"),
                            reverse=True)
    self.allposts = self.filtered_data
    self.currentpost_index = 0

  def previous(self):
    if self.currentpost_index < len(self.allposts) - 1:
      self.currentpost_index += 1
    else:
      print("No more posts to display")

  def next(self):
    if self.currentpost_index > 0:
      self.currentpost_index -= 1
    else:
      print("This is the most recent post")

  def upvote(self):
    if profile_name:
      if self.database.fetch_id_by_username(profile_name) != self.allposts[
          self.currentpost_index][1]:
        if self.database.update_upvotes(
            self.allposts[self.currentpost_index][0],
            self.allposts[self.currentpost_index][9] + 1,
            self.allposts[self.currentpost_index][1]):
          self.allposts[self.currentpost_index][9] += 1
    else:
      self.login = Login(self.que, "Authentication", self.database)
      self.login.run()
      if str(self.database.fetch_id_by_username(profile_name)) != str(
          self.allposts[self.currentpost_index][1]):
        if self.database.update_upvotes(
            self.allposts[self.currentpost_index][0],
            self.allposts[self.currentpost_index][9] + 1,
            self.allposts[self.currentpost_index][1]):
          self.allposts[self.currentpost_index][9] += 1

  def mark_cleaned(self):
    if self.database.update_cleaned_up(
        self.allposts[self.currentpost_index][0]):
      self.allposts[self.currentpost_index][14] = 1
      print("Entry marked as cleaned. Thank you!")
      self.cleaning = False
    else:
      print("Already cleaned up.")

  def run(self):
    while True:
      self.display_post(self.currentpost_index)
      self.display_menu()
      self.choice = input("enter selection: ")
      action = self.choices.get(self.choice)
      if self.choice == self.exit:
        break
      if action:
        action[1]()
        if self.cleaning:
          self.choices["5"] = ("mark cleaned", self.mark_cleaned)
        else:
          self.choices["5"] = ("clean up vandalism", self.clean_up_vandalism)
      else:
        rich.print(
            f"[yellow2]'{self.choice}' is an invalid option.[/yellow2] [italic]please try again[/]"
        )

  def display_menu(self):
    for menukey, menuitem in self.choices.items():
      rich.print(f"[blue bold]{menukey}:[/] [cyan]{menuitem[0]}[/]", end="|")
    self.exit = "b"
    rich.print("[magenta][b]b:[/] back[/]")
    rich.print("[italic]please enter an option:[/]")

  def display_post(self, index):
    try:
      self.indexedpost = self.allposts[index]
      print(
          f" Post id: {self.indexedpost[0]}\n Date: {self.indexedpost[11]} \n Heading: {self.indexedpost[2]} \n Details: {self.indexedpost[3]} \n Address: {self.indexedpost[4]}, {self.indexedpost[6]}, {self.indexedpost[7]}, {self.indexedpost[8]}, {self.indexedpost[5]} \n Upvotes: {self.indexedpost[9]} \n Type: {self.indexedpost[10]} \n Time: {self.indexedpost[12]} \n"
      )
    except:
      print("No posts to display")


class Login(Menu):

  def __init__(self, queue, classname, database):
    self.choices = {
        "1": ("login", self.login),
        "2": ("register", self.register)
    }
    super().__init__(self.choices, queue, classname)
    self.database = database

  def run(self):
    while True:
      if profile_name:  # Comment: Check if profile_name is already set
        break
      self.display_menu()
      self.choice = input()
      print(end="\033c")  # Comment: Clear the interpreter console
      action = self.choices.get(self.choice)
      if self.choice == self.exit:
        break
      if action:
        if (action[1]()):
          return True
      else:
        rich.print(
            f"[yellow2]'{self.choice}' is an invalid option.[/yellow2] [italic]please try again[/]"
        )

  def user_authentication(self):  #AI assisted
    while True:
      self.user = input("Enter your username: ")
      self.password = input("Enter your password: ")
      if not self.database.fetch_id_by_username(self.user):
        print("no such username")
        return False
      elif self.database.authenticate(self.user, self.password):
        print("Authentication successful!")
        global profile_name  # Comment: Add global keyword to update global variable
        profile_name = copy.deepcopy(self.user)
        break
      else:
        print("Invalid username or password. Please try again.")
    return True

  def login(self):
    if self.user_authentication():
      return True
    else:
      return False

  def register(self):  #AI
    while True:
      self.user = input("Enter your username: ")
      self.phonenumber = input("Enter your phone number: ")
      self.password = input("Enter your password: ")
      self.password_repeat = input("Repeat your password: ")

      if self.password != self.password_repeat:
        print("Passwords do not match. Please try again.")
        continue

      if not self.is_good_password(self.password):
        print("Password is not strong enough. Please try again.")
        continue
      else:
        self.database.add_profile(self.user, self.password, self.phonenumber)
        print("User added successfully!")
        break

  def is_good_password(self, password):
    # Implement your password strength criteria here
    # For example, you can check for minimum length, presence of uppercase, lowercase, digits, etc.
    # Return True if the password meets the criteria, False otherwise
    return len(password) >= 8 and any(c.isupper() for c in password) and any(
        c.islower() for c in password) and any(c.isdigit() for c in password)
