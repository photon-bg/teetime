import datetime, time, json, os, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger

#####################################################
def get_element_info(element):
    """a wrapper for getting the details of an element"""
    attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', element)
    print(attrs)

#####################################################
def check_teetime_availability(teetime):
    ''' Takes in tee time object found on site by time
        Either clicks on the tee time and returns 1 or
        someone has the tee time and move on
    '''
    #get_element_info(teetime)
    try:
        if teetime.get_attribute("class")=='teetime_button standard_button ftInit':
            golfers = json.loads(teetime.get_attribute("data-ftjson"))
            if golfers['wasP1']=="" and golfers['wasP2']=="" and golfers['wasP3']=="" and golfers['wasP4']=="" and golfers['wasP5']=="":
                return 1
            else:
                #print('teetime is only partially available')
                return 0
        else:
            #print('teetime is totally booked')
            return 0
    except:
        return 0
    
#####################################################
def make_date_page_link():
    ''' This function takes in the key strings needed to get the link to the date
    we want to click on to make a tee time.
    It outputs the link to be clicked and then the timestamp so we can wait for the time to click.
    '''
    daysahead = 14
    start = 'https://www1.foretees.com/v5/bayclubboulderridge_golf_m56/Member_sheet?calDate='
    end = '&course=&select_jump'
    now = datetime.datetime.now()
    later = now + datetime.timedelta(days=daysahead)
    date = later.strftime("%m/%d/%Y")
    link = start+date+end
    timestamp = now.replace(hour=6, minute=30, second=00, microsecond=000000)
    return link, timestamp

#####################################################
def retry_loop(how_to_look, details, speed_to_retry):
    """main structure for trying to click on something as fast as possible
    """
    retry=0
    while retry<speed_to_retry:
        if how_to_look == 'class':
            try:
                button = driver.find_element(By.CLASS_NAME, details)
                return button
            except:
                time.sleep(5/speed_to_retry)
                retry = retry+1
                continue
        elif how_to_look == 'xpath':
            try:
                button = driver.find_element(By.XPATH, details)
                return button
            except:
                time.sleep(5/speed_to_retry)
                retry = retry+1
                continue
        else:
            try:
                button = driver.find_element(By.ID, details)
                return button
            except:
                time.sleep(5/speed_to_retry)
                retry = retry+1
                continue  
    return
    

