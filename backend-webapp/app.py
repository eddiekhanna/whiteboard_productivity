from datetime import datetime, timedelta
from functools import wraps
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from flask_cors import CORS
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Enable CORS to allow cross-origin requests from mobile app
CORS(app)

# CS50 CODE
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///whiteboard_productivity.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



#ERROR APOLOGY 
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code



#REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    
    #If user is requesting registration page
    if request.method == "GET":
        return render_template('registration.html')
    
    #Elif user has filled out registration form
    elif request.method == "POST":
        #Initialize variables from form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        #Error checking
        if not username or not password or not confirmation:
            return apology("Missing text field.")
        
        usedUsernames = db.execute("SELECT username FROM users")
        for usedUsername in usedUsernames:
            if username == usedUsername["username"]:
                return apology("Username already taken.")
        
        if password != confirmation:
            return apology("Password do not match.")
                
        #Security
        hash = generate_password_hash(password)

        #Add user to database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        #Log new user in
        result = db.execute(
            "SELECT id FROM users WHERE username = ? AND hash = ?", username, hash)
        
        if result:
            session["user_id"] = result[0]["id"]
            db.execute("INSERT INTO preferences (user_id, alarm_preference) VALUES (?, ?)", session["user_id"], 'static/alarms/THE SHADE.mp3')
        else:
            return apology("Registration failed")
        
        #Return user to goal creation page
        return redirect("/newgoal")
        
        

                
#LOGIN            
@app.route("/login", methods = ["GET", "POST"])    
def login():
    
    # Forget any user_id
    session.clear()
    
    #If user needs to login
    if request.method == "GET":
        return render_template('login.html')
    
    #Elif the user has completed the log in form
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("Missing text field.")
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username or password")
        
        #Remember user log in
        session["user_id"] = rows[0]["id"]

        #Send user to homepage
        return redirect("/")
            


#REQUIRE LOGIN FUNCTION
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



#CREATE GOAL
@app.route("/newgoal", methods = ["GET", "POST"])
@login_required
def newgoal():

    #If the user is loading in goal creation page
    if request.method == "GET":
        return render_template('newgoal.html')
    
    #Elif the user has submitted a new goal
    elif request.method == "POST":
        if not request.form.get("goalName"):
            return apology("Goal must have name")
        
        goalName = request.form.get("goalName")
        
        goalHours = request.form.get("goalHours", 0)
        if goalHours == "":
            goalHours = 0
        goalHours = int(goalHours)
        
        goalMinutes = request.form.get("goalMinutes", 0)
        if goalMinutes == "":
            goalMinutes = 0
        goalMinutes = int(goalMinutes)
            
        goalSeconds = request.form.get("goalSeconds", 0)
        if goalSeconds == "":
            goalSeconds = 0
        goalSeconds = int(goalSeconds)
        
        databaseGoalTime = (goalHours * 3600) + (goalMinutes * 60) + goalSeconds

        if databaseGoalTime == 0:
            return apology("Must have a goal time")
        
        prevHours = request.form.get("prevHours", 0)
        if prevHours == "":
            prevHours = 0
        prevHours = int(prevHours)

        prevMinutes = request.form.get("prevMinutes", 0)
        if prevMinutes == "":
            prevMinutes = 0
        prevMinutes = int(prevMinutes)

        prevSeconds = request.form.get("prevSeconds", 0)
        if prevSeconds == "":
            prevSeconds = 0
        prevSeconds = int(prevSeconds)

        databasePrevTime = (prevHours * 3600) + (prevMinutes * 60) + prevSeconds

        description = request.form.get("description")

        #Run query for new goal
        db.execute("INSERT INTO goals (name, user_id, time_goal, time_spent, description) VALUES (?, ?, ?, ?, ?)",
                   goalName, session["user_id"], databaseGoalTime, databasePrevTime, description)

        if 'subgoal' in request.form:
            session["goal_id"] = db.execute("SELECT goal_id FROM goals WHERE name = ? AND user_id = ?", goalName, session["user_id"])[0]["goal_id"]
            return redirect("/newsubgoal")
        else:
            return redirect("/")
        


