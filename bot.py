import config
import myToken
import telebot
import json
from time import gmtime, strftime
from threading import Timer
import time

bot = telebot.TeleBot(myToken.token)

teamList = {}
admins = [334793866]

with open('logs/teamList.txt') as data_file:    
    teamList = json.load(data_file)



@bot.message_handler(commands=['help'])
def help(message):
	string = "/start - познакомиться с ботом." + "\n" +\
	"/newTeam - создать команду для этого чата." + "\n" +\
	"/deleteThisTeam - удалить команду для этого чата." + "\n" +\
	"/showAllTeams - показать список всех зарегестрированных команд." + "\n" +\
	"/deleteAllTeams - удалить все команды для этого бота (доступна только для админов)." + "\n" +\
	"/startGame - начать игру (доступна только для админов)." + "\n" +\
	"/continueGame - возобновить игру, после перезапуска бота (доступна только для админов)." + "\n" +\
	"/sendToAllTeams - отправить сообщение всем командам (доступна только для админов)." + "\n" +\
	"/progressList - (доступна только для админов)."
	bot.send_message(message.chat.id, string)


@bot.message_handler(commands=['start'])
def startCommand(message):
	sent = bot.send_message(message.chat.id, "Привет, как тебя зовут?")
	bot.register_next_step_handler(sent, hello)

def hello(message):
	bot.send_message(message.chat.id, "Очень приятно, {name}. А меня зовут ЛалаБот:)".format(name = message.text))



@bot.message_handler(commands=['newTeam'])
def newTeam(message):
	sent = bot.send_message(message.chat.id, "Введите название команды")
	bot.register_next_step_handler(sent, setTeamName)

def setTeamName(message):
	teams = teamList.values()
	if message.text in teams:
		sent = bot.send_message(message.chat.id, "Команда c таким названием уже существует.\nВведите название команды")
		bot.register_next_step_handler(sent, setTeamName)
	elif message.chat.id in teamList:
		bot.send_message(message.chat.id, "Команда для этого чата уже существует.\nНазвание: {name}.\nID: {id}".format(name = teamList[message.chat.id], id = message.chat.id))
	else:
		teamList[str(message.chat.id)] = {'name' : message.text, 'step' : '0'}
		saveTeamList()
		bot.send_message(message.chat.id, "Ваша команда зарегестрирована.\nНазвание: {name}.\nID: {id}".format(name = message.text, id = message.chat.id))


@bot.message_handler(commands=['deleteThisTeam'])
def deleteThisTeam(message):
	if str(message.chat.id) in teamList:
		teamList.pop(str(message.chat.id))
		saveTeamList()
	bot.send_message(message.chat.id, "Команда для этого чата удалена.")


@bot.message_handler(commands=['deleteAllTeams'])
def deleteAllTeams(message):
	if message.chat.id in admins:
		teamList.clear()
		saveTeamList()
		bot.send_message(message.chat.id, "Все команды для этого бота удалены.")
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")


@bot.message_handler(commands=['showAllTeams'])
def showAllTeams(message):
	string = ""
	for key in teamList.keys():
		string = string + "{name} id: {id}\n".format(name = teamList[key]['name'], id = key)
	bot.send_message(message.chat.id, string)


@bot.message_handler(commands=['newAdmin'])
def newAdmin(message):
	sent = bot.send_message(message.chat.id, "Введите пароль")
	bot.register_next_step_handler(sent, checkPassword)

def checkPassword(message):
	if config.adminPassword == message.text:
		admins.append(message.chat.id)
		bot.send_message(message.chat.id, "Теперь в этом чате можно выполнять админские команды.")
	else:
		bot.send_message(message.chat.id, "Неверный пароль.")


@bot.message_handler(commands=['progressList'])
def progressList(message):
	if message.chat.id in admins:
		string = ""
		for key in teamList.keys():
			string = string + "name: {name}, step: {step}\n".format(name = teamList[key]['name'], step = teamList[key]['step'])
		bot.send_message(message.chat.id, string)
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")


