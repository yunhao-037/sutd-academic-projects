**"Down For Laundry"**

A group project with the course "Digital World" (Python, Jan - Apr 2019).

Designed an IoT product (an integrated system of laundromat machines and a mobile app).
Aimed to create a solution to optimise the usage of washing machines and dryers in hostel laundromat.
Programmed Raspberry Pi (RPi) with Python to update Firebase database with real-time human traffic flow,
which further pushes update to the phone app (designed using Kivy) of machine availabilities.

**Python codes running instructions:**

1) Setup Raspberry Pi, open DFL_RPi.py and DFL_ML.py in Raspberry Pi; run DFL_RPi.py.

2) Open DFL_kivy.py and DFL_opencv.py; run DFL_kivy.py. This is the kivy console.

3) When hosting a group in Laundry Hitch, the host will select the number of people with him right now
   and the number of people he is looking for respectively. Once the group is filled up,
   the host can proceed with informing the other members to come to the laundry room through the app.
   The app would then prompt the host to only close the group after everyone has met up and done their laundry.
   
4) When looking to join a group in Laundry Hitch, the user can select from a refreshing page of available groups.
   The button will indicate the number of open spots left in the group as well as the total number of people that will eventually be in the group.
