import config
import telebot
import json
from time import gmtime, strftime

bot = telebot.TeleBot(config.token)

teamList = {}
admins = [334793866]

with open('logs/teamList.txt') as data_file:    
    teamList = json.load(data_file)



@bot.message_handler(commands=['help'])
def help(message):
	bot.send_message(message.chat.id, "/start - познакомиться с ботом.")
	bot.send_message(message.chat.id, "/newTeam - создать команду для этого чата.")
	bot.send_message(message.chat.id, "/deleteThisTeam - удалить команду для этого чата.")
	bot.send_message(message.chat.id, "/deleteAllTeams - удалить все команды для этого бота (доступна только для админов).")
	bot.send_message(message.chat.id, "/showAllTeams - показать список всех зарегестрированных команд.")
	bot.send_message(message.chat.id, "/startGame - начать игру (доступна только для админов).")


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
		teamList[message.chat.id] = {'name' : message.text, 'step' : '0'}
		saveTeamList()
		bot.send_message(message.chat.id, "Ваша команда зарегестрирована.\nНазвание: {name}.\nID: {id}".format(name = message.text, id = message.chat.id))


@bot.message_handler(commands=['deleteThisTeam'])
def deleteThisTeam(message):
	teamList.pop(message.chat.id)
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
	for key in teamList.keys():
		bot.send_message(message.chat.id, "{name} id: {id}".format(name = teamList[key]['name'], id = key))


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

#### game logic ####

@bot.message_handler(commands=['startGame'])
def startGame(message):
	if message.chat.id in admins:
		for key in teamList.keys():
			sendMessage(bot, key, "\nВнимание!! Игра началась!")
			step1(key)
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

def step1(key):
	sendMessage(bot, key, "Сколько стоит 9 нагетсов в БургеКинге?. Формат ответа - /число.", "step1", step2)
	teamList[key]['step'] = '1'
	saveTeamList()

def step2(message):
	log(str(message.chat.id), "Team: step1:" + message.text)
	if message.text == "/69":
		teamList[str(message.chat.id)]['step'] = '2'
		saveTeamList()
		sendMessage(bot, message.chat.id, "Успех!", "step1")
		sendMessage(bot, message.chat.id, "В чем смысл жизни?. Формат ответа - /число.", "step2", step3)
	else:
		sendMessage(bot, message.chat.id, "Неверный ответ.", "step1", step2)

def step3(message):
	log(str(message.chat.id), "Team: step2:" + message.text)
	if message.text == "/42":
		teamList[str(message.chat.id)]['step'] = '0'
		saveTeamList()
		sendMessage(bot, message.chat.id, "Успех!", "step2")
		sendMessage(bot, message.chat.id, "Вы завершили игру, поздравляю!")
	else:
		sendMessage(bot, message.chat.id, "Неверный ответ.", "step3", step3)

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


if __name__ == '__main__':
     bot.polling(none_stop=True)