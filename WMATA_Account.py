from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from time import sleep, strftime, gmtime, time
import getpass
import csv
import numpy


class WMATA_Account:
    def __init__(self, username="",password="", visible = False, login_url = "https://smartrip.wmata.com/Account/Login", account_url = "https://smartrip.wmata.com/Account/Summary", user_box = 'UserName', pass_box = 'Password', login_button = 'log_in', card_class = "cardInfo", number_class = "card-number", card_details_xpath = "//div[@class='col-md-16 col-xs-24 info-value']", status_xpath = "//div[@class='col-md-16 col-xs-24 info-value ']", value_xpath = "//div[@class='col-lg-7 col-md-12 col-xs-11 xs-text-right']", card_name = "Card Name", card_number = "Number", card_status = "Status", card_date = "Expiration Date", card_value = "Value", WMATA_browser = None):

        #sets the different lists which will contain the out put data for the xml file
        self._card_name_list = []
        self._card_number_list = []
        self._card_status_list = []
        self._card_date_list = []
        self._card_value_list = []        
        
        #sets the names of the columns in the xml file
        self._card_name = card_name
        self._card_number = card_number
        self._card_status =  card_status
        self._card_date = card_date
        self._card_value = card_value

        #sets the username for the WMATA account to "" so that _enter_Username will be called
        self._username = username
        
        #sets the password for the WMATA account to "" so that _enter_Password will be called
        self._password = password
        
        #this url is set by default to the login url of WMATA as of 12/22/2023
              #to update this, change the input above to the new login url
        self._login_url = login_url
        
        #this is the HTML NAME for the username box in the WMATA login page as of 12/22/2023
              #to update this, change the input above to the new username box NAME
        self._user_box = user_box
        
        #this is the HTML NAME for the password box in the WMATA login page as of 12/22/2023
              #to update this, change the input above to the new password box NAME        
        self._pass_box = pass_box
        
        #this is the HTML NAME for the login button in the WMATA login page as of 12/22/2023
              #to update this, change the input above to the new login button NAME        
        self._login_button = login_button
        
        #this url is set by default to the account management page url of WMATA as of 12/22/2023
              #to update this, change the input above to the new account management page url
        self._account_url = account_url
        
        #this is the HTML CLASS_NAME for the individual cards in the WMATA account page as of 12/27/2023
              #to update this, change the input above to the new card CLASS_NAME
        self._card_class = card_class
        
        #this is the HTML CLASS_NAME for the number of the individual cards in the WMATA account page as of 12/27/2023
              #to update this, change the input above to the new number CLASS_NAME
        self._number_class = number_class
        
        #this is the HTML XPATH for the details of the card on the WMATA individual card page as of 12/27/2023
              #to update this, change the input above to the new details XPATH
        self._card_details_xpath = card_details_xpath
        
        #this is the HTML XPATH for the status of the card on the WMATA individual card page as of 12/27/2023
              #to update this, change the input above to the new status XPATH
        self._status_xpath = status_xpath

        #this is the HTML XPATH for the value of the card on the WMATA individual card page as of 12/27/2023
              #to update this, change the input above to the new value XPATH
        self._value_xpath = value_xpath
        
        self._percentage_complete = 0
        
        self._total_time = 0
                
        #creates a virtual display if the visible setting is set to False
        if WMATA_browser == None:
            if visible == False:
                nonvis_options = Options()
                nonvis_options.add_argument("--headless")
                self._WMATA_browser = webdriver.Edge(options=nonvis_options)
            else:
                self._WMATA_browser = webdriver.Edge()
        else: 
            self._WMATA_browser = WMATA_browser
    
    #has the user set the username of the object
    def _enter_Username(self):
        user = input("Please enter the username for your WMATA account:\n")
        self._username = user
        
    #has the user set the password of the object     
    def _enter_Password(self):
        password = getpass.getpass("Please enter the password for your WMATA account:\n")
        self._password = password
    
    #simply uses the close function from the browser object
    def close_Window(self):
        self._WMATA_browser.close()
    
    #uses the saved information of the class to set the 
    def login(self):

        while self._username == "":
            self._enter_Username()
        while self._password == "":
            self._enter_Password()
           
        #load the login webpage
        self._WMATA_browser.get(self._login_url) 
        
        #finds the text boxes for the username and password as well as the login button
        user_input_search = self._WMATA_browser.find_element(By.NAME,self._user_box)
        pass_input_search = self._WMATA_browser.find_element(By.NAME, self._pass_box)
        login_input_search = self._WMATA_browser.find_element(By.NAME, self._login_button)
        
        #enters the username and password then waits a second for it to register
        user_input_search.send_keys(self._username)
        pass_input_search.send_keys(self._password)
        sleep(1)
        
        #after waiting a second for the inputs, the button to login is pressed.
        login_input_search.click()
        sleep(5)
        
        #after waiting ten seconds, the program determines whether the login was successful or not
              #if successful, the process of scraping the data can begin.
              #if unsuccessful, the browser will attempt to login again.
        if self._WMATA_browser.current_url == self._login_url:
            self._username = ""
            self._password = ""
            print("Incorrect username and/or password. Please try entering them in again")
            self.login()
        else:
            print("Login Successful!")
            if self._WMATA_browser.current_url != self._account_url:
                self._WMATA_browser.get(self._account_url)
    
    #after logging-in, the data is scrapped from the WMATA account page and the individual WMATA card pages
    def scrape_data(self):
        
        timed_response = 0
        
        #preliminary announcements to user
        print("Please wait as we gather the data to be put into a .csv file.....")
        print("(This can take some time to complete depending on the current internet traffic to the WMATA website and the number of cards.)")
        
        #variables and empty lists are initialized for later usage
        acc = 0
        numOp = 0
        totalNumOp = len(self._WMATA_browser.find_elements(By.CLASS_NAME, self._card_class))
        tmp_elements = []
        tmp_data = ""
        tmp_page = []
        
        #first makes sure that the current browser page is correct and otherwise will attempt to login
        if self._WMATA_browser.current_url != self._account_url:
            self.login()

        #collects all the card numbers and stores them in a list
        tmp_page = self._WMATA_browser.find_elements(By.CLASS_NAME, self._number_class)
        for i in tmp_page:
            self._card_number_list.append(i.text)
        
        #iterates through each the WMATA card pages to collect the card data
        for i in range(totalNumOp):
            
            #selects the current card in the iteration
            tmp_elements = self._WMATA_browser.find_elements(By.CLASS_NAME, self._card_class)
            tmp_elements[i].click()
            
            #waits for the browser to finish loading the new page
            while self._WMATA_browser.current_url == self._account_url:
                sleep(1)
                timed_response += 1
                if timed_response == 11:
                    tmp_elements[i].click()
                    timed_response = 0
            
            #finds the card name and the expiration date for the card
            tmp_page.clear()
            tmp_page = self._WMATA_browser.find_elements(By.XPATH, self._card_details_xpath)
            for i in tmp_page:
                acc += 1
                tmp_data = i.text
                if acc == 1:
                    self._card_name_list.append(tmp_data[:-5])
                else:
                    self._card_date_list.append(tmp_data)
            acc = 0
            
            #finds the status of the metro card on the metro card page
            tmp_data = self._WMATA_browser.find_element(By.XPATH, self._status_xpath)
            self._card_status_list.append(tmp_data.text)
            
            #finds the value of the metro card on the metro card page
            tmp_data = self._WMATA_browser.find_element(By.XPATH, self._value_xpath)
            self._card_value_list.append(tmp_data.text)
            
            #returns back to the WMATA account page
            self._WMATA_browser.get(self._account_url)
            while self._WMATA_browser.current_url != self._account_url:
                sleep(1)
            
            #registers the current status of the operation and prints to output once it is 25, 50, 75, or 100 percent complete
            numOp += 1
            self._percentage_complete = ((numOp * 10000) // totalNumOp) / 100
            if self._percentage_complete % 1 == 0:
                print("{0} Percent complete".format(self._percentage_complete//1))
                
    #uses the current date and time as well as the account name to have uniquely identifiable name per file
          #writes the account details into the .csv file
    def _build_CSV(self):

        file_name = "WMATA_Account_{0}_{1}.csv".format(self._username, strftime("%Y-%m-%d_%H%M%S", gmtime())) 
        
        fields = [self._card_name, self._card_number, self._card_status, self._card_date, self._card_value]
        
        rows = numpy.array([self._card_name_list, self._card_number_list, self._card_status_list, self._card_date_list, self._card_value_list])
        
        with open(file_name, 'w', newline='') as WMATA_csvfile:
            
            WMATA_csvwriter = csv.writer(WMATA_csvfile)
            
            WMATA_csvwriter.writerow(fields)
            
            WMATA_csvwriter.writerows(rows.T)

    
    #executes the downloading of the account info and tracks the total amount of time taken
    def download_Account_Info(self):
        
        start_time = 0
        end_time = 0
        
        self.login()
        
        start_time = time()
        self.scrape_data()
        self.close_Window()
        self._build_CSV()
        end_time = time()
        
        self._total_time = end_time - start_time
        hours = self._total_time // 3600
        minutes = (self._total_time - (hours*3600)) // 60
        seconds = (((self._total_time - (hours*3600) - (minutes*60)) * 10000) // 1) / 10000
            
        print("Total Time Elapsed:", hours, "Hours;", minutes, "Minutes;", seconds, "Seconds")
        getpass.getpass("Press 'ENTER' to exit.")

def main():
    browser = WMATA_Account()
    browser.download_Account_Info()
    sleep(1)
    
if __name__ == '__main__':
    main()
