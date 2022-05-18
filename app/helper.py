import json

def set_config():
    
    with open("config.json") as json_data:
        d = json.load(json_data)
    
    print("1- Localhost")
    print("2- Pythonanywhere")
    print("3- Heroku")
    
    opc = int(input("Choose of the options above: "))

    if opc == 1:
        return d["localhost"]
    elif opc == 2:
        return d["pythonanywhere"]
    elif opc == 3:
        return d["heroku"]
    else:
        return None
