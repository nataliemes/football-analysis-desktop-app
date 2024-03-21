"""
OOP2 Python - Final Project 2022
Natalie Mesablishvili
"""

from project import Ui_MainWindow
import sys
from PyQt5 import QtWidgets
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# from logging_setup import logging   # for using logging_setup.py directly
import logging
import logging.config
import json

# reading the logging configuration from a json file
with open("logging_config.json", "r", encoding="utf-8") as fd:
    logging.config.dictConfig(json.load(fd))

logger = logging.getLogger("my_app")

class Date():
    """
    Object: Date
    Attributes: day, month, year
    Purpose: creates a Date object to store the current date
    """
    def __init__(self, d, m, y):
        """
        Function: constructor of class Date
        Purpose: constructs an instance of class Date
        Parameters: day, month, year
        Return value: none
        """
        self.day=d
        self.month=m
        self.year=y

class Result():
    """
    Object: Result
    Attributes: home_team, away_team, home_score, away_score
    Purpose: creates a Result object to store the participant countries of the match & their scores
    """
    def __init__(self, home_team, away_team, home_score, away_score):
        """
        Function: constructor of class Result
        Purpose: constructs an instance of class Result
        Parameters: home_team, away_team, home_score, away_score
        Return value: none
        """
        self.home_team=home_team
        self.away_team=away_team
        self.home_score=int(home_score)
        self.away_score=int(away_score)

class Match(Date, Result):
    """
    Object: Match
    Attributes: day, month, year, home_team, away_team, home_score, away_score, tournament
    Purpose: creates a Match object to store all the data about the match
             inherits from classes Date & Result, also has its own attributes - tournament,
             and winner & loser - names of countries according to the result of the match
    """
    def __init__(self, d, m, y, home_team, away_team, home_score, away_score, tournament):
        """
        Function: constructor of class Match
        Purpose: constructs an instance of class Match
        Parameters: day, month, year, home_team, away_team, home_score, away_score, tournament
        Return value: none
        """

        # constructing the given date & result of the match
        Date.__init__(self, d, m, y)
        Result.__init__(self, home_team, away_team, home_score, away_score)
        self.tournament=tournament  # also storing the name of the tournament

        # determining which country won and which one lost according to the scores
        if int(home_score)>int(away_score):
            self.winner = home_team
            self.loser = away_team
        elif int(home_score)<int(away_score):
            self.winner = away_team
            self.loser = home_team
        else:
            self.winner, self.loser = "Tie", "Tie"
    
    def obj_to_dict(self):
        """
        Function: object to dictionary
        Purpose: transforms an object of class Match into a dictionary, so that it can be saved on MongoDB database
        Parameters: none
        Return value: dictionary obtained from the object
        """

        dct = {"day": self.day, "month": self.month, "year": self.year,
                "home_team": self.home_team, "away_team": self.away_team,
                "home_score": self.home_score, "away_score": self.away_score,
                "tournament": self.tournament, "winner": self.winner, "loser": self.loser}
        
        return dct       


