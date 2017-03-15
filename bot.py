import config
import telebot
import json

bot = telebot.TeleBot(config.token)

teamList = {}
admins = []

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
		j = json.dumps(teamList)
		f = open('logs/teamList.txt', 'w')
		f.write(j)
		f.close()
		bot.send_message(message.chat.id, "Ваша команда зарегестрирована.\nНазвание: {name}.\nID: {id}".format(name = message.text, id = message.chat.id))


@bot.message_handler(commands=['deleteThisTeam'])
def deleteThisTeam(message):
	teamList.pop(message.chat.id)
	j = json.dumps(teamList)
	f = open('logs/teamList.txt', 'w')
	f.write(j)
	f.close()
	bot.send_message(message.chat.id, "Команда для этого чата удалена.")


@bot.message_handler(commands=['deleteAllTeams'])
def deleteAllTeams(message):
	if message.chat.id in admins:
		teamList.clear()
		j = json.dumps(teamList)
		f = open('logs/teamList.txt', 'w')
		f.write(j)
		f.close()
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
			bot.send_message(key, "Внимание!! Игра началась!")
			step1(key)
	else:
		bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

def step1(key):
	sent = bot.send_message(key, "Сколько стоит 9 нагетсов в БургеКинге?. Формат ответа - /число.")
	teamList[key]['step'] = '1'
	j = json.dumps(teamList)
	f = open('logs/teamList.txt', 'w')
	f.write(j)
	f.close()
	bot.register_next_step_handler(sent, step2)

def step2(message):
	if message.text == "/69":
		teamList[str(message.chat.id)]['step'] = '2'
		j = json.dumps(teamList)
		f = open('logs/teamList.txt', 'w')
		f.write(j)
		f.close()
		bot.send_message(message.chat.id, "Успех!")
		sent = bot.send_message(message.chat.id, "В чем смысл жизни?. Формат ответа - /число.")
		bot.register_next_step_handler(sent, step3)
	else:
		sent = bot.send_message(message.chat.id, "Неверный ответ.")
		bot.register_next_step_handler(sent, step2)

def step3(message):
	if message.text == "/42":
		teamList[str(message.chat.id)]['step'] = '0'
		j = json.dumps(teamList)
		f = open('logs/teamList.txt', 'w')
		f.write(j)
		f.close()
		bot.send_message(message.chat.id, "Успех!")
		bot.send_message(message.chat.id, "Вы завершили игру, поздравляю!")
#		sent = bot.send_message(key, "В чем смысл жизни?. Формат ответа - /число.")
#		bot.register_next_step_handler(sent, step3)
	else:
		sent = bot.send_message(message.chat.id, "Неверный ответ.")
		bot.register_next_step_handler(sent, step3)


if __name__ == '__main__':
     bot.polling(none_stop=True)