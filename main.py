# Name: Mohammed Hisham Moizuddin
# UIN: 650344339
# CS 341 - Project 1 | Fall 2022 | Professor Patrick Troy
# Description: A console-based Python program that inputs commands from the user and outputs data from the CTA2 L daily ridership database.


import sqlite3
import matplotlib.pyplot as plt
import re


##################################################################
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()

    print("General stats:")

    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")  #No. of Stations

    dbCursor.execute("Select count(Stop_Name) From Stops;")
    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")  #No. of Stops

    dbCursor.execute("Select count(Station_ID) From Ridership;")
    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")  #No. of Ride Entries

    dbCursor.execute("Select MIN(date(Ride_Date)), MAX(date(Ride_Date)) from Ridership;")  #Date Range
    row = dbCursor.fetchone()
    print("  date range:", row[0], end='')
    print(" -", row[1])

    dbCursor.execute("Select sum(Num_Riders) From Ridership;")
    row = dbCursor.fetchone()
    totalRidership = int(row[0])  #Total Ridership
    print("  Total ridership:", f"{row[0]:,}")

    dbCursor.execute("Select sum(Num_Riders) From Ridership where Type_of_Day = 'W';")  #Weekday Ridership
    row = dbCursor.fetchone()
    weekdayRidership = int(row[0])
    percWeekday = float(round((weekdayRidership / totalRidership) * 100, 2))
    print("  Weekday ridership:", f"{row[0]:,}", f"({percWeekday:.2f}%)")

    dbCursor.execute("Select sum(Num_Riders) From Ridership where Type_of_Day = 'A';")  #Saturday Ridership
    row = dbCursor.fetchone()
    saturdayRidership = int(row[0])
    percSaturday = float(round((saturdayRidership / totalRidership) * 100, 2))
    print("  Saturday ridership:", f"{row[0]:,}", f"({percSaturday:.2f}%)")

    dbCursor.execute("Select sum(Num_Riders) From Ridership where Type_of_Day = 'U';")  #Sunday/Holiday Ridership
    row = dbCursor.fetchone()
    sundayOrHolidayRidership = int(row[0])
    percU = float(round((sundayOrHolidayRidership / totalRidership) * 100, 2))
    print("  Sunday/holiday ridership:", f"{row[0]:,}", f"({percU:.2f}%)")


#####################################################################
# retrieve_stations()
# This function retrieves the stations that are “like” the user’s input
#
def retrieve_stations(dbConn):
  print()
  name = str(input("Enter partial station name (wildcards _ and %): "))

  dbCursor = dbConn.cursor()
  dbCursor.execute("Select Station_ID, Station_Name From Stations where Station_Name like ? order by Station_Name asc",[name])
  rows = dbCursor.fetchall()

  if len(rows) == 0:
    print("**No stations found...")  #No records found when rows fetched are 0
    return userCommandHelper(dbConn)
  else:
    for x in rows:
      print(x[0], ":", x[1])

  return userCommandHelper(dbConn)

#####################################################################
# output_ridership()
# This function retrieves and Outputs the ridership at each station, in ascending order by station name
#
def output_ridership(dbConn):

  totalRiders = 0
  dbCursor = dbConn.cursor()
  dbCursor.execute("Select Station_Name, sum(Num_Riders) from Ridership a join Stations b where a.Station_ID = b.Station_ID group by Station_Name order by Station_Name asc")
  rows = dbCursor.fetchall()

  if len(rows) == 0:
      print("**No stations found...")  #No records found when rows fetched are 0
      return userCommandHelper(dbConn)

  print("** ridership all stations **", end="\n")

  for x in rows:
    totalRiders = totalRiders + x[1]   # total riders summation

  for y in rows:
    percRidership = float(round((y[1] / totalRiders) * 100, 2))
    print(y[0], ":", f"{y[1]:,}", f"({percRidership:.2f}%)")

  return userCommandHelper(dbConn)