#####################################################
if __name__ == '__main__':

    """Make sure you setup your cron job:
    
    in terminal, type $sudo crontab -u photon -e
    type password.

    put these two lines in the crontab

    SHELL=/bin/zsh
    29 6 * * 6,0 export DISPLAY=:0 && export PATH=$PATH:/usr/local/bin && cd /Users/photon/Coding/personal/teetime && sh run.sh >> teetime_cron_log.txt 2>&1
    """


    #setup logging
    logging.basicConfig(filename="teetime_log.txt",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Test messages
    #logger.debug("Harmless debug Message")
    #logger.info("Just an information")
    #logger.warning("Its a Warning")
    #logger.error("Did you try to divide by zero")
    #logger.critical("Internet is down")
    
    logger.info(datetime.datetime.now())
    USERNAME = os.environ.get('BAYCLUB_USERNAME')
    PASSWORD = os.environ.get('BAYCLUB_PASSWORD')
    if type(USERNAME)==None:
        logger.error('You forgot to setup your BAYCLUB_USERNAME and BAYCLUB_PASSWORD in ~/.zshrc')
        logger.error('https://apple.stackexchange.com/questions/356441/how-to-add-permanent-environment-variable-in-zsh')
        quit()
    
    try:
        #driver = webdriver.Safari()
        #trying Chrome
        
        
# Set the threshold for urllib3 to WARNING
        service = Service(executable_path="./chromedriver_mac64/chromedriver", )
        driver = webdriver.Chrome(service=service)
        #seleniumLogger.setLevel(logging.CRITICAL)
    except Exception as e:
        logger.error(e)
        logger.error('YOU HAVE TO SETUP YOUR SAFARI DRIVER!')
        logger.error('https://www.lambdatest.com/blog/selenium-safaridriver-macos/')
        quit()

    #Login Page
    driver.get("http://bayclubconnect.com")
    driver.maximize_window()

    looking_for = 'username'
    element = retry_loop('id', looking_for, 20) #how many times in 10 sec?

    element.send_keys(USERNAME)
    element = driver.find_element(By.ID,'password')
    element.send_keys(PASSWORD)
    element.send_keys(Keys.RETURN)

    #Bayclub Member homepage
    logger.info("inside the Bayclub Member Homepage")
    looking_for = '//*[contains(text(), "PLAN A VISIT")]'
    button = retry_loop('xpath',looking_for, 20) 
    button.click()


    #select which location
    logger.info('selecting location')

    # xpath for "Boulder Ridge"
    #looking_for ='/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-club/div/div[1]/div/div[2]/div/div[2]/div[4]/div/app-radio-select/div/div[1]/div/span[2]'
    #radio_button = retry_loop('xpath', looking_for, 200)
    #radio_button.click()
    time.sleep(2)
    # xpath for continue
    looking_for = '/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-club/div/div[2]/div/div'
    #looking_for = '/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-club/div/div[2]/div/div'
    button1 = retry_loop('xpath', looking_for, 20)
    try:
        button1.click()
    except:
        print('missed the button again......  trying one more time.')
        button1 = retry_loop('xpath', looking_for, 20)
    
    time.sleep(2)
    #looking_for = '//*[contains(text(), " CONTINUE ")]'
    looking_for = '/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-service/div/div/div/div[2]/div/div'
    button = retry_loop('xpath', looking_for, 20)
    button.click()


    #select golf or driving range
    """     logger.info('select golf or driving range')
    looking_for = 'm-auto'
    button = retry_loop('class', looking_for, 20)
    button.click() """

    #select continue or driving range

    time.sleep(5) # wait for the new page to load

    #Foretees main page
    logger.info("we're on the foretees main page")
    #driver.switch_to.window(driver.window_handles[1])    #this may only be necessary if safari
    driver.get("https://www1.foretees.com/v5/bayclubboulderridge_golf_m56/Member_select")

    #make teetime alternatives in case the first chosen time isn't available.
    teetimes=[]
    for num in [4,5]:
        teetimes.append('8:'+str(num)+'0 AM')
    for num in [0,1,2,3,4,5]:
        teetimes.append('9:'+str(num)+'0 AM')
    teetimes.append('2:00 PM')
    teetimes.append('2:10 PM')

    #find the correct date, check for the start time and go to the link
    link, timestamp = make_date_page_link()
    a=0
    y = datetime.datetime.now()
    while a==0:
        if y<timestamp:
            y = datetime.datetime.now()
        else:
            driver.get(link)
            a=1

    #time.sleep(2)

    #on the tee booking page

    #look first for the primary choice teetime
    looking_for = "//*[contains(text(), '8:30 AM')]"
    teetime = retry_loop('xpath', looking_for, 1200)
    result = check_teetime_availability(teetime)

    if result == 1:
        teetime.click()
    else:
        for spot in teetimes:
            teetime_spot = "//*[contains(text(), '"+spot+"')]"
            try:
                button = driver.find_element(By.XPATH, teetime_spot)
            except:
                continue
            #teetime = retry_loop('xpath', looking_for, 1200)
            result = check_teetime_availability(teetime)
            if result == 1:
                teetime.click()
                logger.info('Getting tee time '+spot)
                break


    #Teetime selected, now "Yes continue or OK or somethign like that."

    looking_for="//*[contains(text(), 'Yes, Continue')]"
    continue_button = retry_loop('xpath', looking_for, 20)
    try:
        continue_button.click()
        logger.info('continue_button exists')
    except Exception as e:
        logger.error(e)
        logger.error('Trying to click continue after tee time choice')

    try:
        oops = driver.find_element(By.XPATH, "//*[contains(text(), 'Sorry, but you are allowed to create up to 1 tee times for any given day.')]")
        oops.click()
        logger.info("We already have a teetime for this day.")
        driver.quit()
        quit()
    except:
        pass

    #Insert the Golfers

    golfers = ['Gamp_080, Brianna (N/A)', 'Gamp_082, Athena (N/A)','Gamp_083, Leo (N/A)']
    x=0
    for golfer in golfers:
        looking_for = "//*[contains(text(), '"+golfer+"')]"
        if x==0:
            player=retry_loop('xpath', looking_for, 20)
            x=1
            player.click()
        else:
            player = driver.find_element(By.XPATH, "//*[contains(text(), '"+golfer+"')]")
            player.click()

    #Select Golf Cart as mode of transportation for the other three players

    gc = driver.find_element(By.XPATH, '//*[@id="slot_player_row_1"]/div[4]/select/option[2]')
    gc.click()
    gc = driver.find_element(By.XPATH, '//*[@id="slot_player_row_2"]/div[4]/select/option[2]') 
    gc.click()
    gc = driver.find_element(By.XPATH, '//*[@id="slot_player_row_3"]/div[4]/select/option[2]') 
    gc.click()

    #Select Confirm.
    confirm = driver.find_element(By.XPATH, '//*[@id="main"]/div[6]/div/div[2]/div/div[3]/a[2]') 
    try:
        confirm.click()
    except Exception as e:
        logger.error(e)
        logger.error('trying to click continue to leave the tee time process')
    #delay just in case there's something I can't think of.
    time.sleep(2)
    logger.info("We're at the end of the script....... the last page says:")
    logger.info(driver.find_element(By.XPATH, "/html/body").text)
    driver.quit()