#CREATE SUBGOAL
@app.route("/newsubgoal", methods = ["GET", "POST"])
@login_required
def newsubgoal():

    #If the user wants to create a subgoal
    if request.method == "GET":
        goalName = db.execute("SELECT name FROM goals WHERE goal_id = ?", session["goal_id"])[0]["name"]
        return render_template('newsubgoal.html', goalName = goalName)

    #Elif the user is submitting a new subgoal
    elif request.method == "POST":
        
        if not request.form.get("subgoalName"):
            return apology("Subgoal must have name")
        
        subgoalName = request.form.get("subgoalName")
        
        subgoalHours = request.form.get("subgoalHours", 0)
        if subgoalHours == "":
            subgoalHours = 0
        subgoalHours = int(subgoalHours)
        
        subgoalMinutes = request.form.get("subgoalMinutes", 0)
        if subgoalMinutes == "":
            subgoalMinutes = 0
        subgoalMinutes = int(subgoalMinutes)
            
        subgoalSeconds = request.form.get("subgoalSeconds", 0)
        if subgoalSeconds == "":
            subgoalSeconds = 0
        subgoalSeconds = int(subgoalSeconds)
        
        databaseSubgoalTime = (subgoalHours * 3600) + (subgoalMinutes * 60) + subgoalSeconds

        prevHours = request.form.get("prevHours", 0)
        if prevHours == "":
            prevHours = 0
        prevHours = int(prevHours)

        prevMinutes = request.form.get("prevMinutes", 0)
        if prevMinutes == "":
            prevMinutes = 0
        prevMinutes = int(prevMinutes)

        prevSeconds = request.form.get("prevSeconds", 0)
        if prevSeconds == "":
            prevSeconds = 0
        prevSeconds = int(prevSeconds)
        
        databasePrevTime = (prevHours * 3600) + (prevMinutes * 60) + prevSeconds

        subgoalDescription = request.form.get("subgoalDescription")

        #Run query for new subgoal
        db.execute("INSERT INTO subgoals (name, goal_id, time_goal, time_spent, description) VALUES (?, ?, ?, ?, ?)",
                   subgoalName, session["goal_id"], databaseSubgoalTime, databasePrevTime, subgoalDescription)
        

        session["goal_id"] = None
        return redirect("/")



#HOMEPAGE
@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    
    #If the user is loading in the homepage
    if request.method == "GET":
        
        #Get data for alarm display
        goalsForDropdown = db.execute("SELECT name FROM goals WHERE user_id = ?",  session["user_id"])
        subgoalsForDropdown = db.execute("SELECT name FROM subgoals WHERE goal_id IN (SELECT goal_id FROM goals WHERE user_id = ?)", session["user_id"])
        
        dropdown = goalsForDropdown + subgoalsForDropdown
        
        alarmPreference = db.execute("SELECT alarm_preference FROM preferences WHERE user_id = ?",  session["user_id"])[0]["alarm_preference"]

        return render_template('index.html', alarmPreference=alarmPreference, dropdown=dropdown)
    
    #Elif wants to save the amount of time 
    elif request.method == "POST":
        
        submittedName = request.form.get("goal")
        finalTimeInSeconds = int(session["elapsed_time"])

        #FIXME: Account for cases where there are multiple of the same goal
        #Fetch goal and subgoal names for the current user
        goalRows = db.execute("SELECT goal_id, name FROM goals WHERE user_id = ?", session["user_id"])
        subgoalRows = db.execute("SELECT subgoal_id, name FROM subgoals WHERE goal_id IN (SELECT goal_id FROM goals WHERE user_id = ?)", session["user_id"])

        isGoal = None
        isSubgoal = None

        #Check if the submitted name matches a goal
        for row in goalRows:
            if row["name"] == submittedName:
                isGoal = row["goal_id"]

        #Check if the submitted name matches a subgoal
        for row in subgoalRows:
            if row["name"] == submittedName:
                isSubgoal = row["subgoal_id"]

        #If the user entered an invalid name for their goal/subgoal
        if isGoal is None and isSubgoal is None:
            return apology("Goal/Subgoal does not exist")
    
        #If the user selected a goal
        elif isGoal is not None and isSubgoal is None:
            #Calculate new goal time
            prevGoalTime = db.execute("SELECT time_spent FROM goals WHERE goal_id = ?", isGoal)[0]["time_spent"]
            newGoalTime = prevGoalTime + finalTimeInSeconds

            #Update the goal time in the database
            db.execute("UPDATE goals SET time_spent = ? WHERE goal_id = ?", newGoalTime, isGoal)
    
        #If the user selected a subgoal
        elif isGoal is None and isSubgoal is not None:
            # alculate new subgoal time
            prevSubgoalTime = db.execute("SELECT time_spent FROM subgoals WHERE subgoal_id = ?", isSubgoal)[0]["time_spent"]
            newSubgoalTime = prevSubgoalTime + finalTimeInSeconds

            #Calculate new goal time (update parent goal's time_spent)
            parentGoalId = db.execute("SELECT goal_id FROM subgoals WHERE subgoal_id = ?", isSubgoal)[0]["goal_id"]
            prevGoalTime = db.execute("SELECT time_spent FROM goals WHERE goal_id = ?", parentGoalId)[0]["time_spent"]
            newGoalTime = prevGoalTime + finalTimeInSeconds

            #Update the subgoal and goal time in the database
            db.execute("UPDATE subgoals SET time_spent = ? WHERE subgoal_id = ?", newSubgoalTime, isSubgoal)
            db.execute("UPDATE goals SET time_spent = ? WHERE goal_id = ?", newGoalTime, parentGoalId)


        #Reset session["elapsed_time"]
        session["elapsed_time"] = 0

        return redirect("/goals")
    


