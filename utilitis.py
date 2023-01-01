import requests


url = 'http://127.0.0.1:5000/api/all_students'

def get_students():

    result = requests.get(url)
    if result.status_code == 200:
        return result.json()
    else:
        print("Errorr!")

if __name__ == '__main__':
    print(get_students())