#####################################################################
# top_ten_busiest()
# This Function retrieves and Outputs the top-10 busiest stations in terms of ridership, in descending order by ridership
#
def top_ten_busiest(dbConn):
  totalRiders = 0
  dbCursor = dbConn.cursor()
  secondCursor = dbConn.cursor()  # second cursor in order to store total ridership used for percentage calculation

  dbCursor.execute("Select Station_Name, sum(Num_Riders) as ridersum from Ridership a join Stations b where a.Station_ID = b.Station_ID group by Station_Name order by ridersum desc limit 10;")
  rows = dbCursor.fetchall()

  if len(rows) == 0:  #No records found when rows fetched are 0
      print("**No stations found...")
      return userCommandHelper(dbConn)

  secondCursor.execute("select sum(Num_Riders) from Ridership;")
  secondRows = secondCursor.fetchall()

  print("** top-10 stations **", end='\n')
  for x in secondRows:
    totalRiders = totalRiders + x[0]  # total riders summation

  for y in rows:
    percRidership = float(round((y[1] / totalRiders) * 100, 2))
    print(y[0], ":", f"{y[1]:,}", f"({percRidership:.2f}%)")

  return userCommandHelper(dbConn)

####################################################################
# least_ten_busiest()
# This Function retrieves and Outputs the least-10 busiest stations in terms of ridership, in ascending order by ridership
#
def least_ten_busiest(dbConn):
  totalRiders = 0
  dbCursor = dbConn.cursor()
  secondCursor = dbConn.cursor()  # second cursor in order to store total ridership used for percentage calculation

  dbCursor.execute("Select Station_Name, sum(Num_Riders) as ridersum from Ridership a join Stations b where a.Station_ID = b.Station_ID group by Station_Name order by ridersum limit 10;")
  rows = dbCursor.fetchall()

  if len(rows) == 0:  #No records found when rows fetched are 0
    print("**No stations found...")
    return userCommandHelper(dbConn)

  secondCursor.execute("select sum(Num_Riders) from Ridership;")
  secondRows = secondCursor.fetchall()

  print("** least-10 stations **", end='\n')
  for x in secondRows:
    totalRiders = totalRiders + x[0] # total riders summation

  for y in rows:
    percRidership = float(round((y[1] / totalRiders) * 100, 2))
    print(y[0], ":", f"{y[1]:,}", f"({percRidership:.2f}%)")

  return userCommandHelper(dbConn)

####################################################################
# line_color_stops()
# This function takes a color from user as input, and outputs all stop names that are part of that line, in ascending order
#
def line_color_stops(dbConn):
  print("\n")
  userColor = input("Enter a line color (e.g. Red or Yellow): ")
  dbCursor = dbConn.cursor()

  dbCursor.execute("select stop_name, direction, ada from stops s join stopdetails sd on s.stop_id = sd.stop_id join lines l on sd.line_id = l.line_id where l.color = '"+ userColor +"' COLLATE NOCASE group by stop_name order by stop_name;")
  rows = dbCursor.fetchall()

  if len(rows) == 0:  #No records found when rows fetched are 0
      print("**No such line...", end='\n')
      return userCommandHelper(dbConn)

  for x in rows:
    print(x[0], ": direction =", x[1], "(accessible? ", end='')

    if int(x[2]) == 1:  # checking if ADA value at x[2] is accessible
      print("yes)", end='\n')
    else:
      print("no)", end='\n')

  return userCommandHelper(dbConn)

####################################################################
# ridership_by_month()
# This Function Outputs total ridership by month, in ascending order by month
#
def ridership_by_month(dbConn):

  dbCursor = dbConn.cursor()
  dbCursor.execute("select strftime('%m', Ride_Date), sum(Num_Riders) from Ridership group by strftime('%m', Ride_Date) order by strftime('%m', Ride_Date) asc;")
  print("** ridership by month **", end='\n')
  rows = dbCursor.fetchall()

  for x in rows:
    print(x[0], ":", f"{x[1]:,}")

  userChoice = str(input("Plot? (y/n)"))

  if (userChoice == 'y'):

    dbCursor.execute("select strftime('%m', Ride_Date), sum(Num_Riders) from Ridership group by strftime('%m', Ride_Date) order by strftime('%m', Ride_Date) asc;")
    rows = dbCursor.fetchall()

    x = []
    y = []

    for row in rows:
      x.append(row[0])
      y.append(row[1])
    # plot labels and titles
    plt.xlabel("month")
    plt.ylabel("number of riders (x * 10^8)")
    plt.title("monthly ridership")
    plt.plot(x, y)
    plt.show()

  else:
    return userCommandHelper(dbConn)

  return userCommandHelper(dbConn)