#START TIMER FUNCTION
@app.route("/start_timer", methods=["POST"])
def start_timer():
    # Record the current time as the start time
    session["start_time"] = datetime.now()
    
    return redirect("/")



#STOP TIMER FUNCTION
@app.route("/stop_timer", methods=["POST"])
def stop_timer():
    #Check if start_time is available in session
    if "start_time" not in session:
        return apology("Timer was never started.")

    #Calculate the time difference
    startTime = session["start_time"]
    stopTime = datetime.now()
    timeDelta = stopTime - startTime

    #Convert the the time_delta into a float
    timeDeltaSeconds = timeDelta.total_seconds()
    
    #Initialize elapsed_time in session in order to run equation
    if "elapsed_time" not in session:
        session["elapsed_time"] = 0.0
    
    #Add up elapsed_time
    session["elapsed_time"] += timeDeltaSeconds

    # Get the start hour and end hour
    start_hour = startTime.hour
    end_hour = stopTime.hour

    # Convert the time_delta into seconds
    total_seconds = int(timeDelta.total_seconds())

    # Extract JSON data from the request
    data = request.get_json()
    
    # Get the task name from the form
    submittedName = data.get("goalName") 

    #Fetch goal and subgoal names for the current user
    goalRows = db.execute("SELECT goal_id, name FROM goals WHERE user_id = ?", session["user_id"])
    subgoalRows = db.execute("SELECT subgoal_id, name, goal_id FROM subgoals WHERE goal_id IN (SELECT goal_id FROM goals WHERE user_id = ?)", 
                             session["user_id"])

    isGoal = None
    isSubgoal = None

    #Check if the submitted name matches a goal
    for row in goalRows:
        if row["name"] == submittedName:
            isGoal = row["goal_id"]

    #Check if the submitted name matches a subgoal
    for row in subgoalRows:
        if row["name"] == submittedName:
            isSubgoal = row["goal_id"]
            submittedName = db.execute("SELECT name FROM goals WHERE user_id = ? AND goal_id = ?", session["user_id"], isSubgoal)[0]["name"]

    #If the user entered an invalid name for their goal/subgoal
    if isGoal is None and isSubgoal is None:
        return apology("Goal/Subgoal does not exist")
    

    # Initialize a variable to keep track of the remaining time
    remaining_time = total_seconds

    # Log the time spent in hourly segments
    for hour in range(start_hour, end_hour + 1):
        if remaining_time <= 0:
            break
        
        # Determine the start and end time for this hour
        if hour == start_hour:
            # For the first hour, start from the actual start time
            hour_start = startTime
            hour_end = hour_start.replace(minute=59, second=59)  # End at 59:59
        elif hour == end_hour:
            # For the last hour, end at the actual stop time
            hour_start = hour_start.replace(hour=hour, minute=0, second=0)
            hour_end = stopTime
        else:
            # For middle hours, take the full hour
            hour_start = hour_start.replace(hour=hour, minute=0, second=0)
            hour_end = hour_start.replace(hour=hour, minute=59, second=59)
        
        # Calculate the duration in seconds for this segment
        duration_in_hour = (hour_end - hour_start).total_seconds()
        
        if remaining_time > duration_in_hour:
            # Log the full hour
            db.execute("INSERT INTO task_logs (user_id, task_name, duration, log_date, log_hour) VALUES (?, ?, ?, ?, ?)", 
                       session["user_id"], submittedName, int(duration_in_hour), hour_start.date(), hour)
            remaining_time -= duration_in_hour
        else:
            # Log the remaining time
            db.execute("INSERT INTO task_logs (user_id, task_name, duration, log_date, log_hour) VALUES (?, ?, ?, ?, ?)", 
                       session["user_id"], submittedName, remaining_time, hour_start.date(), hour)
            remaining_time = 0  # All time logged


    #Remove "start_time" so it can be used again
    session.pop("start_time", None)

    return redirect("/")



