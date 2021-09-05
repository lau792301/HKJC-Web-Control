# HKJC Web Control
The template of selenium web control including login, marksix

## Step 1 -- Install Firefox

## (Optional) Download webdrivers for your system operation
`.modules/webdriver` folder already contains related version for Window and Linux
https://github.com/mozilla/geckodriver/releases

## Step 2 -- Install related Python library
pip3 install -r requirements.txt

## Step 3 -- Create `.env` and insert your HKJC information
ACCOUNT = `<Account>` \
PASSWORD = `<Password>`

## Step 4 -- Uncomment the code in `main.py` and run it