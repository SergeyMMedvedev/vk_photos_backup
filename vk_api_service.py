import requests
from utils import progress


class VK:

    _BASE_URL = 'https://api.vk.com/method'
    _USERS_GET = '/users.get'
    _PHOTOS_GET = '/photos.get'
    _BAR_NAME = 'VK API: '

    def __init__(self, access_token: str, user_id: str, version: str = '5.131') -> None:
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    @progress(_BAR_NAME, 'Загрузка фотографий из альбома Вконтакте')
    def get_photos(
        self,
        album_id: str = 'profile',
        extended: int = 1,
        photo_sizes: int = 1,
        count: int = 5
    ) -> dict:
        """
        Возвращает данные о фотографиях пользователя указанного альбома
        """
        url = self._BASE_URL + self._PHOTOS_GET
        params = {
            'owner_id': self.id,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': count
        }
        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        response_json = response.json()
        if response_json.get('error'):
            raise VKException(f'{response_json.get("error").get("error_msg")}')
        return response_json
    

class VKException(Exception):
    pass
