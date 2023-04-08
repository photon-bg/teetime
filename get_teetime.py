import datetime, json, os, logging, time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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
        options = Options()
        options.add_argument("window-size=2121x1228")
        options.add_argument("--allow-all-cookies")
        #options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # set headless mode
        driver = webdriver.Chrome(options=options, service=service)
        wait = WebDriverWait(driver, 10)
        short_wait = WebDriverWait(driver,10, poll_frequency=datetime.timedelta(milliseconds=50))
        #driver = webdriver.Chrome(service=service)
        #seleniumLogger.setLevel(logging.CRITICAL)
    except Exception as e:
        logger.error('Somethings is wrong with setting up the web service or wait functions')
        logger.error(e)
        quit()

    #Login Page
    driver.get("http://bayclubconnect.com")
    #driver.maximize_window()

    looking_for = 'username'
    element = wait.until(EC.presence_of_element_located((By.ID, "username")))
    #element = retry_loop('id', looking_for, 20) #how many times in 10 sec?

    element.send_keys(USERNAME)
    element = wait.until(EC.presence_of_element_located((By.ID, "password")))
    element.send_keys(PASSWORD)
    element.send_keys(Keys.RETURN)

    #Bayclub Member homepage
    logger.info("inside the Bayclub Member Homepage")
    looking_for = '//*[contains(text(), "PLAN A VISIT")]'
    try:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "PLAN A VISIT")]')))
    #button = retry_loop('xpath',looking_for, 20) 
        button.click()
    except Exception as e:
        logger.error('error clicking on Plan A Visit')
        logger.error(e)
        logger.error(driver.find_element(By.XPATH, "/html/body").text)
        logger.error(driver.find_element(By.XPATH, "/html").text)

    #select which location
    logger.info('selecting location')

    # xpath for "Boulder Ridge"
    #looking_for ='/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-club/div/div[1]/div/div[2]/div/div[2]/div[4]/div/app-radio-select/div/div[1]/div/span[2]'
    #radio_button = retry_loop('xpath', looking_for, 200)
    #radio_button.click()
    #time.sleep(2)
    # xpath for continue
    #looking_for = '/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-club/div/div[2]/div/div'
    #looking_for = '/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-club/div/div[2]/div/div'
    #already_selected = 0

    try:
        #radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Boulder Ridge Golf Club')]/ancestor::div[contains(@class, 'clickable')]/preceding-sibling::input[@type, 'radio']")))
        #radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Boulder Ridge Golf Club")]/ancestor::div[contains(@class, "clickable")]')))
        #radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Boulder Ridge Golf Club")]/ancestor::div[contains(@class, "clickable")]')))
        #radio_button = wait.until(EC.element_to_be_clickable(By.XPATH, '//span[contains(text(), "Boulder Ridge Golf Club")]/ancestor::div[contains(@class, "clickable")]'))
        #radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Boulder Ridge Golf Club")]')))
        radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Boulder Ridge Golf Club")]')))
        #already_selected = 0
        #for element in radio_button:
        #    logger.error("Text content:", element.text)
        #    logger.error("Class name:", element.get_attribute("class"))
        # 
        radio_button.click()
    except Exception as e:
            logger.error('error when clicking on the boulder ridge radio button')
            logger.error(e)
            logger.error(driver.find_element(By.XPATH, "/html/body").text)
            logger.error(driver.find_element(By.XPATH, "/html").text)
            quit()

        



    try:
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "CONTINUE")]')))
        continue_button.click()
    except Exception as e:
        logger.error('error when clicking on the Continue after clicking the boulder ridge radio button')
        logger.error(e)
        html=driver.page_source
        logger.error(driver.find_element(By.XPATH, "/html/body").text)
        logger.error(html)
    #time.sleep(2)
    #looking_for = '//*[contains(text(), " CONTINUE ")]'
    #looking_for = '/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-service/div/div/div/div[2]/div/div'
    try:
        #button = wait.until(EC.presence_of_element_located(By.XPATH, '/html/body/mol-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-service/div/div/div/div[2]/div/div'))
        button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-service/div/div/div/div[2]/div/div')))
        #/html/body/modal-container/div/div/app-schedule-visit-desktop/div/div/app-schedule-visit-service/div/div/div/div[2]/div/div
        #['@class, btn btn-outline-light-blue service-tile text-uppercase font-weight-bold align-middle text-center d-flex justify-content-center'
        button.click()
    except Exception as e:
        logger.error('error when clicking On Golf after selecting Boulder Ridge as the location')
        logger.error(e)
        logger.error(driver.find_element(By.XPATH, "/html/body").text)
        logger.error(driver.find_element(By.XPATH, "/html"))


    #select golf or driving range
    """     logger.info('select golf or driving range')
    looking_for = 'm-auto'
    button = retry_loop('class', looking_for, 20)
    button.click() """

    #select continue or driving range

    # wait for the new page to load
    #time.sleep(2)
    wait.until(EC.number_of_windows_to_be(2))
    # Switch to the new tab
    handles = driver.window_handles
    driver.switch_to.window(handles[1])
    #Foretees main page
    logger.info("we're on the foretees main page")
    #driver.switch_to.window(driver.window_handles[1])    #this may only be necessary if safari
    button = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    driver.get("https://www1.foretees.com/v5/bayclubboulderridge_golf_m56/Member_select")
    logger.info(driver.find_element(By.XPATH, "/html/body").text)


    #make teetime alternatives in case the first chosen time isn't available.
    teetimes=[]
    for num in [4,5]:
        teetimes.append('8:'+str(num)+'0 AM')
    for num in [0,1,2,3,4,5]:
        teetimes.append('9:'+str(num)+'0 AM')
    for num in [0,1,2,3,4,5]:
        teetimes.append('2:'+str(num)+'0 PM')

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
    try:
        teetime = short_wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '8:30 AM')]")))
        result = check_teetime_availability(teetime)
    except Exception as e:
        result = 0


        
    
    #teetime = retry_loop('xpath', looking_for, 1200)
    

    if result == 1:
        teetime.click()
    else:
        print('something went wrong w/ 8:30...')
        for spot in teetimes:
            teetime_spot = "//*[contains(text(), '"+spot+"')]"
            try:
                logger.info('looking for',teetime_spot)
                button = driver.find_element(By.XPATH, teetime_spot)
                result = check_teetime_availability(teetime)
            except Exception as e:
                result = 0
                print(e)
                continue
            #teetime = retry_loop('xpath', looking_for, 1200)
            
            if result == 1:
                teetime.click()
                logger.info('Getting tee time ',spot)
                break
            else:
                logger.error("can't find teetime ",spot)
                #logger.error(driver.find_element(By.XPATH, "/html/body").text)


    #Teetime selected, now "Yes continue or OK or somethign like that."

    looking_for="//*[contains(text(), 'Yes, Continue')]"
    try:
        continue_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Yes, Continue')]")))
        continue_button.click()
        logger.info('continue_button exists')
    except Exception as e:
        logger.error('error when clicking continue after tee time choice')
        logger.error(e)
        logger.error(driver.find_element(By.XPATH, "/html/body").text)
        try:
            oops = driver.find_element(By.XPATH, "//*[contains(text(), 'Sorry, but you are allowed to create up to 1 tee times for any given day.')]")
            oops.click()
            logger.info("We already have a teetime for this day.")
            driver.quit()
            quit()
        except:
            pass

    #Insert the Golfers
    #golfers_xpath = ['//*[@id="main"]/div[6]/div/div[1]/div[2]/div[2]/div[1]/div/div[2]/div[2]/span']
    golfers = ['Gamp_080, Brianna (N/A)', 'Gamp_082, Athena (N/A)','Gamp_083, Leo (N/A)']
    x=0
    for golfer in golfers:
        looking_for = "//*[contains(text(), '"+golfer+"')]"
        try:
            player = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '"+golfer+"')]")))
            player.click()
        except Exception as e:
            logger.error('error when looking for',golfer)
            logger.error(e)
            logger.error(driver.find_element(By.XPATH, "/html/body").text)
        


    #Select Golf Cart as mode of transportation for the other three players

    golf_cart_elements = ['//*[@id="slot_player_row_1"]/div[4]/select/option[2]', '//*[@id="slot_player_row_2"]/div[4]/select/option[2]', '//*[@id="slot_player_row_3"]/div[4]/select/option[2]']
    
    try:
        for gc_element in golf_cart_elements:
            gc = driver.find_element(By.XPATH, gc_element)
            gc.click()
    except Exception as e:
        logger.error('error when looking for',gc_element)
        logger.error(e)
        logger.error(driver.find_element(By.XPATH, "/html/body").text)

    #Select Confirm.
    confirm = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[6]/div/div[2]/div/div[3]/a[2]')))
    #confirm = driver.find_element(By.XPATH, '//*[@id="main"]/div[6]/div/div[2]/div/div[3]/a[2]') 
    try:
        confirm.click()
    except Exception as e:
        logger.error('trying to click continue to leave the tee time process')
        logger.error(e)
        logger.error(driver.find_element(By.XPATH, "/html/body").text)
        
    #delay just in case there's something I can't think of.
    #time.sleep(2)
    logger.info("We're at the end of the script....... the last page says:")
    logger.info(driver.find_element(By.XPATH, "/html/body").text)
    driver.quit()