#GOALS
@app.route("/goals", methods = ["GET"])
@login_required
def goals():
    
    #If the user is loading in the goals page
    if request.method == "GET":
        goalsForTable = db.execute("SELECT * FROM goals WHERE user_id = ?",  session["user_id"])
        
        return render_template('goals.html', goalsForTable = goalsForTable)
    


#SET GOALID
@app.route("/set_goal_id", methods = ["POST"])
@login_required
def set_goal_id():
    data = request.get_json()
    
    goal_id = data.get("goal_id")

    if goal_id:
        session["goal_id"] = goal_id
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400



#GOAL
@app.route("/goal", methods = ["GET"])
@login_required
def goal():

    if request.method == "GET":
        # Get all of goal data for given goal
        goalInfo = db.execute("SELECT * FROM goals WHERE goal_id = ?", session["goal_id"])
        
        subgoalsForTable = db.execute("SELECT * FROM subgoals WHERE goal_id = ?", session["goal_id"])

        return render_template('goal.html', goalInfo=goalInfo[0], subgoalsForTable=subgoalsForTable)
    


#EDITGOAL
@app.route("/editgoal", methods = ["GET", "POST"])
@login_required
def editgoal():

    if request.method == "GET":
        goalName = db.execute("SELECT name FROM goals WHERE goal_id = ?", session["goal_id"])[0]["name"]
        return render_template("editgoal.html", goalName=goalName)
    
    elif request.method == "POST":
        
        #Edit for time spent on goal
        addedHours = request.form.get("addedHours")
        if addedHours == "":
            addedHours = 0
        addedHours = int(addedHours)

        addedMinutes = request.form.get("addedMinutes")
        if addedMinutes == "":
            addedMinutes = 0
        addedMinutes = int(addedMinutes)

        addedSeconds = request.form.get("addedSeconds")
        if addedSeconds == "":
            addedSeconds = 0
        addedSeconds = int(addedSeconds)

        addedTime = (3600 * addedHours) + (60 * addedMinutes) + addedSeconds

        #Get previous time spent on goal
        previousTime = db.execute("SELECT time_spent FROM goals WHERE goal_id = ?", session["goal_id"])[0]["time_spent"]

        newTime = previousTime + addedTime

        #Update database to reflect new time spent on goal
        db.execute("UPDATE goals SET time_spent = ? WHERE goal_id = ? ", newTime, session["goal_id"])

        #Edit on goal time
        newGoalHours = request.form.get("newGoalHours")
        newGoalMinutes = request.form.get("newGoalMinutes")
        newGoalSeconds = request.form.get("newGoalSeconds")
        
        #If the the user did not leave the new goal time section blank
        if newGoalHours != "" or newGoalMinutes != "" or newGoalSeconds != "":
            
            if newGoalHours == "":
                newGoalHours = 0
            newGoalHours = int(newGoalHours)

            if newGoalMinutes == "":
                newGoalMinutes = 0
            newGoalMinutes = int(newGoalMinutes)

            if newGoalSeconds == "":
                newGoalSeconds = 0
            newGoalSeconds = int(newGoalSeconds)

            newGoalTime = (3600 * newGoalHours) + (60 * newGoalMinutes) + newGoalSeconds

            db.execute("UPDATE goals SET time_goal = ? WHERE goal_id = ? ", newGoalTime, session["goal_id"])

        return redirect("/goal")




