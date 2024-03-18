import sqlite3
#replit copilot was used for this project

class Database:

  def __init__(self):
    con = sqlite3.connect('posts.db')
    cur = con.cursor()
    #create tables which are filled with values that corespond to the lists that will be inputed into functions
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, title TEXT, details TEXT, address TEXT, zipcode INTEGER, city TEXT, state TEXT, country TEXT, upvotes INTEGER, type TEXT, date TEXT, time TEXT, datetime TEXT)'''
    )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS profiles (profile_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, phone_number TEXT, verified INTEGER, posts_upvoted TEXT)''' 
      #the verified has a value either 0 or 1 and it assumes that an account is zero (not verified) unless add_verified_profile function is called
    )



  def connect(
      self
  ):  #this function is to establish conections and runs in the beginning of every other function
      #even though the same command (except for self) is in __init__ this function is necessary to reestablish connection as we close connection after each function
    self.con = sqlite3.connect('posts.db')
    self.cur = self.con.cursor()

  def data_refiner(
      self, data
  ):  #takes in the output of sql fetchall and turns it into list of lists
    for i in range(
        len(data)
    ):  #use this for loop to return as list of lists each of which are in the same format as recieved plus a datetime column
      data[i] = list(data[i])
    return (data)

  """gpt pormpt to create the following function (only the following function no others): this is my class: import sqlite3 class Database:
    def init(self): pass def connect(self): #this will connect to the database con = sqlite3.connect('posts.db')
    self.cur = con.cursor() create a function called database.add_entry(list) that takes in a list that has
    the following variables: [id, profile_id, title, details, address, zipcode, city, state, country upvotes, 
    type, date, time] with id, zipcode profile_id, upvotes, and type being ints and the other variables being strings.
    Create a function that takes these in and adds them to a table called incidents (with the variable name in the function
    as the column name in the table) along with and sqlite3 date time in a separate column called datetime."""

  #this function has been modified from the ai result
  def add_entry(self, entry):
    self.connect()  #create a connection to the database

    self.cur.execute(
        '''INSERT INTO incidents ( profile_id, title, details, address, zipcode, city, state, country, upvotes, type, date, time, datetime) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
        (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6],
         entry[7], entry[8], entry[9], entry[10], entry[11]))
    #use ? to prevent injection attack
    self.con.commit()
    self.cur.close()
    self.con.close()  #close all connections

  #takes in username password and phone number and adds them to the profiles table along with an id that is autoincremented
  def add_profile(self, username, password, phone_number):
    self.connect()

    self.cur.execute(
        '''INSERT INTO profiles (username, password, phone_number,verified, posts_upvoted) VALUES ( ?, ?, ?,0,'[]')''',
        (username, password, phone_number))
    #use ? to prevent injection attack
    self.con.commit()
    self.cur.close()
    self.con.close()  #close all connections
  #this is a separate function because verrified users must be put in on the backend and is reserved for community leaders and police
  def add_verified_profile(self, username, password, phone_number):
    self.connect()

    self.cur.execute(
        '''INSERT INTO profiles (username, password, phone_number,verified, posts_upvoted) VALUES ( ?, ?, ?,1,'[]')''', #the one means that it is a verified account
        (username, password, phone_number))
    #use ? to prevent injection attack
    self.con.commit()
    self.cur.close()
    self.con.close()  #close all connections

    #take in username and password and returns whether username and password is valid
  def authenticate(self, username, password):
      self.connect()

      authenticator = self.cur.execute(
        '''SELECT * FROM profiles WHERE username = ? AND password = ?''',
        (username, password)).fetchall()
      return (
        len(authenticator) > 0
      )  #check if there are any rows in the table that match the username and password and if there are return true

  def fetch_id_by_username(self, username):
    self.connect()
    try:
      #return the id of the profile with the username by returning the first element of the tuple returned by cursor
      return (self.cur.execute(
          '''SELECT profile_id FROM profiles WHERE username = ?''',
          (username, )).fetchall()[0][0])
    except:
      return False  #if there is no profile with the username return false

  def fetch_username_by_id(self, id):
    self.connect()
    try:
      #return the id of the profile with the username by returning the first element of the tuple returned by cursor
      return (self.cur.execute(
          '''SELECT username FROM profiles WHERE profile_id = ?''',
          (id, )).fetchall()[0][0])
    except:
      return False  #if there is no profile with the id return false this would indicate a problem with the backend

  def fetch_all_entries(self):
    self.connect()
    result = self.cur.execute('''SELECT * FROM incidents''').fetchall()
    return (
        self.data_refiner(result)
    )  #change to format that is easier to read and return the data as a list of lists

  def fetch_by_date(self, date):
    self.connect()
    result = self.cur.execute('''SELECT * FROM incidents WHERE date = ?''',
                              (date, )).fetchall()
    return (
        self.data_refiner(result)
    )  #change to format that is easier to read and return the data as a list of lists

  def fetch_by_city(self, city):
    self.connect()
    result = self.cur.execute('''SELECT * FROM incidents WHERE city = ?''',
                              (city, )).fetchall()
    return (
        self.data_refiner(result)
    )  #change to format that is easier to read and return the data as a list of lists

  def fetch_by_zip(self, zip):
    self.connect()
    result = self.cur.execute('''SELECT * FROM incidents WHERE zip = ?''',
                              (zip, )).fetchall()
    return (
        self.data_refiner(result)
    )  #change to format that is easier to read and return the data as a list of lists

  def fetch_by_country(self, country):
    self.connect()
    result = self.cur.execute('''SELECT * FROM incidents WHERE country = ?''',
                              (country, )).fetchall()
    return (
        self.data_refiner(result)
    )  #change to format that is easier to read and return the data as a list of lists

  def fetch_by_state(self, state):
    self.connect()
    result = self.cur.execute('''SELECT * FROM incidents WHERE state = ?''',
                              (state, )).fetchall()
    return (
        self.data_refiner(result)
    )  #change to format that is easier to read and return the data as a list of lists

  #checks for trolls if it detects a troll or the user doesn't exist then it returns false, otherwise return true

  #the way that the funtion detects trolls is by assuming that any nonverified user that has posted more than twice in the last 24 hours and has more posts than upvotes is a troll
  def check_user(self, username, date,user_id):
    self.connect()
    is_verified = self.cur.execute('''SELECT * FROM profiles WHERE username = ?''',(username,)).fetchall() #find user in profile db

    if len(is_verified) == 0: #if the user is not in the db then return false

      return False
    if is_verified[0][3] == 1: #check if verified
      return True
    posts = self.fetch_by_date(date) #check the posts today and compiles into list
    self.data_refiner(posts) #make it into nice list
    posts_total = 0 #this is a counter of how many posts the user has posted today
    upvotes_total = 0 #this counts total upvotes

    for i in range(len(posts)):
      if posts[i][1] == user_id: #if the id of the post is the same as the user id
        posts_total += 1
        upvotes_total += int(posts[i][9]) #this adds the amount of upvotes to the total

    if posts_total > 2: #if the user has posted more than 2 posts today meaning if they are likely a troll

      return(upvotes_total >= posts_total) #if upvotes are greater than posts than they are still trustworthy
    return True #if doesn't detect troll


  #the following fwas the original function
  """def update_upvotes(self, post_id, upvote_value, profile_id):
    self.connect()
    posts_upvoted = list(self.cur.execute('''SELECT posts_upvoted FROM profiles WHERE profile_id = ?''', (profile_id,)).fetchall())
    print(posts_upvoted)

    for i in posts_upvoted:
        if str(post_id) == i:
            return False  # Return False if the post has already been upvoted by this user

    self.cur.execute('''UPDATE incidents SET upvotes = ? WHERE id = ?''', (upvote_value, post_id))
    self.con.commit()
    #posts_upvoted = list(posts_upvoted[0][0].strip('[]').replace("'", "").split(', ')) if str(posts_upvoted) else []

    if str(post_id) in posts_upvoted:
      print(post_id)
      return False  # Return False if the post has already been upvoted by this user

    posts_upvoted.append(str(post_id))
    print(posts_upvoted)
    self.cur.execute('''UPDATE profiles SET posts_upvoted = ? WHERE profile_id = ?''', (str(posts_upvoted), profile_id))
    self.con.commit()
    print(list(self.cur.execute('''SELECT * FROM profiles WHERE profile_id = ?''', (profile_id,)).fetchall()))

    self.cur.close()
    self.con.close()

    return True  # Return True to indicate that the operation was successful"""
  #the following is the function that is noted out above debugged using ai
  def update_upvotes(self, post_id, upvote_value, profile_id):
    self.connect() 

    posts_upvoted = self.cur.execute(
        '''SELECT posts_upvoted FROM profiles WHERE profile_id = ?''',
        (profile_id,)
    ).fetchone()#grab the list of posts upvoted as a string
    if not posts_upvoted:
        posts_upvoted = []
    else:
        posts_upvoted = eval(posts_upvoted[0]) if posts_upvoted[0] else []
    if str(post_id) in posts_upvoted:
        return False  # Return False if the post has already been upvoted by this user
    #update the upvotes for the post
    self.cur.execute(
        '''UPDATE incidents SET upvotes = ? WHERE id = ?''',
        (upvote_value, post_id)
    )
    #update the list of posts upvoted so that the same acount can't update it again
    posts_upvoted.append(str(post_id))
    self.cur.execute(
        '''UPDATE profiles SET posts_upvoted = ? WHERE profile_id = ?''',
        (str(posts_upvoted), profile_id)
    )
    self.con.commit()
    self.cur.close()
    self.con.close()
    return True  # Return True to indicate that the operation was successful
