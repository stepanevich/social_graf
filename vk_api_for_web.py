import vk_api
import settings


class VkApiForWeb:
    def __init__(self, login, password='', with_app=False):
        if with_app:
            self.session = vk_api.VkApi(
                app_id=settings.vk_app, client_secret=settings.vk_key,
                login=login, password=password, scope='users, friends',
                api_version='5.80'
            )
        else:
            self.session = vk_api.VkApi(
                login=login, scope='users, friends, groups'
            )

        try:
            self.session.auth(reauth=with_app)
            self.error = None
        except vk_api.AuthError:
            self.error = 'Введены неверные данные. Попробуйте еще раз'
        except:
            self.error = 'Произошла ошибка. Попробуйте еще раз'


def autocomplete_data(data):
    result = []
    for item in data['items']:
        if item['type'] == 'profile':
            label_list = []
            profile = item['profile']
            name = ' '.join([item['profile']['first_name'],
                            item['profile']['last_name']])
            label_list.extend([name])
            place = [profile[key]['title'] for key in ['city', 'country']
                     if profile.get(key, None)]
            label_list.extend(place)
            if item.get('description', None):
                label_list.extend([item['description']])
            label = ', '.join(label_list)
            value = profile['id']
            result.extend([{'label': label, 'value': value}])

    return result