@bot.message_handler(commands=['sendToAllTeams'])
def sendToAllTeams(message):
	if message.chat.id in admins:
		sent = bot.send_message(message.chat.id, "Введите сообщение, которое хотите отправить всем командам.")
		bot.register_next_step_handler(sent, sendToAll)
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

def sendToAll(message):
	for key in teamList.keys():
		bot.send_message(key, message.text)

#### game logic ####

@bot.message_handler(commands=['startGame'])
def startGame(message):
	if message.chat.id in admins:
		for key in teamList.keys():
			if teamList[key]['step'] == '0':
				sendMessage(bot, key, "\nВнимание!! Игра началась!")
				setStep(key, '1')
				sendMessage(bot, key, "Сколько стоит 9 нагетсов в БургеКинге?. Формат ответа - /число.", "step1", gameFlow)
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")


@bot.message_handler(commands=['continueGame'])
def continueGame(message):
	if message.chat.id in admins:
		for key in teamList.keys():
			if teamList[key]['step'] != '0':
				sendMessage(bot, key, "У нас были некоторые технические неполадки, но сейчас они устранены. Вы можете продолжить игру.", "", gameFlow)
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")


@bot.message_handler(commands=['resetGame'])
def resetGame(message):
	if message.chat.id in admins:
		for key in teamList.keys():
			setStep(key, '0')
			sendMessage(bot, key, "Игра остановлена админом. Вы не сможите продолжить игру.")
		bot.send_message(message.chat.id, "Игра остановленна.")
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

def gameFlow(message):
	currentStep = teamList[str(message.chat.id)]['step']
	log(str(message.chat.id), "Team: {step}:".format(step = currentStep) + message.text)

	if currentStep == '1':
		if message.text == "/69":
			setStep(message.chat.id, '2')
			sendMessage(bot, message.chat.id, "Успех!", "step1")
			sendMessage(bot, message.chat.id, "В чем смысл жизни?. Формат ответа - /число.", "step2", gameFlow)
			t = Timer(10, timeout, [message.chat.id, '2'])
			t.start()
		else:
			sendMessage(bot, message.chat.id, "Неверный ответ.", "step1", gameFlow)

	elif currentStep == '2':
		if message.text == "/42" or message.text == "/next":
			if message.text == "/42":
				setStep(message.chat.id, '3')
				sendMessage(bot, message.chat.id, "Успех!", "step2")
			elif message.text == "/next":
				step = teamList[str(message.chat.id)]['step']
				nextStep = int(step) + 1
				setStep(message.chat.id, str(nextStep))
			sendMessage(bot, message.chat.id, "\"Он вам не ...\". Формат ответа - /Слово", "step3", gameFlow)
		else:
			sendMessage(bot, message.chat.id, "Неверный ответ.", "step2", gameFlow)

	elif currentStep == '3':
		if message.text == "/Димон":
			sendMessage(bot, message.chat.id, "Успех!", "step3")
			setStep(message.chat.id, '0')
			sendMessage(bot, message.chat.id, "Вы завершили игру, поздравляю!")
		else:
			sendMessage(bot, message.chat.id, "Неверный ответ.", "step3", gameFlow)

def timeout(key, step):
	currentStep = teamList[str(key)]['step']
	if currentStep == step:
		sendMessage(bot, key, "Вы не успели выполнить задание. /next - что бы получить следующее задание.", "step{s}".format(s=currentStep))

#### helpers ####

def saveTeamList():
	j = json.dumps(teamList)
	f = open('logs/teamList.txt', 'w')
	f.write(j)
	f.close()

def log(key, message):
	string = "{time}: {str}\n".format(time = strftime("%Y-%m-%d %H:%M:%S", gmtime()), str = message)
	f = open("logs/{name}.txt".format(name = teamList[key]['name']), 'a')
	f.write(string)
	f.close()

def sendMessage(bot, key, message, mark = "", next = 0):
	sent = bot.send_message(key, message)
	log(str(key), "lala_bot: {mark}: ".format(mark = mark) + message)
	if next != 0:
		bot.register_next_step_handler(sent, next)
	return bot

def setStep(key, step):
	teamList[str(key)]['step'] = step
	saveTeamList()

if __name__ == '__main__':
     bot.polling(none_stop=True)