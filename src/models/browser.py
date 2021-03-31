import time
from datetime import date, datetime

from selenium.common import exceptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

from src.helpers.browser_helper import wait_until_found


class Channel:
    def __init__(self, name, c_id, browser, element):
        self.name = name
        self.c_id = c_id
        self.browser = browser
        self.element = element

    def __str__(self):
         return self.name 

    def open_channel(self):
        self.element.find_element_by_class_name("channel-anchor").click()
        time.sleep(1)
        wait_until_found(self.browser,"div.item-wrap.ts-message-list-item",5 ,try_untill_found=True)


class Team:
    def __init__(self, name, t_id, browser):
        self.browser = browser
        self.name = name
        self.t_id = t_id

    def __str__(self):
        channel_string = '\n\t'.join([str(channel) for channel in self.channels])
        return f"{self.name}\n\t{channel_string}"

    def get_elem(self):
        team_header = self.browser.find_element_by_css_selector(f"h3[id='{self.t_id}'")
        team_elem = team_header.find_element_by_xpath("..")
        return team_elem

    def expand_channels(self):
        try:
            self.get_elem().find_element_by_css_selector("div.channels")
        except exceptions.NoSuchElementException:
            try:
                self.get_elem().click()
                self.get_elem().find_element_by_css_selector("div.channels")
            except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException):
                return None

    def update_channels(self):
        self.expand_channels()
        channels = self.get_elem().find_elements_by_css_selector(".channels > ul > ng-include > li")

        channel_names = [channel.get_attribute("data-tid") for channel in channels]
        channel_names = [channel_name[channel_name.find("channel-") + 8:channel_name.find("-li")] for channel_name in channel_names if channel_name is not None]

        channels_ids = [channel.get_attribute("id").replace("channel-", "") for channel in channels]

        self.channels = [Channel(channel_names[i], channels_ids[i], self.browser, channels[i]) for i in range(len(channel_names))]

    def expand_downloads(self, until: date):
        self.update_channels()
        started_downloads = 0
        months = {
                'January': 1,
                'February': 2,
                'March': 3,
                'April': 4,
                'May': 5,
                'June': 6,
                'July': 7,
                'August': 8,
                'September': 9,
                'October': 10,
                'November': 11,
                'December': 12
            }
        for channel in self.channels:
            channel.open_channel()
            chats = self.browser.find_elements_by_css_selector('div.item-wrap.ts-message-list-item')
            chats.reverse()
            broke_chat = None
            broke_date = None

            previous_date = datetime.now().date()
            for chat in chats:
                date_obj = previous_date
                try:
                    date = chat.find_element_by_css_selector('div.message-list-divider.date-separator')
                    date_string = date.find_element_by_css_selector('div.message-list-divider-text.app-font-caption.app-font-base-bold').text.split(' ')
                    date_obj = datetime(int(date_string[2]),months[date_string[0]], int(date_string[1].replace(',',''))).date()
                except exceptions.NoSuchElementException:
                    pass
                except:
                    pass
                
                if not date_obj > until:
                    broke_chat = chat
                    broke_date = date_obj
                    break
                previous_date = date_obj
            
            next_date = datetime.now().date()
            if not broke_chat == None:
                index = chats.index(broke_chat)
                chats = chats[0:index]
                next_date = broke_date
            
            chats.reverse()

            for chat in chats:
                if next_date > until:
                    try:
                        subs = chat.find_elements_by_class_name('media message-body acc-thread-focusable expand-collapse')
                        for s in subs:
                            if not s.get_attribute('title') == 'Collapse all':
                                s.click()
                        time.sleep(1)
                        downloads = chat.find_elements_by_class_name('download-label')
                        for download in downloads:
                            download.click()
                            started_downloads += 1
                        
                    except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException):
                        pass
                
                date_obj = next_date
                try:
                    date = chat.find_element_by_css_selector('div.message-list-divider.date-separator')
                    date_string = date.find_element_by_css_selector('div.message-list-divider-text.app-font-caption.app-font-base-bold').text.split(' ')
                    date_obj = datetime(int(date_string[2]),months[int(date_string[0])], int(date_string[1].replace(',',''))).date()
                except exceptions.NoSuchElementException:
                    pass
                except:
                    pass

                next_date = date_obj

                
        return started_downloads

