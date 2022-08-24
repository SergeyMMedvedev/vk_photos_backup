import requests
from datetime import datetime, date


class VKException(Exception):
    pass


class VK:

    _BASE_URL = 'https://api.vk.com/method'
    _USERS_GET = '/users.get'
    _PHOTOS_GET = '/photos.get'

    def __init__(self, access_token: str, user_id: str, version: str = '5.131') -> None:
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_users_info(self):
        url = self._BASE_URL + self._USERS_GET
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_photos(self, album_id='profile', extended=1, photo_sizes=1, count=5):
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

    def _download_image(self, url):
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def create_image_name(self, image, image_url):
        image_likes = image['likes']['count']
        image_name = str(image_likes)
        if image_likes in self.image_likes_set:
            image_upload_date = str(date.fromtimestamp(image['date']))
            image_name += image_upload_date
        self.image_likes_set.add(image_likes)
        image_extension = image_url[image_url.rfind('.'):]
        image_name += image_extension
        print('image_name', image_name)
        return image_name

    def get_images_names_and_urls(self):

        images_urls_list = []
        self.image_likes_set = set()

        photos_response = self.get_photos().get('response', {})
        print(photos_response)
        if not photos_response.get('count'):
            raise VKException('Photos not found')

        for item in photos_response.get('items', []):
            image_url = item['sizes'][-1]['url']
            image_name = self.create_image_name(item, image_url)
            # image_file = self._download_image(image_url)
            images_urls_list.append((image_name, image_url))

        return images_urls_list

    # print(vk.get_albums())
    # print(vk.get_friends())
    # print(vk.get_photos_all())

    # photo = requests.get('https://sun9-30.userapi.com/c9884/u4470114/-6/x_a4439d91.jpg').content

    # with open('image_name.jpg', 'wb') as handler:
    #     handler.write(photo)
