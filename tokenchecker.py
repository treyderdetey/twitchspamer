import requests


def validate_token(token):
    url = 'https://id.twitch.tv/oauth2/validate'
    headers = {'Authorization': f'OAuth {token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print('Токен действителен!')
        print('Информация о токене:', response.json())
    else:
        print('Токен недействителен. Код ошибки:', response.status_code)
        print('Ответ сервера:', response.text)


# Ваш Access Token
access_token = 'token'
validate_token(access_token)