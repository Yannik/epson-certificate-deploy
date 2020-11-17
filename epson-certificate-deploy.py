#!/usr/bin/env python3

import os
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import sys
from time import sleep

def stepshot(driver, screenshots, suffix):
    if screenshots:
        driver.save_screenshot('selenium_' + str(suffix) + '.png')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("host", help="printer hostname")
parser.add_argument("password", help="printer admin password")
parser.add_argument("certfile", help="file which contains the certificate")
parser.add_argument("keyfile", help="file which contains the private key")
parser.add_argument("--headless", action="store_true", help="run headless")
parser.add_argument("--insecure", action="store_true", help="ignore invalid ssl cert on phone (useful for first setup)")
parser.add_argument("--no-screenshots", action="store_false", help="disable saving screenshots for each step")
parser.add_argument("--debug", action="store_true", help="debug output")
args = parser.parse_args()

screenshots = args.no_screenshots

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logging.getLogger().addHandler(ch)

options = Options()
if args.debug:
  options.log.level = "trace"
  logger.setLevel(logging.DEBUG)
if args.headless:
  options.add_argument("--headless")

profile = webdriver.FirefoxProfile()
profile.DEFAULT_PREFERENCES['frozen']['security.tls.version.enable-deprecated'] = True

capabilities = DesiredCapabilities.FIREFOX.copy()
if args.insecure:
  capabilities['acceptInsecureCerts'] = True
driver = webdriver.Firefox(capabilities=capabilities, firefox_profile=profile, options=options)
driver.set_window_size(1024, 768)

driver.get("https://" + args.host + "/PRESENTATION/ADVANCED/NWS_CERT_SSLTLS/TOP")
stepshot(driver, screenshots, 1)

if args.password:
  password_field = WebDriverWait(driver, 15).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="INPUTT_PASSWORD"]'))
  )
  password_field.send_keys(args.password)

  driver.find_element_by_xpath('//button[contains(@onclick, "OnSetButton")]').click()
  driver.get("https://" + args.host + "/PRESENTATION/ADVANCED/NWS_CERT_SSLTLS/TOP")

driver.find_element_by_xpath('//button[contains(@onclick, "CA_IMPORT")]').click()

print('Selecting file and submitting form')
cert_input = driver.find_element_by_css_selector('input[name="cert0"]')
cert_input.send_keys(os.path.abspath(args.certfile))

key_input = driver.find_element_by_css_selector('input[name="key"]')
key_input.send_keys(os.path.abspath(args.keyfile))

try:
  driver.find_element_by_xpath('//button[contains(@onclick, "OnImportButton")]').click()
except NoSuchElementException:
  driver.find_element_by_xpath('//button[contains(@onclick, "OnOverwriteImportButton")]').click()
  driver.switch_to.alert.accept()

result = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.warning'))
)

print("Result text: " + result.text)
# If no certificate was present previously
if "Einrichtung ist abgeschlossen." in result.text:
  driver.get("https://" + args.host + "/PRESENTATION/ADVANCED/NWS_CERT_SSLTLS/TOP")

  select = Select(driver.find_element_by_name('SEL_SSLTLSUSECERT'))
  select.select_by_value('CA-SIGNED_CERT')

  driver.find_element_by_xpath('//button[contains(@onclick, "input_form")]').click()
  driver.find_element_by_xpath('//button[contains(@onclick, "confirm_form")]').click()
  WebDriverWait(driver, 15).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'div.warning'))
  )

if not args.debug:
  driver.quit()

