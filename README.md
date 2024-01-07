# WMATA_Account_CSV
Creates a CSV file of WMATA Metro information associated with cards on a single WMATA account after logging in.

**Currently Only Works for Windows Devices!!!**
The purpose behind this project is to create a script which takes the information that is located on the WMATA Metro website and puts it into a ".csv" file.
My reason for making this script is that there isn't a "Download CSV" feature for the WMATA Metro website. This makes the process of tracking multiple cards on an account to be rather difficult since one has to go under each individual card's webpage to see the following:
1. The Status of the Card
2. The Expiration Date of the Card
3. The Monetary Value of the Card
4. The Pending Monetary Value of the Card
This is merely inconvenient if one has less than a dozen cards. However, if one is part of an organization which has a multitude of WMATA Metro cards, this becomes a large waste of time to track the individual card information.

What this script does is:
1. Has the user enter the Username and Password
2. Uses the python Selenium module (https://pypi.org/project/selenium/) to login and go under the individual cards to gather the information. The script gathers: The Card Name, The Card Number, The Card Status, The Card Expiration Date, The Card Value, and The Card Pending Value.
3. Creates a ".csv" file with the name of the account and the current date and time in its name that contains the gathered information.
4. Stores the ".csv" file in a subfolder called "Downloaded_CSVs"
