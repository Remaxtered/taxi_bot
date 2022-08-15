from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import requests
import telebot
import json
import time
import os
from datetime import date
import traceback

class App():


	def __init__(self, user_login, user_password):
		self.set_driver_options()
		self.driver = webdriver.Chrome('chromedriver.exe', options=self.options)
		self.MAIN_TOKEN = 'SOME_API_TOKEN'
		self.RES_TOKEN = 'ANOTHER_API_TOKEN'
		self.main_bot = telebot.TeleBot(self.MAIN_TOKEN, threaded=False)
		self.res_bot = telebot.TeleBot(self.RES_TOKEN, threaded=False)
		try:
			self.main_bot.get_updates(allowed_updates=["channel_post"])
		except:
			self.MAIN_TOKEN = self.RES_TOKEN
			self.main_bot = self.res_bot
			self.main_bot.get_updates(allowed_updates=["channel_post"])
		self.CHAT_ID = '-SOME_CHAT_ID'
		self.ERRORS_CHAT_ID = "-ANOTHER_CHAT_ID"
		self.RELOGIN_INT = 1800
		self.USER_LOGIN = user_login
		self.USER_PASS = user_password
		self.today_date = date.today()


	def set_driver_options(self):
		self.options = webdriver.ChromeOptions()
		self.options.add_experimental_option("useAutomationExtension", False)
		self.options.add_experimental_option("excludeSwitches", ["enable-automation"])


	def login(self):
		for i in range(5):
			try:
				self.driver.get("https://scouts-n-agents.taxi.yandex.net/signin")
				time.sleep(i*2)
				if (self.driver.current_url == "https://scouts-n-agents.taxi.yandex.net/signin"):
					self.driver.find_element_by_css_selector("input[type=text]").send_keys(self.USER_LOGIN)
					self.driver.find_element_by_css_selector("input[type=password]").send_keys(self.USER_PASS)
					time.sleep(i*2)
					self.driver.find_element_by_css_selector("button[type=submit]").click()
			except:
				if i >= 3:
					time.sleep(i * 10)
				time.sleep(i)
			else:
				self.login_time = time.time()
				self.today_date= date.today()
				return
		print("Ошибка во время процесса авторизации на сайте!\nПроверьте подключение к интернету!")
		self.main_bot.send_message(self.ERRORS_CHAT_ID, 'Бот не смог авторизоваться на сайте!')
		self.update_cache()


	def update_cache(self):
	    self.request = requests.get(f'https://api.telegram.org/bot{self.MAIN_TOKEN}/getUpdates').json()
	    if (self.request['result'] != [] ):
	        self.offset = str(self.request['result'][-1]['update_id']+1)
	        requests.get(f'https://api.telegram.org/bot{self.MAIN_TOKEN}/getUpdates?offset={self.offset}')


	def watch(self):
		@self.main_bot.channel_post_handler()
		def get_user_data(x):
			self.current_time = time.time()
			if (self.current_time - self.login_time >= self.RELOGIN_INT):
				self.login()
			self.process_msg(x.text)
			time.sleep(10)


	def process_msg(self, msg):
		if (msg.startswith('{')):
			data = json.loads(msg)
			if ("validate" in data):
				self.validate_data = {"phone_number": data["validate"]["phone_number"],"license": data["validate"]["license"]}
				self.validate(self.validate_data)
				return
			if ("reg_data" in data):
				self.reg_data = {
					"job_type": data["reg_data"]["job_type"],
					"full_name": data["reg_data"]["full_name"],
					"birth_date": data["reg_data"]["birth_date"],
					"city": data["reg_data"]["city"],
					"phone": data["reg_data"]["phone"],
					"license": data["reg_data"]["license"],
					"country": data["reg_data"]["country"],
					"issue_date": data["reg_data"]["issue_date"],
					"expiration_date": data["reg_data"]["expiration_date"],
					"brand": data["reg_data"]["brand"],
					"model": data["reg_data"]["model"],
					"car_number": data["reg_data"]["car_number"],
					"vehicle_cert": data["reg_data"]["vehicle_cert"],
					"vin": data["reg_data"]["vin"],
					"color": data["reg_data"]["color"],
					"year": data["reg_data"]["year"],
				}
				self.registrate(self.reg_data)
			return


	def validate(self, data):
		self.driver.get("https://scouts-n-agents.taxi.yandex.net")
		if (data["phone_number"] != "" and data["license"] == ""):
			self.i = 0
			while True:
				self.i += 1
				try:
					self.driver.find_elements_by_css_selector("img.main-desktop__header-elements-icon")[1].click()
					time.sleep(self.i)
					self.driver.find_element_by_css_selector("input.ant-input").send_keys(data["phone_number"])
					self.driver.find_element_by_css_selector("div.sc-gzVnrw>button.ant-btn").click()
					time.sleep(self.i)
					self.status = self.driver.find_elements_by_css_selector("span.main-desktop__card-text")[1].get_attribute('innerText')
				except:
					if self.i == 5:
						self.phone = data["phone_number"]
						print(f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
						self.main_bot.send_message(self.CHAT_ID, '{"validate_status": { "status":"OK"} }')
						self.main_bot.send_message(self.ERRORS_CHAT_ID, f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
						return
				break
			if self.status == "Берем":
				self.main_bot.send_message(self.CHAT_ID, '{"validate_status": { "status":"OK"} }')
				return
			self.main_bot.send_message(self.CHAT_ID, '{"validate_status": { "status":"BAD"} }')
			return
		elif (data["phone_number"] != "" and data["license"] != ""):
			self.i = 0
			while True:
				self.i += 1
				try:
					self.driver.find_elements_by_css_selector("img.main-desktop__header-elements-icon")[2].click()
					time.sleep(self.i)
					self.driver.find_element_by_css_selector("input.ant-input").send_keys(data["license"])
					self.driver.find_element_by_css_selector("div.sc-gzVnrw>button.ant-btn").click()
					time.sleep(self.i)
					self.status = self.driver.find_elements_by_css_selector("span.main-desktop__card-text")[1].get_attribute('innerText')
				except:
					if self.i == 3:
						self.phone = data["phone_number"]
						self.license = data["license"]
						print(f"Ошибка во время проверки на лида пользователя с ВУ: {self.license}")
						self.main_bot.send_message(self.CHAT_ID, '{"validate_status": { "status":"OK"} }')
						self.main_bot.send_message(self.ERRORS_CHAT_ID, f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
						return
				else:
					break
			if self.status == "Берем":
				self.main_bot.send_message(self.CHAT_ID, '{"validate_status": { "status":"OK"} }')
				return
			self.main_bot.send_message(self.CHAT_ID, '{"validate_status": { "status":"BAD"} }')
			return
		self.main_bot.send_message(self.CHAT_ID, '{"validate_status": { "status":"OK"} }')
		self.main_bot.send_message(self.ERRORS_CHAT_ID, f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
		return


	def registrate(self, data):
		self.brand = data["brand"]
		self.model = data["model"]
		self.full_name = data["full_name"]
		self.driver.get("https://scouts-n-agents.taxi.yandex.net/drivers")
		time.sleep(1)
		self.driver.find_elements_by_css_selector("button.ant-btn-icon-only")[2].click()
		try:
			time.sleep(1)
			self.driver.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[0].send_keys(data["full_name"])
			self.select_val(0, data["birth_date"].split('.')[0])
			self.select_val(1, data["birth_date"].split('.')[1])
			self.select_val(2, data["birth_date"].split('.')[2])
			for i in range(3):
				try:
					self.select_val(3, data["city"])
				except:
					time.sleep(1)
				else:
					break
			self.driver.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[1].send_keys(data["phone"])
			self.select_val(4, data["job_type"])
			self.driver.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[2].send_keys(data["license"])
			self.select_val(5, data["country"])
			self.select_val(6, data["issue_date"].split('.')[0])
			self.select_val(7, data["issue_date"].split('.')[1])
			self.select_val(8, data["issue_date"].split('.')[2])
			self.select_val(9, data["expiration_date"].split('.')[0])
			self.select_val(10, data["expiration_date"].split('.')[1])
			self.select_val(11, data["expiration_date"].split('.')[2])
			self.select_val(12, self.brand)
			self.driver.execute_script(f"""document.querySelectorAll("div.sc-iwsKbI div[role=combobox]")[13].click()""")
			self.driver.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[3].send_keys(data["car_number"])
			self.driver.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[4].send_keys(data["vehicle_cert"])
			self.driver.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[5].send_keys(data["vin"])
			self.select_val(14,  data["color"])
			self.select_val(15,  data["year"])
			self.select_val(16,  self.t.strftime("%d/%m/%Y").split('/')[0])
			self.select_val(17,  self.t.strftime("%d/%m/%Y").split('/')[1])
			self.select_val(18,  self.t.strftime("%d/%m/%Y").split('/')[2])
			self.select_val(19,  "Интернет")
			time.sleep(1)
			for i in range(3):
				try:
					self.select_val(13, self.model)
				except:
					time.sleep(i)
				else:
					break
			self.driver.find_element_by_css_selector("div.sc-iwsKbI button.ant-btn").click()
		except:
			print(f"Ошибка во время регистрации {self.full_name}!")
			self.main_bot.send_message(self.ERRORS_CHAT_ID, f"Ошибка во время регистрации!\nДанные для регистрации {data}\n\nТекст ошибки:\n{traceback.format_exc()}")
			return


	def select_val(self, p, v):
		self.driver.execute_script(
			f"""
					document.querySelectorAll("div.sc-iwsKbI div[role=combobox]")[{p}].click();
					let selects = document.querySelectorAll("div.ant-select-dropdown ul[role=listbox]");
					let options = selects[{p}].querySelectorAll("li[role=option]")
					let index = Array.from(options).findIndex(item => item.innerText == "{v}");
					options[index].click();""")

load_dotenv()

LOGIN = str(os.getenv('LOGIN'))
PASS = str(os.getenv('PASS'))

while True:
	try:
		app = App(LOGIN, PASS)
		app.set_driver_options()
		app.login()
		app.update_cache()
		app.watch()
		app.main_bot.polling(none_stop=True)
	except Exception as e:
		os.system("cls")
		os.system("taskkill /IM chromedriver.exe /F")
		os.system("taskkill /IM chrome.exe /F")
		time.sleep(1)
		print("\n\nОшибка во время выплнения программы!!!\n\nТекст ошибки:\n")
		raise e
		print("\n\nПерезапуск... Нажмите Ctrl-C для отмены...\n\n")
		time.sleep(10)