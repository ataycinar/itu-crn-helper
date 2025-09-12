from datetime import datetime
import network_handler as net
import os
import logger
import time
import pwinput

def saveToken(token):
    personalInfo = net.getPersonalInfo(token)
    if personalInfo == None:
        return None
    tcNo = personalInfo['kimlikNo']
    filename = f'{tcNo}.token'
    path = f'tokens/{filename}'
    os.makedirs("tokens", exist_ok=True)
    with open(path , 'w') as file:
        file.write(token)
    logger.info(f'Token başarıyla kaydedildi. {path}')
    return None

def readToken(filename):
    with open(f'tokens/{filename}' , 'r') as file:
        return file.read()
    
def getCredentials():
    print("Dikkat! Bu uygulama açık kaynak kodludur. Yani Github reposu üzerinden kodu inceleyip bilgilerinizi girmenin güvenli olup olmadığını inceleyebilirsiniz.")
    print("https://github.com/ataycinar/itu-course-grabber")

    while True:
        time.sleep(1.5)
        print('Lütfen İTÜ mailinizi girin')
        email = input()
        if email == '':
            print('İTÜ Maili girilmedi, lütfen tekrar deneyin.')
        elif not email.endswith('@itu.edu.tr'):
            print('İTÜ Maili hatalı girildi lütfen tekrar kontrol edin')
            time.sleep(1)
            print('Örnek bir İTÜ Mail : arican25@itu.edu.tr\n')
        else:
            break

    while True:
        print('Lütfen şifrenizi girin.')
        password = pwinput.pwinput()
        if password == '':
            print('Parola girişi yapılmadı lütfen tekrar deneyin.')
        else:
            break
    return email , password

def getTokenManual():
    while True:
        print("Lütfen tokeni girin. Örnek bir token : Bearer mYXSUtXw7CgB2xnr... ")
        token = input()
        if token == '':
            print('Lütfen bir token girin')
            time.sleep(2)
        elif not token.startswith('Bearer '):
            print("Tokenin başında 'Bearer' olduğundan emin olun")
        else:
            saveToken(token)
            return None
    

print("Merhaba, İTÜ OBS uygulamasına giriş yapmak için scriptin token'a ihtiyacı var. Lütfen bir seçimde bulunun.\n")
time.sleep(2.5)
print("[1] İTÜ mail ve şifre ile token'ı otomatik olarak çek.")
print("[2] Manuel olarak JWT gir. (ne yaptığımı biliyorum)")

while True:
    match input():
        case '1':
            email,password = getCredentials()
            token = net.getToken(email,password)
            if token == None:
                break
            saveToken(token)
            break
        case '2':
            getTokenManual()
            break
        case _:
            print('Lütfen bir seçim yapın. 1 veya 2')