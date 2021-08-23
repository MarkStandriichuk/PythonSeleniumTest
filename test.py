# coding=utf-8
import time as t
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random

LOGIN = raw_input("Please, enter your login: ")
PASSWORD = raw_input("Please, enter your password: ")

options = Options()
options.add_argument('--incognito')
options.add_argument('--start-fullscreen')
driver = webdriver.Chrome(options=options)

timeout = 60
wait = WebDriverWait(driver, timeout)

mailing_address = LOGIN + "@ukr.net"
number_of_messages = 15
generated_subjects = {}
generated_body = {}
messages_count_before = 0
messages_data = {}
repeats = 15
sent_messages_data = {}


def login():
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='login']"))).send_keys(LOGIN)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))).send_keys(PASSWORD)


def close_old_tab(current_handle):
    all_handles = driver.window_handles
    driver.close()
    for handle in all_handles:
        if handle != current_handle:
            driver.switch_to.window(handle)


def randomizer(count):
    symbols = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz' + '1234567890'
    return ''.join(random.sample(symbols, k=count))


def composing_massages():
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//button[@class='button primary compose']"))).send_keys(mailing_address)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='toFieldInput']"))).send_keys(mailing_address)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='subject']"))).send_keys(randomizer(10))
    driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[1])
    wait.until(EC.presence_of_element_located((By.ID, "tinymce"))).send_keys(randomizer(10))
    driver.switch_to.default_content()
    wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button primary send']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='button primary']"))).click()


def get_subject_and_body(messages):
    for i in messages:
        message_subject, body = i.text.strip().split(' ')
        messages_data[message_subject] = body
    return messages_data


def delete_messages():
    try:
        driver.find_element_by_css_selector('table.noselect').find_elements_by_css_selector('td.msglist__row-subject')
    except StaleElementReferenceException:
        return

    wait.until(EC.presence_of_element_located((By.ID, '0'))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='controls-link remove']"))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='controls-link remove']"))).click()


def count_numbers_and_letters(message_body):
    numbers_count = 0
    list_of_body = list(message_body)
    for i in list_of_body:
        if i.isdigit():
            numbers_count += 1
    letters_count = len(message_body) - numbers_count
    return numbers_count, letters_count


driver.implicitly_wait(5)
driver.get('https://www.ukr.net/')
current_handle = driver.current_window_handle
driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
login()
driver.find_element_by_xpath('//button[@class="form__submit"]').click()
t.sleep(1)
driver.find_element_by_xpath('//a[text()="Вхідні"]').click()
close_old_tab(current_handle)

delete_messages()

try:
    messages_count_before += len(
        driver.find_element_by_css_selector('table.noselect').find_elements_by_css_selector('td.msglist__row-subject')
    )
except StaleElementReferenceException:
    pass


for message in range(1, repeats + 1):
    composing_massages()
subject = {value: key for key, value in generated_subjects.items()}
for key, value in generated_subjects.items():
    sent_messages_data[key] = generated_body[value]
if len(sent_messages_data) != repeats:
    print("Count of sent messages [%s] not equal to count of messages [%s] need to  be sent" % (
        len(sent_messages_data), repeats))
    driver.quit()

driver.find_element_by_xpath("//button[text()='Повернутись у вхідні']").click()

messages = wait.until(EC.presence_of_element_located((By.XPATH, "//table[@class='noselect']"))). \
    wait.until(EC.presence_of_element_located((By.XPATH, "//td[@class='msglist__row-subject']")))
massages_count_after = messages_count_before + repeats
if massages_count_after != len(messages):
    print("Sum of sends mails [%s] and mails that were in the box [%s] not equal to count of mails [%s] in the "
          "inbox!" % (repeats, messages_count_before, len(messages)))
    driver.quit()
else:
    print("Sum of sends mails [%s] and mails that were in the box [%s] is equal to count of mails [%s] in the "
          "inbox!" % (repeats, messages_count_before, len(messages)))
messages_data = get_subject_and_body(messages)
if not sent_messages_data == messages_data:
    print('Not all of the sent mails are received')
    print(sent_messages_data, messages_data)
    driver.quit()

wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button primary compose']"))).click()
wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='toFieldInput']"))).send_keys(mailing_address)
wait.until(EC.presence_of_element_located((By.NAME, 'subject'))).send_keys("final message")

# composing final message
final_body = ''
for subj, messages_body in sent_messages_data.items():
    numbers, letters = count_numbers_and_letters(messages_body)
    final_body += "Received message on theme %s with message: %s. It contains %s " \
                  "letters and %s numbers \n" % (str(subj), str(messages_body), letters, numbers)
wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='mce_0_ifr']"))).send_keys.send_keys(final_body)
wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button primary send']"))).click()
wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='link3']"))).click()

wait.until(EC.presence_of_element_located((By.ID, '0'))).click()
delete_item = driver.find_elements_by_css_selector('.checkbox.noselect')
for item in range(1, len(delete_item)):
    delete_item[item].click()
wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button primary']"))).click()

driver.quit()
