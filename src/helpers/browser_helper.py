
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def wait_until_found(browser, sel, timeout, print_error=True, try_untill_found=False):
    try:
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, sel))
        WebDriverWait(browser, timeout).until(element_present)

        return browser.find_element_by_css_selector(sel)
    except exceptions.TimeoutException:
        if print_error:
            print(f"Timeout waiting for element: {sel}")
        if try_untill_found:
            print(f"Trying Again waiting for element: {sel}")
            return wait_until_found(browser, sel, timeout, print_error, try_untill_found)
        return None
