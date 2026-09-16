Demo Link : https://drive.google.com/file/d/1aRIjK7j0fsX9hLNz048KS_ojUKfmVoCT/view?usp=drive_link


Drive Link: https://drive.google.com/drive/folders/1qTPge7sJg2tQ2jeazTXE79MWN8ntLOSK


Dashboard Link: https://docs.google.com/spreadsheets/d/1eV10lFZPSP-VRwzdwCfoloq6Oo-JBCMzOH1XV7ER7qw/edit?gid=0#gid=0


Instagram Scraper
A Selenium-based Instagram scraper that collects posts and reels from the Instagram Explore feed and extracts useful metadata such as captions, hashtags, mentions, locations, and timestamps.

Project Structure
Instagram-Scraper/ │ ├── setup.sh ├── installation.sh ├── web_scrapper_new.py ├── Fast_Webscrapper_26.08_for_test.ipynb ├── README.md └── .gitignore

Requirements
Operating System
The project is designed to work with:

Windows using Git Bash
macOS
Linux
Windows users must use Git Bash to run the .sh files.

Python
Python 3.11 or newer is recommended.

Check your Python installation:

python --version
or:

python3 --version
Google Chrome
Google Chrome must be installed because the scraper uses Selenium with Chrome WebDriver.

Internet Connection
An active internet connection is required to access Instagram.

Required Python Libraries
The setup script installs the following packages:

selenium
webdriver-manager
pandas
openpyxl
jupyter
jupyterlab
notebook
ipykernel
If installing manually:

pip install selenium webdriver-manager pandas openpyxl jupyter jupyterlab notebook ipykernel
Windows Installation
1. Install Git Bash
Install Git for Windows, which includes Git Bash.

After installation, open Git Bash.

2. Open the Project Folder
Open Git Bash inside the folder containing the project files.

The folder should contain:

setup.sh
installation.sh
web_scrapper_new.py
Fast_Webscrapper_26.08_for_test.ipynb
3. Run the Installation Script
Run:

bash installation.sh
If you are using the newer setup script, run:

bash setup.sh
The setup script will:

Detect your operating system.
Check Python installation.
Create a virtual environment.
Install required packages.
Configure Jupyter.
Start the scraper.
macOS / Linux Installation
Open Terminal inside the project folder and run:

bash setup.sh
Virtual Environment
The setup script creates a virtual environment named:

venv_instagram
The Python executable is located at:

Windows:

venv_instagram/Scripts/python.exe
macOS / Linux:

venv_instagram/bin/python
All required Python packages are installed inside this virtual environment.

Running the Scraper
The main scraper is:

web_scrapper_new.py
Windows
From Git Bash:

venv_instagram/Scripts/python.exe web_scrapper_new.py
macOS / Linux
venv_instagram/bin/python web_scrapper_new.py
The program will ask:

Enter scraping duration in minutes:
Enter the required duration and press Enter.

Login Process
When the scraper starts:

Chrome opens the Instagram login page.
The configured login fields are filled automatically.
Complete the login manually if CAPTCHA or 2FA is required.
The scraper waits for the login process to complete.
Instagram Explore is opened.
Scraping begins.
Scraping Workflow
main() │ ├── Ask for scraping duration │ ├── create_driver() │ ├── setup_csv() │ ├── load_seen_urls() │ ├── login_instagram() │ ├── open_explore() │ ├── scrape_feed() │ │ │ ├── collect_new_links() │ ├── scrape_url() │ ├── extract_metadata() │ ├── save_batch_to_csv() │ └── save_seen_urls() │ └── Close browser

Data Collected
The scraper creates CSV data with the following fields:

Field	Description
type	Post or Reel
url	Instagram post/reel URL
caption	Caption text
mentions	Mentions found in the caption
hashtags	Hashtags found in the caption
location	Location, if available
timestamp	Instagram post timestamp
Output Files
CSV File
A timestamped CSV file is generated after scraping.

Example:

202608271530_instagram_data.csv
Seen URLs
The scraper also creates:

seen_urls.pkl
This file stores previously processed URLs and helps prevent duplicate scraping.

Jupyter Notebook
The repository contains:

Fast_Webscrapper_26.08_for_test.ipynb
Windows
Run:

venv_instagram/Scripts/python.exe -m jupyter lab
macOS / Linux
Run:

venv_instagram/bin/python -m jupyter lab
Then open:

Fast_Webscrapper_26.08_for_test.ipynb
Configuration
Some scraper settings can be modified inside:

web_scrapper_new.py
Important settings include:

LOGIN_WAIT_SECONDS = 60
BATCH_SIZE = 20
SEEN_FILE = "seen_urls.pkl"
LOGIN_WAIT_SECONDS
Controls how long the scraper waits for the Instagram login process.

BATCH_SIZE
Controls how many scraped records are collected before being saved to the CSV.

SEEN_FILE
Stores previously processed Instagram URLs.

Troubleshooting
Python Not Found
If you receive an error that Python cannot be found, install Python 3.11 or newer and make sure Python is added to PATH.

Verify:

python --version
Git Bash Not Found
Windows users should install Git for Windows and use Git Bash to execute the .sh files.

Setup Script Closes Immediately
Do not double-click the .sh file.

Open Git Bash manually and run:

bash setup.sh
or:

bash installation.sh
This keeps the terminal open so that error messages can be viewed.

Selenium / Chrome Error
Make sure Google Chrome is installed and working correctly.

Recommended .gitignore
Do not upload the virtual environment or generated files to GitHub.

Create a .gitignore file containing:

venv_instagram/
__pycache__/
*.pyc
*.csv
seen_urls.pkl
.ipynb_checkpoints/
Quick Start
Windows
# Open Git Bash in the project folder

bash setup.sh

# Run the scraper

venv_instagram/Scripts/python.exe web_scrapper_new.py
macOS / Linux
bash setup.sh

venv_instagram/bin/python web_scrapper_new.py
Important Security Note
Do not commit Instagram usernames, passwords, API keys, or other credentials to a public GitHub repository.

Credentials should be stored using environment variables or another secure configuration method.

Disclaimer
This project is intended for educational and research purposes.

Users are responsible for complying with Instagram's terms, applicable laws, and any restrictions related to automated access and data collection.
