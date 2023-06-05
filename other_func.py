import json

# считываем данные из файла
def load_chats_from_json():
    with open("chats.json", "r") as ch:
        chats = json.load(ch)
    return chats

# составляем список названий чатов, в которых состоит бот
def chat_titles(chats):
    send_chats = ''
    for k, each in enumerate(chats):
        send_chats += each['title']
        if k < len(chats) - 1:
            send_chats += ', '
    return send_chats