#SET SUBGOALID
@app.route("/set_subgoal_id", methods = ["POST"])
@login_required
def set_subgoal_id():
    data = request.get_json()
    
    subgoal_id = data.get("subgoal_id")

    if subgoal_id:
        session["subgoal_id"] = subgoal_id
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400



#SUBGOAL
@app.route("/subgoal", methods = ["GET"])
@login_required
def subgoal():

    if request.method == "GET":
        # Get all of the subgoal data for given subgoal
        subgoalInfo = db.execute("SELECT * FROM subgoals WHERE subgoal_id = ?", session["subgoal_id"])

        return render_template('subgoal.html', subgoalInfo=subgoalInfo[0])
    


#EDITSUBGOAL
@app.route("/editsubgoal", methods = ["GET", "POST"])
@login_required
def editsubgoal():

    if request.method == "GET":
        subgoalName = db.execute("SELECT name FROM subgoals WHERE subgoal_id = ?", session["subgoal_id"])[0]["name"]
        return render_template("editsubgoal.html", subgoalName=subgoalName)
    
    elif request.method == "POST":
        addedHours = request.form.get("addedHours")
        if addedHours == "":
            addedHours = 0
        addedHours = int(addedHours)

        addedMinutes = request.form.get("addedMinutes")
        if addedMinutes == "":
            addedMinutes = 0
        addedMinutes = int(addedMinutes)

        addedSeconds = request.form.get("addedSeconds")
        if addedSeconds == "":
            addedSeconds = 0
        addedSeconds = int(addedSeconds)

        addedTime = (3600 * addedHours) + (60 * addedMinutes) + addedSeconds

        previousTime = db.execute("SELECT time_spent FROM subgoals WHERE subgoal_id = ?", session["subgoal_id"])[0]["time_spent"]

        newTime = previousTime + addedTime

        db.execute("UPDATE subgoals SET time_spent = ? WHERE subgoal_id = ? ", newTime, session["subgoal_id"])


        #Edit on goal time
        newSubgoalHours = request.form.get("newSubgoalHours")
        newSubgoalMinutes = request.form.get("newSubgoalMinutes")
        newSubgoalSeconds = request.form.get("newSubgoalSeconds")
        
        #If the the user did not leave the new  sub goal time section blank
        if newSubgoalHours != "" or newSubgoalMinutes != "" or newSubgoalSeconds != "":
            
            if newSubgoalHours == "":
                newSubgoalHours = 0
            newSubgoalHours = int(newSubgoalHours)

            if newSubgoalMinutes == "":
                newSubgoalMinutes = 0
            newSubgoalMinutes = int(newSubgoalMinutes)

            if newSubgoalSeconds == "":
                newSubgoalSeconds = 0
            newSubgoalSeconds = int(newSubgoalSeconds)

            newSuboalTime = (3600 * newSubgoalHours) + (60 * newSubgoalMinutes) + newSubgoalSeconds

            db.execute("UPDATE subgoals SET time_goal = ? WHERE subgoal_id = ? ", newSuboalTime, session["subgoal_id"])

        return redirect("/subgoal")





#MONTH SELECT
@app.route("/month", methods = ["GET", "POST"])
@login_required
def month():

    if request.method == "GET":
         
         #Always prompt user for given month
         currentMonth = datetime.now().month
         
         return render_template("month.html", currentMonth=currentMonth)
    
    elif request.method == "POST":

        #Get actual selected month
        session["selectedMonthNumber"] = int(request.form.get("month"))

        # Set year variable 
        session["selectedYearNumber"] = int(request.form.get("year"))
        session["selectedYearNumber"] = 2024

        
        #Ensure there is a value in selectedMonth
        if session["selectedMonthNumber"] is None:
            session["selectedMonthNumber"] = datetime.now().month

        if session["selectedMonthNumber"] < 1 or session["selectedMonthNumber"] > 12:
            return apology("Please select month between 1 and 12")

        return redirect("/calendar")