class myApp(QtWidgets.QMainWindow):
    """
    Object: myApp
    Attributes: ui, conn, base, coll, figure, canvas, tab
    Purpose: creates an object for GUI
    """
    def __init__(self):
        """
        Function: constructor of class myApp
        Purpose: constructs the myApp object
        Parameters: none
        Return value: none
        """
        super(myApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("International Football Statistics")

        logger.info("important: application window opened")

        # connecting to the MongoDB database
        self.conn = MongoClient()
        self.base = self.conn["Football_base"]
        self.coll = self.base["Result_recs"]

        logger.info("connected to MongoDB database")

        # making the day/month/year textboxes unavailable for the user
        # so that they will choose the date from the calendar widget
        self.ui.day_box.setEnabled(False)
        self.ui.month_box.setEnabled(False)
        self.ui.year_box.setEnabled(False)

        def fields_enabled(arg):
            """
            Function: changing the accecibility of the fields
            Purpose: enables or disables all the textboxes depending on the argument recieved
            Parameters: boolean variable True or False
            Return value: none
            """
            self.ui.calendarWidget.setEnabled(arg)
            self.ui.tournament_box.setEnabled(arg)
            self.ui.homeTeam_box.setEnabled(arg)
            self.ui.awayTeam_box.setEnabled(arg)
            self.ui.homeScore_box.setEnabled(arg)
            self.ui.awayScore_box.setEnabled(arg)
            self.ui.userInput_box.setEnabled(arg) 
            
            self.ui.butt_save_match.setEnabled(arg) 
            self.ui.butt_plot_diagram.setEnabled(arg) 
    
        # at first all the textboxes are disabled
        fields_enabled(False)
        

        def clear():
            """
            Function: clearing fields
            Purpose: empty all the textboxes that the user might have filled
            Parameters: none
            Return value: none
            """
            self.ui.day_box.clear()
            self.ui.month_box.clear()
            self.ui.year_box.clear()
            self.ui.tournament_box.clear()
            self.ui.homeTeam_box.clear()
            self.ui.awayTeam_box.clear()
            self.ui.homeScore_box.clear()
            self.ui.awayScore_box.clear() 
            self.ui.textLabel.clear()
      

        def date_chosen():
            """
            Function: determining chosen date
            Purpose: checks what date user marked on the calendar widget
                     & displays this date in the appropriate textboxes
            Parameters: none
            Return value: none
            """
            date = self.ui.calendarWidget.selectedDate()
            self.ui.day_box.setPlainText(f'{date.day()}')
            self.ui.month_box.setPlainText(f'{date.month()}')    
            self.ui.year_box.setPlainText(f'{date.year()}')  

            logger.debug(f"date chosen: day {date.day}, month {date.month}, year {date.year}")

        # while the calendar widget is activated, date textboxes will be updated accordingly
        self.ui.calendarWidget.activated.connect(date_chosen)

        def butt_make_db_clicked():
            """
            Function: "create a database" button clicked 
            Purpose: create a MongoDB database by reading from csv file
            Parameters: none
            Return value: none
            """
            logger.info("important: create database button clicked")
            clear()        

            # checking whether or not database already exists
            dbnames = self.conn.list_database_names()
            if 'Football_base' in dbnames:
                self.ui.textLabel.setText("Database already exists!")
                fields_enabled(True)
                logger.warning("user tried to create database which already exists")
            else:
                try:  # trying to read from the file if such a file exists
                    df = pd.read_csv('results.csv')  # create a dataframe of results
                except:
                    self.ui.textLabel.setText("File for database not found!")
                    logger.critical("important: file for database not found!")
                    return
                
                # creating a MongoDB database from dataframe
                self.coll.insert_many(df.to_dict('records'))
                self.ui.textLabel.setText("Database was created!")
                fields_enabled(True)  # opening up all the textboxes

                logger.info("database created")
                logger.info("textboxes opened")
        

        def butt_save_match_clicked(): # adds data of one student to the database
            """
            Function: "save the match" button clicked 
            Purpose: saves the match that the user entered
            Parameters: none
            Return value: none
            """
            logger.info("important: save match button clicked")
            
            # reading user's input
            day = self.ui.day_box.toPlainText()
            month = self.ui.month_box.toPlainText()
            year = self.ui.year_box.toPlainText()
            homeTeam = self.ui.homeTeam_box.toPlainText()
            awayTeam = self.ui.awayTeam_box.toPlainText()
            homeScore = self.ui.homeScore_box.toPlainText()
            awayScore = self.ui.awayScore_box.toPlainText()
            tournament = self.ui.tournament_box.toPlainText()

            clear()  # clearing all the fields after reading them

            logger.debug(f"info read from calendar - day: {day}, month: {month}, year: {year}")
            logger.debug(f"info read from user - homeTeam: {homeTeam}, awayTeam: {awayTeam}, homeScore: {homeScore}, awayScore: {awayScore}, tournament: {tournament}")        
                         

            # error checking
            validInput = True
            if day == "": validInput = False
            if homeScore == "" or int(homeScore)<0: validInput = False
            elif awayScore == "" or int(awayScore)<0: validInput = False

            if not validInput:
                self.ui.textLabel.setText("Invalid input, match was not added!")
                logger.error("user entered invalid input for the match")
                return

            # adding the match to the database if it is valid
            currentMatch = Match(day, month, year, homeTeam, awayTeam, homeScore, awayScore, tournament)                                 
            currentMatch = currentMatch.obj_to_dict() # transforming the object to a dictionary  
            self.coll.insert_one(currentMatch)
            self.ui.textLabel.setText("New match was added!")

            logger.info("user's new match was added to the database")

            logger.debug(f"info of the match added to the database: day {day}, month {month}, year {year}, \
                         homeTeam {homeTeam}, awayTeam {awayTeam}, homeScore {homeScore}, \
                         awayScore {awayScore}, tournament {tournament}")
            
            logger.debug(f"date of the match added to the database - day: {day}, month: {month}, year: {year}")
            logger.debug(f"info of the match added to the database - homeTeam: {homeTeam}, awayTeam: {awayTeam}, homeScore: {homeScore}, awayScore: {awayScore}, tournament: {tournament}")


        def butt_plot_diagram_clicked():
            """
            Function: "plot diagram" button clicked 
            Purpose: plot the appropriate diagram for the user in different styles
            Parameters: none
            Return value: none
            """
            logger.info("important: plot button clicked")

            clear()
            self.ui.charts_tab.clear()  # clearing the charts tab in case previous charts are there            

            def createTab(chartType, grp_df1, grp_df2=""):
                """
                Function: creating a tab
                Purpose: adds a new tab in the charts tab widget & displays a diagram in it
                Parameters: string - what type the diagram should be
                            series - what data should be visualized
                Return value: none
                """

                logger.info("tab creation started")

                # adding a new tab into the charts tab widget
                self.figure = plt.figure()
                self.canvas = FigureCanvas(self.figure)
                layout = QtWidgets.QVBoxLayout()
                layout.addWidget(self.canvas)
                self.tab = QtWidgets.QWidget()
                QtWidgets.QTabWidget.addTab(self.ui.charts_tab, self.tab, f"{chartType} chart") 
                self.tab.setLayout(layout)

                logger.info("tab creation ended")

                # bar chart includes lots of years on the x-axis,
                # so, making sure that the labels don't overlap
                if chartType=='bar':
                    plt.rc('xtick', labelsize=5)
                else:
                    plt.rc('xtick', labelsize = 10)

                
                logger.info("diagram plotting started")

                # plotting the diagrams
                if type(grp_df2)==str:                     
                        grp_df1.plot(color = 'rebeccapurple', kind=str(chartType))
                else:
                    grp_df1.plot(color='violet', kind=chartType)
                    grp_df2.plot(color='midnightblue', kind=chartType)   

                logger.info("diagram plotting finished")              
            

            # reading user's input
            parameter = self.ui.comboBox_parameter1.currentText()
            userInput = self.ui.userInput_box.toPlainText()

            logger.debug(f"user input for plotting diagrams: {userInput}")

            if (userInput == ""):
                logger.error("user entered nothing when attempting to plot")
                return  # error checking                    
            
            # first reading all the data from MongoDB database to pandas
            df = pd.DataFrame(list(self.coll.find()))   
            logger.info("reading data from MongoDB database to pandas")           

            if (parameter == "# of victories"): parameter = "winner"
            elif (parameter == "# of defeats"): parameter = "loser"                

            if parameter == "Goals scored":

                # analyzing data with pandas module
                df_temp1 = df[df["home_team"] == userInput]
                if len(df_temp1) == 0:   # error checking
                    logger.warning(f"{userInput} not found as a home_team in the database")
                    return
                grp_df1 = df_temp1["home_score"].groupby(df_temp1["year"]).sum()
                
                df_temp2 = df[df["away_team"] == userInput]
                if len(df_temp2) == 0:   # error checking
                    logger.warning(f"{userInput} not found as an away_team in the database")
                    return
                grp_df2 = df_temp2["away_score"].groupby(df_temp2["year"]).sum()
                
                # creating different types of diagrams in different tabs
                chartTypes = ['area', 'bar', 'line']
                for chartType in chartTypes:
                    createTab(chartType, grp_df1, grp_df2) 

            else:  # if parameter is "# of victories" or "# of defeats"
                # analyzing data with pandas module
                df_temp = df[df[parameter] == userInput]
                if len(df_temp) == 0:
                    logger.warning(f"{userInput} not found in the '{parameter}' column in the database")
                    return  # error checking
                grp_df1 = df_temp["year"].groupby(df_temp["year"]).count()

                # creating different types of diagrams in different tabs 
                createTab("area", grp_df1) 
                createTab("bar", grp_df1)
                createTab("line", grp_df1)
                createTab("hist", grp_df1)
                createTab("box", grp_df1)
                    


        # connecting each button to the corresponding function
        self.ui.butt_make_db.clicked.connect(butt_make_db_clicked)
        self.ui.butt_save_match.clicked.connect(butt_save_match_clicked)  
        self.ui.butt_plot_diagram.clicked.connect(butt_plot_diagram_clicked)

          
# opening the window until the user closes it
app = QtWidgets.QApplication([])
application = myApp()
application.show()
sys.exit(app.exec())