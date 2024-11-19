# WHITEBOARD PRODUCTIVITY
#### Video Demo:  <URL https://www.youtube.com/watch?v=AmSgWIhPhxY>
#### Description:
    Whiteboard productivity is a web application that allows users to keep track of how much time they spend on a given task and stores it for them to see. When a user first loads up the web app they will be prompted to log in but if they do not have an account they can register for an account by clicking the link in the top right corner. Once the user enters in a valid username and password they will immediately be prompted to create a new goal. (NOTE: The files discussed in this paragraph were... 'login.html' & 'registration.html')

    When creating a new goal, you want to choose a task/goal that you are working towards and can easily time. For me, it has been learning how to code, so I would put 'Coding' and then the amount of time I want to spend, '1000', and the time I have spent so far, '250'. If the user wants to create a subgoal, they can by clicking the checkbox in the form. An example of this would be for my main goal 'Coding', I might have a subgoal of spending '100' hours working on Whiteboard Productivity so I would utilize the subgoal feature then. The user can also add a description to their goal. An example of this would be, 'I want to learn how to code by taking Harvard's CS50, Princeton's Algorithms 1 & 2, and Stanford's introductory Machine Learning course'.  I couldn't figure out how to recursively do this so the user is only limited to a subgoal within a goal, not subgoals within a subgoal of a goal and as of right the individual goal page that allows user to see this discription for each goal as well as their subgoals is not available yet. (NOTE: The files discussed in this paragraph were... 'newgoal.html' & 'newsubgoal.html')

    After creating a goal the user will be sent to the home page of the web application which is also where the timer functionality is located. When starting a timer the user first needs to choose a goal they would like to keep track of. If they do not put in a goal then the timer will default to whatever the first goal they ever made was. Once they have selected a goal, they can choose for how much time they want to set their timer for by either utilizing the increment/decrement arrows or by typing in any time. The front end automatically converts the time into seconds which allows it to update the UI every second once the timer is started.  Once timer is started the start button becomes a stop button and on the backend the start timer function is called in which stores a session["start_time"] which is used to eventually calculate the session["elapsed_time"]. Using AJAX requests we are able to do this without refreshing the page which makes it so that all data actually used to keep track of the time spent on a task is handled on the backend which means a user with malicious intent cannot break it. Once the timer hits 00:00:00, the user will here an alarm and can then stop the timer. Once they stop the timer they have the option to save the time which will not occur asynchronously but will update the time they have spent in total on a task and send them to the Goals page where they can view. (NOTE: The files discussed in this paragraph were... 'index.html' & 'app.py')

    Once the user is sent to their Goals page. They will see a table with only one column since they only have one goal. This table includes data on the goal name, a progress bar, the percentage of the goal they have completed, how much time they have spent so far and finally how much their goal time is. A design choice I had to make was how I was going to make the progress bar since I could have made it by myself or by utlizing the built in HTML element. Eventually, I decided to go with the built HTML element since I have limited CSS knowledge; however, visually, within my web application I still think it works. Something I really want to add in the future is the ability for the user click on each table row and then see a customized Goal page tailored to each unique Goal via that page they would be able to click on the various subgoals they had which would display to them a Subgoal Page. (NOTE: The files discussed in this paragraph were... 'goals.html' eventually... 'goal.html' & 'subgoal.html')

    Finally, the user can click on the gear icon in the right corner of the nav bar which allows the users to view their settings. They can there change their alarm as well as log out. The user's preferences are all stored in a table within the database called 'preferences'.  The request to change a user's preferences occurs asynchronously via the 'set_alarm' function. (NOTE: The files discussed in this paragraph were... 'settings.html' & 'app.py')# whiteboard_productivity