@app.route("/calendar", methods = ["GET"])
@login_required
def data():

    if request.method == "GET":
        
        #Query for list of all goal names
        namesOfGoals = db.execute("SELECT task_name FROM task_logs WHERE user_id = ? AND strftime('%Y', log_date) = ? AND strftime('%m', log_date) = ?", 
                                  session["user_id"], str(session["selectedYearNumber"]), str(session["selectedMonthNumber"]).zfill(2))
        
        
        #Legend colors
        legendColors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']

        
        #FIXME: Account for case where user has more than 7 goals
        addedGoals = set()
        
        #Create list of name-color pairs
        session["goalsWithColors"] = []
        
        for i in range(len(namesOfGoals)):
            nameOfGoal = namesOfGoals[i]['task_name']
            
            if nameOfGoal not in addedGoals:
                color = legendColors[i % len(legendColors)]
                session["goalsWithColors"].append((nameOfGoal, color))

                addedGoals.add(nameOfGoal)

        print(session["goalsWithColors"])

        
        #Convert selected month number into name
        monthNames = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        #Let the month name from the dictionary
        session["selectedMonthName"] = monthNames.get(session["selectedMonthNumber"], "Invalid month")


        return render_template('calendar.html', selectedMonthName=session["selectedMonthName"], 
                               selectedMonthNumber=session["selectedMonthNumber"], selectedYearNumber=session["selectedYearNumber"],
                               goalsWithColors=session["goalsWithColors"])
    


#GET DAILY DATA
@app.route("/get_daily_data", methods = ["POST"])
@login_required
def get_daily_data():
    data = request.get_json()
    dayValue = data.get('dayValue')
    print(dayValue)

    # Assuming the values in the session are integers for year, month, and day
    year = session["selectedYearNumber"]
    month = session["selectedMonthNumber"]
    #FIXME: Ensure there is a valid integer
    day = int(dayValue)

    # Construct the date string in the format YYYY-MM-DD
    log_date = f"{year:04d}-{month:02d}-{day:02d}"

    dailyData = db.execute("SELECT * FROM task_logs WHERE user_id = ? AND log_date= ?", session["user_id"], log_date)
    
    if not dailyData:
        # No data for the specified date
        print("No task logs found for this date.")
        return jsonify({"status": "success", "message": "No task logs found.", "data": dailyData}), 200
    else:
        print(dailyData)
        formattedData = [{"task_name": log["task_name"], "duration": log["duration"]} for log in dailyData]
    
        return jsonify({"status": "success", "message": "Task logs found.", "data": formattedData}), 200
    

    


#SET DAY VALUE
@app.route("/set_day_value", methods = ["POST"])
@login_required
def set_day_value():
    data = request.get_json()
    day_value = data.get('dayValue')

    if day_value:
        session["selectedDayNumber"] = int(day_value)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400



#DAY VIEW
@app.route("/dayview", methods = ["GET"])
@login_required
def dayview():

    if request.method == "GET":

        return render_template('dayview.html', selectedMonthName=session["selectedMonthName"], 
                               selectedMonthNumber=session["selectedMonthNumber"], selectedYearNumber=session["selectedYearNumber"], 
                               selectedDayNumber=session["selectedDayNumber"], goalsWithColors=session["goalsWithColors"])

    

#SETTINGS
@app.route("/settings", methods = ["GET", "POST"])
@login_required
def settings():

    #If the user is requesting their settings page
    if request.method == "GET":
        return render_template('settings.html')
    


#SETALARM
@app.route("/set_alarm", methods=["POST"])
def set_alarm():
    data = request.get_json()  #Get the JSON payload from the frontend
    alarmPreference = data.get("alarmPreference")
    
    #FIXME: Error check alarm preference
    if not alarmPreference:
        return jsonify({"error": "No alarm selected"}), 400


    db.execute("UPDATE preferences SET alarm_preference = ? WHERE user_id = ?", alarmPreference, session["user_id"])
    
    
    return redirect("/settings")
    


#LOGOUT
@app.route("/logout", methods = ["POST"])
@login_required
def logout():
    
    #Clear session
    session.clear()

    return redirect("/login")


########################################## MOBILE APP API ###########################################################

@app.route('/api/mobile_login', methods=['POST'])
def mobile_login():
    print("hello world")
    # Get the JSON payload from the frontend
    data = request.get_json()
    
    # Access the username and password from the JSON object
    username = data['username']
    password = data['password']

    print(f"Username: {username}, Password: {password}")

    # Return a success message as a JSON response
    return jsonify({'message': 'Login successful', 'user_id': 123})




################### LAST BIT OF CONFIGURATION ######################
if __name__ == '__main__':
    app.run(debug=True, port=5001)