from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# import chromedriver_binary  # Adds chromedriver binary to path
import time
import os

import itertools
import random
import datetime


# Returns a new browser
def newBrowser():

    print("newBrowser")
    browserProfile = webdriver.ChromeOptions()
    browserProfile.add_experimental_option(
        'prefs', {'intl.accept_languages': 'en,en_US'})

    browser = webdriver.Chrome(options=browserProfile)

    # If an element is not found, browser will try again every 0.5s until 3 seconds
    browser.implicitly_wait(2)

    return browser


# aws login
def awsLogin(browser, aws_id, username, password):

    print("awsLogin")

    # Build AWS Console URL with aws_id
    aws_id = str(aws_id)
    url = "https://%s.signin.aws.amazon.com/console" % aws_id

    # Open browser with the starting URL
    browser.get(url)
    browser.refresh()
    time.sleep(2)

    usernameInput = browser.find_element("name", "username")
    passwordInput = browser.find_element("name", "password")

    usernameInput.send_keys(username)
    passwordInput.send_keys(password)
    passwordInput.send_keys(Keys.ENTER)
    time.sleep(2)

    print(
        f"Successfully logged in to AWS account number {aws_id} with username {username}")


# submit to race
def submit_to_race(browser, aws_id, race_id, modelname):

    print("submit_to_race")

    submitUrl = "https://us-east-1.console.aws.amazon.com/deepracer/home?region=us-east-1#competition/arn%3Aaws%3Adeepracer%3A%3A{aws_id}%3Aleaderboard%2F{race_id}/submitModel"
    submitUrl = submitUrl.format(aws_id=aws_id, race_id=race_id)

    browser.get(submitUrl)
    browser.refresh()
    time.sleep(5)

    # choose a model dropdown
    chooseModelDropdown = browser.find_element(By.XPATH,
                                               '//button[@type="button"]/*[text()="Choose a model"]')
    # click once
    chooseModelDropdown.click()
    # find div class contain awsui_description and text = modelname
    divSelect = browser.find_element(By.XPATH,
                                     '//*[contains(text(), "%s")]' % modelname)
    # click once as select
    divSelect.click()

    # enter race
    enterRaceButton = browser.find_element(By.XPATH,
                                           '//button[@type="submit"]/*[text()="Enter race"]')
    enterRaceButton.click()

    # Sometimes, pressing the submit button will not trigger a submit
    # Therefore, just retry 5 times
    re_press_submit = 5
    while re_press_submit > 0:
        try:
            enterRaceButton.click()
            re_press_submit -= 1
            time.sleep(2)
        except:
            # If click failed, means that submit was successful and we got re-routed to Event starting screen
            re_press_submit = 0

    time.sleep(15)

    print(f"{datetime.datetime.now()} Submitted model {modelname} to {race_id}")


# submit to race at multiple time
def submit_to_race_multiple(browser, aws_id, race_id, modelname, repeat_hours=9):

    print("submit_to_race_multiple")
    # Calculate when to stop
    datetime_stop = datetime.datetime.now() + datetime.timedelta(hours=repeat_hours)

    # Count number of submits
    count_submits = 0
    count_fails = 0

    # Repeat loop until time is up
    while datetime.datetime.now() < datetime_stop:
        try:
            # Submit model to summit
            submit_to_race(browser, aws_id, race_id, modelname=modelname)
            # Wait for 10 minutes before attempting submit again
            time.sleep(10*60)
        except:
            # If failed to submit, wait for 2 minutes and try again
            count_fails += 1
            time.sleep(2*60)
            # If failed 5 times, try to log back in
            if count_fails >= 10:
                awsLogin()
        else:
            # If there was no error, increase counter by 1
            count_submits += 1
            count_fails = 0

    # Print final submit count
    print(f"Submitted number of models to the race: {count_submits}")


def main():
    # open browser
    browser = newBrowser()
    # get environment variable
    with open("env.txt", 'r') as f:
        [aws_id, username, password, race_id, modelname] = f.read().splitlines()

    # login to aws
    awsLogin(browser, aws_id, username, password)

    # Submit the model to the summit race once
    submit_to_race(browser, aws_id, race_id, modelname=modelname)

    # Submit the model to the summit race for multiple hours
    # submit_to_race_multiple(browser, aws_id, race_id, modelname=modelname, repeat_hours=12)

    # quit browser
    # browser.quit()


if __name__ == "__main__":
    main()
