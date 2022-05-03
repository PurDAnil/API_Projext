import requests
import json

my_url = 'http://127.0.0.1:5000/data/users'
my_data = {
    'nick': 'Jute',
    'login': 'Jutonil',
    'age': 16,
    'password': 'capcha'
}


def main():
    print(json.dumps(requests.get(url=my_url).json(), indent=2),
          # requests.get(url=my_url + '/1').json(),
          requests.post(url=my_url, data=my_data).json(),
          # requests.delete(url=my_url + '/10').json(),
          sep='\n\n<------------->\n\n')


if __name__ == '__main__':
    main()
