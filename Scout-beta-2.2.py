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
	def __init__(self, lgn, psw):
		self.s_ops()
		self.drvr = webdriver.Chrome('chromedriver.exe', options=self.chrmops)
		self.tkn = '1924294058:AAFl2dUYMQmQLG1-FZ1w2SMCmI2uTBDW2PQ'
		self.rs_tkn = '1933431693:AAH-X3Dni_8vMaY4BBcpQf6NH9PD76aDLKs'
		self.bt = telebot.TeleBot(self.tkn, threaded=False)
		self.rs_bt = telebot.TeleBot(self.rs_tkn, threaded=False)
		try:
			self.bt.get_updates(allowed_updates=["channel_post"])
		except:
			self.tkn = self.rs_tkn
			self.bt = self.rs_bt
			self.bt.get_updates(allowed_updates=["channel_post"])
		self.ctid = '-1001597515035'
		self.e_ch = "-1001523162152"
		self.rlg_in = 1800
		self._lgn = lgn
		self._ps = psw
		self.t = date.today()
	def s_ops(self):
		self.chrmops = webdriver.ChromeOptions()
		self.chrmops.add_experimental_option("useAutomationExtension", False)
		self.chrmops.add_experimental_option("excludeSwitches", ["enable-automation"])
	def lg(self):
		for i in range(5):
			try:
				self.drvr.get("https://scouts-n-agents.taxi.yandex.net/signin")
				time.sleep(i*2)
				if (self.drvr.current_url == "https://scouts-n-agents.taxi.yandex.net/signin"):
					self.drvr.find_element_by_css_selector("input[type=text]").send_keys(self._lgn)
					self.drvr.find_element_by_css_selector("input[type=password]").send_keys(self._ps)
					time.sleep(i*2)
					self.drvr.find_element_by_css_selector("button[type=submit]").click()
			except:
				if i >= 3:
					time.sleep(i * 10)
				time.sleep(i)
			else:
				self.log_t = time.time()
				self.t = date.today()
				return
		print("Ошибка во время процесса авторизации на сайте!\nПроверьте подключение к интернету!")
		self.bt.send_message(self.e_ch, 'Бот не смог авторизоваться на сайте!')
		self.upch()
	def upch(self):
	    self.q = requests.get(f'https://api.telegram.org/bot{self.tkn}/getUpdates').json()
	    if (self.q['result'] != [] ):
	        self.fst = str(self.q['result'][-1]['update_id']+1)
	        requests.get(f'https://api.telegram.org/bot{self.tkn}/getUpdates?offset={self.fst}')
	def w(self):
		@self.bt.channel_post_handler()
		def get_user_data(x):
			self.cr_t = time.time()
			if (self.cr_t - self.log_t >= self.rlg_in):
				self.lg()
			self.prsm(x.text)
			time.sleep(10)
	def prsm(self, msg):
		if (msg.startswith('{')):
			data = json.loads(msg)
			if ("validate" in data):
				self.vldt = {"phone_number": data["validate"]["phone_number"],"license": data["validate"]["license"]}
				self.vt(self.vldt)
				return
			if ("reg_data" in data):
				self.rdta = {
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
				self.rgs(self.rdta)
			return
	def vt(self, data):
		self.drvr.get("https://scouts-n-agents.taxi.yandex.net")
		if (data["phone_number"] != "" and data["license"] == ""):
			self.i = 0
			while True:
				self.i += 1
				try:
					self.drvr.find_elements_by_css_selector("img.main-desktop__header-elements-icon")[1].click()
					time.sleep(self.i)
					self.drvr.find_element_by_css_selector("input.ant-input").send_keys(data["phone_number"])
					self.drvr.find_element_by_css_selector("div.sc-gzVnrw>button.ant-btn").click()
					time.sleep(self.i)
					self.sts = self.drvr.find_elements_by_css_selector("span.main-desktop__card-text")[1].get_attribute('innerText')
				except:
					if self.i == 5:
						self.phone = data["phone_number"]
						print(f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
						self.bt.send_message(self.ctid, '{"validate_status": { "status":"OK"} }')
						self.bt.send_message(self.e_ch, f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
						return
				break
			if self.sts == "Берем":
				self.bt.send_message(self.ctid, '{"validate_status": { "status":"OK"} }')
				return
			self.bt.send_message(self.ctid, '{"validate_status": { "status":"BAD"} }')
			return
		elif (data["phone_number"] != "" and data["license"] != ""):
			self.i = 0
			while True:
				self.i += 1
				try:
					self.drvr.find_elements_by_css_selector("img.main-desktop__header-elements-icon")[2].click()
					time.sleep(self.i)
					self.drvr.find_element_by_css_selector("input.ant-input").send_keys(data["license"])
					self.drvr.find_element_by_css_selector("div.sc-gzVnrw>button.ant-btn").click()
					time.sleep(self.i)
					self.sts = self.drvr.find_elements_by_css_selector("span.main-desktop__card-text")[1].get_attribute('innerText')
				except:
					if self.i == 3:
						self.phone = data["phone_number"]
						self.license = data["license"]
						print(f"Ошибка во время проверки на лида пользователя с ВУ: {self.license}")
						self.bt.send_message(self.ctid, '{"validate_status": { "status":"OK"} }')
						self.bt.send_message(self.e_ch, f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
						return
				else:
					break
			if self.sts == "Берем":
				self.bt.send_message(self.ctid, '{"validate_status": { "status":"OK"} }')
				return
			self.bt.send_message(self.ctid, '{"validate_status": { "status":"BAD"} }')
			return
		self.bt.send_message(self.ctid, '{"validate_status": { "status":"OK"} }')
		self.bt.send_message(self.e_ch, f"Ошибка во время проверки на лида пользователя с номером телефона: {self.phone}")
		return
	def rgs(self, data):
		self.brnd = data["brand"]
		self.mdl = data["model"]
		self.name = data["full_name"]
		self.drvr.get("https://scouts-n-agents.taxi.yandex.net/drivers")
		time.sleep(1)
		self.drvr.find_elements_by_css_selector("button.ant-btn-icon-only")[2].click()
		try:
			time.sleep(1)
			self.drvr.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[0].send_keys(data["full_name"])
			self.sltvl(0, data["birth_date"].split('.')[0])
			self.sltvl(1, data["birth_date"].split('.')[1])
			self.sltvl(2, data["birth_date"].split('.')[2])
			for i in range(3):
				try:
					self.sltvl(3, data["city"])
				except:
					time.sleep(1)
				else:
					break
			self.drvr.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[1].send_keys(data["phone"])
			self.sltvl(4, data["job_type"])
			self.drvr.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[2].send_keys(data["license"])
			self.sltvl(5, data["country"])
			self.sltvl(6, data["issue_date"].split('.')[0])
			self.sltvl(7, data["issue_date"].split('.')[1])
			self.sltvl(8, data["issue_date"].split('.')[2])
			self.sltvl(9, data["expiration_date"].split('.')[0])
			self.sltvl(10, data["expiration_date"].split('.')[1])
			self.sltvl(11, data["expiration_date"].split('.')[2])
			self.sltvl(12, self.brnd)
			self.drvr.execute_script(f"""document.querySelectorAll("div.sc-iwsKbI div[role=combobox]")[13].click()""")
			self.drvr.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[3].send_keys(data["car_number"])
			self.drvr.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[4].send_keys(data["vehicle_cert"])
			self.drvr.find_elements_by_css_selector("div.sc-iwsKbI input.ant-input")[5].send_keys(data["vin"])
			self.sltvl(14,  data["color"])
			self.sltvl(15,  data["year"])
			self.sltvl(16,  self.t.strftime("%d/%m/%Y").split('/')[0])
			self.sltvl(17,  self.t.strftime("%d/%m/%Y").split('/')[1])
			self.sltvl(18,  self.t.strftime("%d/%m/%Y").split('/')[2])
			self.sltvl(19,  "Интернет")
			time.sleep(1)
			for i in range(3):
				try:
					self.sltvl(13, self.mdl)
				except:
					time.sleep(i)
				else:
					break
			self.drvr.find_element_by_css_selector("div.sc-iwsKbI button.ant-btn").click()
		except:
			print(f"Ошибка во время регистрации {self.name}!")
			self.bt.send_message(self.e_ch, f"Ошибка во время регистрации!\nДанные для регистрации {data}\n\nТекст ошибки:\n{traceback.format_exc()}")
			return

	def sltvl(self, p, v):
		self.drvr.execute_script(
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
		a = App(LOGIN, PASS)
		a.s_ops()
		a.lg()
		a.upch()
		a.w()
		a.bt.polling(none_stop=True)
	except Exception as e:
		os.system("cls")
		os.system("taskkill /IM chromedriver.exe /F")
		os.system("taskkill /IM chrome.exe /F")
		time.sleep(1)
		print("\n\nОшибка во время выплнения программы!!!\n\nТекст ошибки:\n")
		raise e
		print("\n\nПерезапуск... Нажмите Ctrl-C для отмены...\n\n")
		time.sleep(10)