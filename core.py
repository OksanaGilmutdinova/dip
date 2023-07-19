# импортыacces_token
import vk_api
from vk_api.exceptions import ApiError
from datetime import datetime #библиотека для работы со временем
from config import acces_token
from pprint import pprint



class VkTools():
    def __init__(self, acces_token):
       self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):
        try:
            info, = self.api.method('users.get',            # users.get выводит список словарей, поэтому через запятую записываем в конретный словарь, второй пустой
                                {'user_id': user_id,		# о ком получит инфу
                                'fields': 'city,bdate,sex,relation,home_town' #поля в инфе
                                }
                                )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        user_info = {'name': (info['first_name'] + ' '+ info['last_name']) if 'first_name' in info and 'last_name' in info else None,
                     'id':  info['id'],
                     'bdate': info.get('bdate') if info.get('bdate') is not None else None,   #см. 1;13;16
                     'home_town': info.get('home_town'),
                     'sex': info.get('sex'),
                     'city_id': info.get('city')['id'] if info.get('city') is not None else None
                     }
        
        return user_info
    
    def serch_users(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        city_id = params['city_id']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 3
        age_to = age + 3
        count = 50

        try:
            users = self.api.method('users.search',
                                {'count': count,
                                'offset': offset*count,
                                'age_from': age_from,
                                'age_to': age_to,
                                'sex': sex,
                                'city': city_id,
                                'status': 6,
                                'is_closed': False
                                }
                            )
        except ApiError as e:
            info = []
            print(f'error = {e}')

        try:
            users = users['items']
        except KeyError:
            return []
        
        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        try:
            photos = photos['items']
        except KeyError:
            return []
        
        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                        )
        
        # сортировка по лайкам и комментам
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res[:3] # выводим первые 3 фото из этого альбома


#test   if __name__ == '__main__':
    #test    bot = VkTools(acces_token)
    #test    params = bot.get_profile_info(789657038)    print(params)
    #test    users = bot.serch_users(params)    print(params)
    #test print(bot.get_photos(users[2]['id']))