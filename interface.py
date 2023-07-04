# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType # инструменты VK
from vk_api.utils import get_random_id	            # для генерации рандомного индетификатора
from pprint import pprint

from config import comunity_token, acces_token, db_url_object
from core import VkTools
from data_store import DBTools

class BotInterface():
    # инициализация класса self
    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)	# здесь инициализация нашего API и дальше для работы с ней нужно обращаться к объекту interface, т.к. он уже авторизован на стороне VK. А точнее к атрибуту класса self.
        self.api = VkTools(acces_token)
        self.profile_param = None
        self.users =[]
        self.offset = 0
        self.db = DBTools()
    # отправка сообщения
    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,		# кому отправить сообщение
                                'message': message,			# текст сообщения
                                'attachment': attachment,	# вложение, тут все фото
                                'random_id': get_random_id()# уникальный id сообщения
                                }
                                )
    # проверка данных пользователя
    def check_top_user_par(self, user_id, params):
        # проверка обязательных параметров
        s_bdate = params.get('bdate')
        if s_bdate is None or s_bdate.find(".", 3) == -1:
            self.message_send(user_id, f'Не удалось определить Вашу дату рождения. Просьба указать ее в формате ДД.ММ.ГГГГ')
            key = 'bdate'
        elif params.get('sex') is None:
            self.message_send(user_id, f'Не удалось определить Ваш пол. Просьба указать цифрами 1 - если женский, 2 - если мужской')
            key = 'sex'
        elif params.get('home_town') is None:
            self.message_send(user_id, f'Не удалось определить Ваш родной город. Просьба указать в соответсвии с тем как будет искать в поиске')
            key = 'home_town'
        else:
            key = ''
        #do! 'city': info.get('city')['title'] if info.get('city') is not None else None
        return key
    # формирование строки для вложения
    def get_attachment(self, photos_user):
        attach = ''
        for num, photo in enumerate(photos_user):
            attach += f'photo{photo["owner_id"]}_{photo["id"]},'
            # показать до 3х фото пользователя
            if num == 2:
                break
        return attach
    # обработка событий / получение сообщения
    def event_handler(self):
        key = ''
        b_was_hello = False
        b_is_find_db = True
        longpoll = VkLongPoll(self.interface)	# все события пользователя регестрируется в этом массиве

        # слушаем и обрабатываем события
        for event in longpoll.listen():
            # сообщение мне
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    if not b_was_hello:
                        # здесь логика для получения данных пользователя(находится в core.py)
                        self.profile_param = self.api.get_profile_info(event.user_id)
                        # взведём флажок, чтобы заново не прочесть данные из профиля, если их не хватало и задавались уточнения
                        b_was_hello = True
                    self.message_send(event.user_id, f'здравствуй {self.profile_param["name"]}')
                    # Проверка обязательных параметров
                    key = self.check_top_user_par(event.user_id, self.profile_param)
                elif command == 'поиск':
                    self.message_send(event.user_id, 'Начинаем поиск')
                    # цикл пока не найдем user отсутсвтующий в БД
                    while b_is_find_db:
                        # если список users не существует/пустой наполняем его следующей порцией
                        if not self.users:
                            self.users = self.api.serch_users(self.profile_param, self.offset)
                            self.offset +=50    # сдвиг для следующего поиска
                        # возвращает последний элемент в списке и урезает список
                        user = self.users.pop()
                        # здесь логика для проверки бд(находится в data_store.py)
                        b_is_find_db = self.db.check_user(event.user_id, user['id'])
                    photos_user = self.api.get_photos(user['id'])
                    attachment = self.get_attachment(photos_user)
                    self.message_send(event.user_id,
                                      f'Встречайте {user["name"]}, ссылка на страницу https://vk.com/id{user["id"]}',
                                      attachment=attachment
                                      ) 
                    # здесь логика для добавления в бд
                    self.db.add_user(event.user_id, user['id'])
                    b_is_find_db = True # сбрасываем флажок
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                # Проверка ответа на запрос и повторная проверка обязательных параметров
                elif key != '':
                    self.profile_param[key] = command
                    key = self.check_top_user_par(event.user_id, self.profile_param)
                else:
                    self.message_send(event.user_id, 'команда не опознана')

if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
    #test pprint(self.profile_param)
            