####################################################################
# ridership_by_year()
# This function Outputs total ridership by year, in ascending order by year
#
def ridership_by_year(dbConn):
  dbCursor = dbConn.cursor()
  dbCursor.execute("select strftime('%Y', Ride_Date), sum(Num_Riders) from Ridership group by strftime('%Y', Ride_Date) order by strftime('%Y', Ride_Date) asc;")
  rows = dbCursor.fetchall()
  print("** ridership by year **", end='\n')

  for x in rows:
      print(x[0], ":", f"{x[1]:,}")

  userChoice = str(input("Plot? (y/n)"))

  if (userChoice == 'y'):
    dbCursor.execute("select strftime('%Y', Ride_Date), sum(Num_Riders) from Ridership group by strftime('%Y', Ride_Date) order by strftime('%Y', Ride_Date) asc;")
    rows = dbCursor.fetchall()

    x = []
    y = []

    for row in rows:
        yearVal = str(row[0])
        x.append(yearVal[-2:])  # Extracting last 2 digits of Year for the plot's x axis
        y.append(row[1])

    plt.xlabel("year")
    plt.ylabel("number of riders (x * 10^8)")
    plt.title("yearly ridership")
    plt.plot(x, y)
    plt.show()

  else:
    return userCommandHelper(dbConn)

  return userCommandHelper(dbConn)

####################################################################
# compare_ridership()
# This function takes user's Input for a year and the names of two stations (full or partial names), and then outputs the daily ridership at each station for that year (first and last 5 days)
#
def compare_ridership(dbConn):
  print()
  userYear = input("Year to compare against? ")
  print()
  userStation1 = input("Enter station 1 (wildcards _ and %): ")

  stationCheckFlag1 = dbConn.cursor()
  stationCheckFlag1.execute("select count(*) from Stations where Station_Name like ?;",[userStation1])
  checkRows1 = stationCheckFlag1.fetchall()
  totalStations1 = checkRows1[0][0]

  if totalStations1 < 1:
    print("**No station found...", end='\n')  #No stations found to be compared
    return userCommandHelper(dbConn)
  elif totalStations1 > 1:  #Multiple stations found in records, unable to compare
    print("**Multiple stations found...", end='\n')
    return userCommandHelper(dbConn)
  else:
    dbCursor1 = dbConn.cursor()
    dbCursor1.execute("select Station_ID, Station_Name from Stations where Station_Name like ?;",[userStation1])
    myRows1 = dbCursor1.fetchall()
    print()
    userStation2 = input("Enter station 2 (wildcards _ and %): ")
    stationCheckFlag2 = dbConn.cursor()
    stationCheckFlag2.execute("select count(*) from Stations where Station_Name like ?;",[userStation2])
    checkRows2 = stationCheckFlag2.fetchall()
    totalStations2 = checkRows2[0][0]
    
    if totalStations2 < 1:  #No stations found to be compared
      print("**No station found...", end='\n')  
      return userCommandHelper(dbConn)
    elif totalStations2 > 1:  #Multiple stations found in records, unable to compare
      print("**Multiple stations found...", end='\n')
      return userCommandHelper(dbConn)
    else:
      dbCursor2 = dbConn.cursor()
      dbCursor2.execute("select station_id, station_name from stations where station_name like ?;",[userStation2])
      myRows2 = dbCursor2.fetchall()
  
      print("Station 1:", myRows1[0][0], myRows1[0][1])
      myCursor1 = dbConn.cursor()
      myCursor1.execute("select r.Ride_Date, r.Num_Riders from Ridership r, Stations s where r.station_id = s.station_id and s.station_name = '"+ myRows1[0][1] + "' and strftime('%Y', r.Ride_Date) = '" + userYear +"' group by r.Ride_Date;")
      rowsStation1 = myCursor1.fetchall()
  
      dateStation1 = []
      ridershipStation1 = []
  
      for row in rowsStation1:
        date = row[0].split()
        dateStation1.append(date[0])
        ridershipStation1.append(row[1])
      for x in range(5):  # first 5 days range
        print(dateStation1[x], ridershipStation1[x])
      for y in range(-5, 0):  # last 5 days range
        print(dateStation1[y], ridershipStation1[y])
  
      print("Station 2:", myRows2[0][0], myRows2[0][1])
      myCursor2 = dbConn.cursor()
      myCursor2.execute("select r.Ride_Date, r.Num_Riders from Ridership r, Stations s where r.station_id = s.station_id and s.station_name = '"+ myRows2[0][1] + "' and strftime('%Y', r.Ride_Date) = '" + userYear +"' group by r.Ride_Date;")
      rowsStation2 = myCursor2.fetchall()
  
      dateStation2 = []
      ridershipStation2 = []
  
      for row in rowsStation2:
        date = row[0].split()
        dateStation2.append(date[0])
        ridershipStation2.append(row[1])
      for x in range(5):  # first 5 days range
        print(dateStation2[x], ridershipStation2[x])
      for y in range(-5, 0):  # last 5 days range
        print(dateStation2[y], ridershipStation2[y])
  
      userChoice = input("Plot? (y/n) ")
  
      if (userChoice == 'y'):
        day = list(range(0, len(dateStation1)))
        plt.plot(day, ridershipStation1, label=myRows1[0][1])
        plt.plot(day, ridershipStation2, label=myRows2[0][1])
        plt.xlabel("day")  # plot labels and titles
        plt.ylabel("number of riders")
        plt.title("riders each day of "+userYear)
        plt.show()
      else:
        return userCommandHelper(dbConn)

  return userCommandHelper(dbConn)