class Browser:
    def __init__(self, email, password, base_download_path):
        self.email = email
        self.password = password
        self.base_download_path = base_download_path
        self.checked_teams = {}
        self.main()

    def init_browser(self):
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--use-fake-ui-for-media-stream')
        chrome_options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile.default_content_setting_values.media_stream_mic': 1,
            'profile.default_content_setting_values.media_stream_camera': 1,
            'profile.default_content_setting_values.geolocation': 1,
            'profile.default_content_setting_values.notifications': 1,
            'profile': {
                'password_manager_enabled': False
            }
        })
        chrome_options.add_argument('--no-sandbox')

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # make the window headless
        #chrome_options.add_argument('--headless')
        #print("Enabled headless mode")

        chrome_options.add_argument("--mute-audio")

        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        # make the window a minimum width to show the meetings menu
        window_size = self.browser.get_window_size()
        if window_size['width'] < 1200:
            print("Resized window width")
            self.browser.set_window_size(1200, window_size['height'])

        if window_size['height'] < 850:
            print("Resized window height")
            self.browser.set_window_size(window_size['width'], 850)

    def login(self):
        login_email = wait_until_found(self.browser, "input[type='email']", 30, try_untill_found=True)
        login_email.send_keys(self.email)

        login_email = wait_until_found(self.browser, "input[type='email']", 5, try_untill_found=True)
        login_email.send_keys(Keys.ENTER)

        login_pwd = wait_until_found(self.browser, "input[type='password']", 10, try_untill_found=True)
        login_pwd.send_keys(self.password)

        login_pwd = wait_until_found(self.browser, "input[type='password']", 5, try_untill_found=True)
        login_pwd.send_keys(Keys.ENTER)

        keep_logged_in = wait_until_found(self.browser, "input[id='idBtn_Back']", 5)
        if keep_logged_in is not None:
            keep_logged_in.click()
            use_web_instead = wait_until_found(self.browser, ".use-app-lnk", 5, print_error=False)
            if use_web_instead is not None:
                use_web_instead.click()
        else:
            print("Login Unsuccessful")
            raise Exception("Unsuccessful Login")

    def prepare_page(self):
        try:
            self.browser.execute_script("document.getElementById('toast-container').remove()")
        except exceptions.JavascriptException:
            pass

        teams_button = wait_until_found(self.browser, "button.app-bar-link > ng-include > svg.icons-teams", 5)
        if teams_button is not None:
            teams_button.click()
    
    def get_all_teams(self):
        team_elems = self.browser.find_elements_by_css_selector("ul>li[role='treeitem']>div[sv-element]")

        team_names = [team_elem.get_attribute("data-tid") for team_elem in team_elems]
        team_names = [team_name[team_name.find('team-') + 5:team_name.rfind("-li")] for team_name in team_names]

        team_headers = [team_elem.find_element_by_css_selector("h3") for team_elem in team_elems]
        team_ids = [team_header.get_attribute("id") for team_header in team_headers]

        return [Team(team_names[i], team_ids[i], self.browser) for i in range(len(team_elems))]

    def main(self):
        self.init_browser()
        self.browser.get("https://teams.microsoft.com")

        self.login()

        print("Waiting for correct page...", end='')
        wait_until_found(self.browser, "#teams-app-bar", 60, try_untill_found=True)

        print('Webpage Found! Starting Processes')
        self.prepare_page()

    def check_for_downloads(self, team_name, date):
        if team_name in self.checked_teams.keys():
            return self.checked_teams
        
        teams = self.get_all_teams()
        selected_team = None
        for team in teams:
            if team.name == team_name:
                selected_team = team
                break
        
        if selected_team != None:
            self.checked_teams[team_name] = selected_team.expand_downloads(date)
            return self.checked_teams
        else:
            for team in teams:
                if not team.name in self.checked_teams.keys():
                    self.checked_teams[team.name] = team.expand_downloads(date)

            return self.checked_teams
