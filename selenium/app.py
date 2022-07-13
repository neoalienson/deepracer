from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# import chromedriver_binary  # Adds chromedriver binary to path
import time
import os

import itertools
import random
import datetime

hasPromptLogin = True
aws_id = ""
username = ""
password = ""
prompt_email = ""
prompt_password = ""
race_id = ""
modelname = ""


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
def awsLogin(browser):

    print("awsLogin")

    # Build AWS Console URL with aws_id
    global aws_id
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

    if hasPromptLogin:
        awsPromptLogin(browser)


def awsPromptLogin(browser):

    print("awsPromptLogin")

    # url = "https://us-east-1.console.aws.amazon.com/deepracer/home#welcome"
    url = "https://us-east-1.console.aws.amazon.com/deepracer/home?region=us-east-1#competition/arn%3Aaws%3Adeepracer%3A%3A{aws_id}%3Aleaderboard%2F{race_id}/submitModel"
    url = url.format(aws_id=aws_id, race_id=race_id)
    browser.get(url)
    browser.refresh()
    time.sleep(1)

    emailInput = browser.find_element("name", "email")
    passwordInput = browser.find_element("name", "password")

    emailInput.send_keys(prompt_email)
    passwordInput.send_keys(prompt_password)
    # Sign In
    signInButton = browser.find_element(By.XPATH,
                                        '//button[@type="submit"]/*[text()="Sign in"]')
    signInButton.click()

    time.sleep(5)


def scroll_down_browser(browser):
    print("scroll_down_browser")
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script(
            "return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


# submit to race
def submit_to_race(browser):
    try:
        print("submit_to_race")
        submitUrl = "https://us-east-1.console.aws.amazon.com/deepracer/home?region=us-east-1#competition/arn%3Aaws%3Adeepracer%3A%3A{aws_id}%3Aleaderboard%2F{race_id}/submitModel"
        submitUrl = submitUrl.format(aws_id=aws_id, race_id=race_id)

        browser.get(submitUrl)
        browser.refresh()
        time.sleep(4)

        scroll_down_browser(browser)

        print("chooseModelDropdown")
        # choose a model dropdown
        chooseModelDropdown = browser.find_element(By.XPATH,
                                                   '//button[@type="button"]/*[text()="Choose a model"]')
        # click once
        chooseModelDropdown.click()

        print("divSelect")
        # find div class contain awsui_description and text = modelname
        divSelect = browser.find_element(By.XPATH,
                                         '//*[contains(text(), "%s")]' % modelname)
        # click once as select
        divSelect.click()

        print("enterRaceButton")
        # enter race
        enterRaceButton = browser.find_element(By.XPATH,
                                               '//button[@type="submit"]/*[text()="Enter race"]')
        # enterRaceButton.click()

        # Sometimes, pressing the submit button will not trigger a submit
        # Therefore, just retry 5 times
        re_press_submit = 5
        submitted = False
        while re_press_submit > 0 and not submitted:
            try:
                print(f"enterRaceButton.click(), still have {re_press_submit} times to re-try.")
                enterRaceButton.click()
                time.sleep(2)
                if check_exists_by_xpath(browser, '//*[contains(text(), "%s")]' % "This submission is already queued to race"):
                    print(
                        f"{datetime.datetime.now()} FAILS to submitted model {modelname} to {race_id}")
                else:
                    print(
                        f"{datetime.datetime.now()} Submitted model {modelname} to {race_id} successfully.")
                    submitted = True
                re_press_submit -= 1
                time.sleep(2)
            except:
                # If click failed, means that submit was successful and we got re-routed to Event starting screen
                re_press_submit = 0
        time.sleep(5)
        # return submitted succes for this time
        return submitted
        
    except NoSuchElementException as ex:
        raise ex


# submit to race at multiple time
def submit_to_race_multiple(browser, repeat_hours=9):

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
            success = submit_to_race(browser)
            minuteToWaitNextTime = 10
            # if not success, only wait 2 minutes later to re-try again
            if not success:
                minuteToWaitNextTime = 2
            
            # Wait for n minutes before attempting submit again
            print(f"sleep {minuteToWaitNextTime} mins.")
            time.sleep(minuteToWaitNextTime*60)

        except NoSuchElementException as ex:
            # If failed to submit, wait for 2 minutes and try again
            count_fails += 1
            print(f"submit_to_race fails: {count_fails}, message {ex}")
            time.sleep(5)
            # If failed 5 times, try to log back in
            if count_fails >= 2:
                awsLogin(browser)
        else:
            # If there was no error, increase counter by 1
            count_submits += 1
            count_fails = 0

    # Print final submit count
    print(f"Submitted number of models to the race: {count_submits}")


def getEnvironmentVariable():
    # get environment variable
    with open("env.txt", 'r') as f:
        [env_hasPromptLogin, env_aws_id, env_username, env_password, env_prompt_email, env_prompt_password,
            env_race_id, env_modelname] = f.read().splitlines()

    global hasPromptLogin
    hasPromptLogin = env_hasPromptLogin == 'True'

    global aws_id
    aws_id = env_aws_id

    global username
    username = env_username

    global password
    password = env_password

    global prompt_email
    prompt_email = env_prompt_email

    global prompt_password
    prompt_password = env_prompt_password

    global race_id
    race_id = env_race_id

    global modelname
    modelname = env_modelname


def main():
    getEnvironmentVariable()
    # open browser
    browser = newBrowser()

    # login to aws
    # awsLogin(browser, aws_id, username, password)
    awsLogin(browser)

    # Submit the model to the summit race once
    # submit_to_race(browser, aws_id, race_id, modelname=modelname)

    # Submit the model to the summit race for multiple hours
    submit_to_race_multiple(browser, repeat_hours=12)

    # quit browser
    # browser.quit()


if __name__ == "__main__":
    main()