####################################################################
# line_color_plot()
# This function takes user's Input for a line color and outputs all station names that are part of that line, in ascending order
#
def line_color_plot(dbConn):
  print()
  color = input("Enter a line color (e.g. Red or Yellow): ")
  stationCheckFlag1 = dbConn.cursor()
  stationCheckFlag1.execute("select distinct a.Station_Name, b.Latitude, b.Longitude from Stations as a join Stops as b join Stopdetails as sd join Lines as l where a.Station_ID = b.Station_ID and b.Stop_ID = sd.Stop_ID and sd.line_id = l.line_id and l.color = '"+color+"' COLLATE NOCASE group by a.station_name order by a.station_name;")
  checkRows1 = stationCheckFlag1.fetchall()
  
  station_name = []
  latitude_list = []
  longitude_list = []

  if len(checkRows1) == 0:  #No records found when rows fetched are 0
    print("**No such line...")
    return userCommandHelper(dbConn)
  
  for row in checkRows1:
    print(row[0],":",end = " ")
    print("("+str(row[1])+", "+str(row[2])+")")
    station_name.append(row[0])
    latitude_list.append(row[1])
    longitude_list.append(row[2])

  print()
  plot = input("Plot? (y/n)")
  if(plot == 'y'):
    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
    plt.imshow(image, extent=xydims)
    plt.title(color + " line")
    
    if (color.lower() == "purple-express"):
      color="Purple" # color="#800080"  
    
    size = len(latitude_list)
    plt.plot(longitude_list, latitude_list, "o", c=color)
    for sz in range(size):
      plt.annotate(station_name[sz], (longitude_list[sz], latitude_list[sz]))
    
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    plt.show()
    
  else:
    return userCommandHelper(dbConn)

  return userCommandHelper(dbConn)
    

####################################################################
# userCommandHelper()
# This function calls the other functions to execute various SQL queries based on the user's command, including 'x' for exit.
#
def userCommandHelper(dbConn):

  userCommand = (input("\n" + "Please enter a command (1-9, x to exit): "))
  if userCommand == '1':
    retrieve_stations(dbConn)
  elif userCommand == '2':
    output_ridership(dbConn)
  elif userCommand == '3':
    top_ten_busiest(dbConn)
  elif userCommand == '4':
    least_ten_busiest(dbConn)
  elif userCommand == '5':
    line_color_stops(dbConn)
  elif userCommand == '6':
    ridership_by_month(dbConn)
  elif userCommand == '7':
    ridership_by_year(dbConn)
  elif userCommand == '8':
    compare_ridership(dbConn)
  elif userCommand == '9':
    line_color_plot(dbConn)
  elif userCommand == 'x':
    exit()
  else:
    print("**Error, unknown command, try again...")
    return userCommandHelper(dbConn)


####################################################################
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)

userCommandHelper(dbConn)

#
# done
#
