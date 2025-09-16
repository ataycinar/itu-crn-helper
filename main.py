import network_handler as net
import os
import logger
import time as t
import pwinput
import sys
from datetime import datetime
import keyboard

token = ''
sinif = ''
regDateEpoch = ''
addCRN = []
dropCRN = []

#def saveToken(token):
#    personalInfo = net.getPersonalInfo(token)
#    if personalInfo == None: # if token is not valid #
#        return False
#    tcNo = personalInfo['kimlikNo'] # assuming getPersonalInfo(token) returned valid info #
#    filename = f'{tcNo}.token' 
#    path = f'tokens/{filename}'
#    os.makedirs("tokens", exist_ok=True)
#    with open(path , 'w') as file:
#        file.write(token)
#    logger.info(f'Token başarıyla kaydedildi. {path}')
#    # token file could be saved with encryption #
#    return path
#
#def readToken(path):
#    with open(path , 'r') as file:
#        return file.read()
    
def getCredentials():
    cls()
    print("\nDikkat! Bu uygulama açık kaynak kodludur. Yani Github reposu üzerinden kodu inceleyip bilgilerinizi girmenin güvenli olup olmadığını inceleyebilirsiniz.")
    print("https://github.com/ataycinar/itu-auto-crn\n")

    while True:
        t.sleep(1.5)
        print('Lütfen İTÜ mailinizi girin')
        email = input('İTÜ Mail:').strip()
        # Normalize Turkish-specific characters
        email = email.replace('İ', 'I').replace('ı', 'i').casefold()
        if email == '':
            print('İTÜ Maili girilmedi, lütfen tekrar deneyin.')
        elif not email.endswith('@itu.edu.tr'):
            print('İTÜ Maili hatalı girildi lütfen tekrar kontrol edin')
            t.sleep(1)
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
        global token
        token = input()
        if token == '':
            print('Lütfen bir token girin')
            t.sleep(2)
        elif not token.startswith('Bearer '):
            print("Tokenin başında 'Bearer' olduğundan emin olun")
        else:
            if net.checkToken(token):
                return token
            else:
                print("Token geçerli değil. Lütfen kontrol edin")

def getCRNinput():

    validCRN = []
    invalidCRN = []

    while True:
        CRNinput = input('\nCRN:')
        if CRNinput == '.':
            break
        try:
            CRNinput = int(CRNinput)
        except Exception as e:
            print('\nCRN rakamlardan oluşmalıdır. Lütfen tekrar deneyin.')
            continue
        if len(str(CRNinput))>5 or len(str(CRNinput))<4:
            invalidCRN.append(str(CRNinput))
        else:
            validCRN.append(str(CRNinput))

    if len(invalidCRN) != 0:
        print("Geçersiz CRN değerleri girildi. CRN'ler 4 veya 5 rakamdan oluşmalıdır. Bu geçersiz değerler yine de kullanılsın mı ?")
        t.sleep(1)
        print("Geçersiz olan CRN'ler : ", invalidCRN)
        t.sleep(2)
        while True:
            print("[E]vet, geçersiz CRN'ler kullanılsın.       [H]ayır, geçersiz CRN'leri sil.")
            t.sleep(2)
            ans = input().lower()
            if not ans in ['e','h']:
                print('Lütfen geçerli bir cevap girin. E veya H')
            match ans:
                case 'e':
                    validCRN += invalidCRN
                    break
                case 'h':
                    break
    return validCRN

def manualDate():
    print('Lütfen kayıt tarihinizi şu formatta girin : YYYY-AA-GG SS:DD:SS')
    while True:
        date = input('Tarih : ')
        try:
            datetime.strptime(date , "%Y-%m-%d %H:%M:%S")
            return(date)
        except:
            print('Tarih yanlış formatta girildi lütfen tekrar deneyin.')
            continue

def manualTrigger():
    print("Dersleri yollamak istediğinizde herhangi bir tuşa basabilirsiniz. ESC'ye basarak CRN'leri değiştirebilir, tarih girip otomatik olarak yollayabilirsiniz.")
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'esc':
                print("ESC'ye bastınız. CRN'leri değiştirmek veya tarih girmek için ana menüye dönebilirsiniz.")
                return False
            else:
                request = net.courseRequest(token, addCRN, dropCRN)
                print('İSTEK GÖNDERİLDİ')
                try:
                    print(request.json())
                except Exception:
                    print(request.text)
                print(addCRN, dropCRN)
                return True

def autoTrigger(regDate):
    print('kayıt saati bekleniyor...')
    regDate = datetime.strptime(regDate, "%Y-%m-%d %H:%M:%S")
    while True:
        serverTime = net.getServerTime()
        print('server saati : ' , serverTime)
        serverTime = datetime.strptime(serverTime, "%Y-%m-%d %H:%M:%S")
        if serverTime >= regDate:
            print('TIME HAS COME')
            request = net.courseRequest(token,addCRN,dropCRN)
            try:
                jsonResp = request.json()
                print(jsonResp)
            except:
                print('HATAAHATAAA : ', request.text)
                return False
            print(addCRN,dropCRN)
            return True
        t.sleep(0.5)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
def main():
    global addCRN
    global dropCRN
    global token
    cls()

    print("Merhaba, İTÜ OBS uygulamasına giriş yapmak için token'a ihtiyaç var.\n")
    t.sleep(2)

    while True:
        print("\n[1] İTÜ mail ve şifre ile token'ı otomatik olarak çek.")
        t.sleep(1)
        print("[2] Manuel olarak JWT gir. (ne yaptığımı biliyorum)")
        t.sleep(1)
        print('Lütfen bir seçimde bulunun.\n')
        t.sleep(1)
        match input():
            case '1':
                email,password = getCredentials()
                
                token = net.getToken(email,password)

                if token == None:
                    print('Kullanıcı adı veya şifre yanlış.')
                    continue
                else:
                    break
            case '2':
                token = getTokenManual()
                break
            case _:
                print('Lütfen bir seçim yapın. 1 veya 2')

    t.sleep(2)

    cls()

    print('Lütfen eklemek istediğiniz sınıfların CRNlerini teker teker yazıp entera basın. Nokta yazıp entera basarsanız CRN girişi tamamlanır. Eğer kayıt esnasında (add/drop) sınıf eklemek istemiyorsanız nokta yazıp entera basabilirsiniz.\n')

    addCRN = getCRNinput()

    t.sleep(2)

    print('Eklencek olan CRN girişleri tamamlandı. Bırakılacak olanlara geçiliyor...\n')

    t.sleep(2)

    cls()

    print('Lütfen bırakmak istediğiniz sınıfların CRNlerini teker teker yazıp entera basın. Nokta yazıp entera basarsanız CRN girişi tamamlanır. Eğer kayıt esnasında (add/drop) sınıf bırakmak istemiyorsanız nokta yazıp entera basabilirsiniz.\n')

    t.sleep(2)

    dropCRN = getCRNinput()

    t.sleep(2)

    print('\nCRN girişleri başarıyla tamamlandı\n')
    t.sleep(1)
    cls()
    print("\nEklenecek olan CRN'ler : " , addCRN)
    print("Bırakılacak olan CRN'ler : " , dropCRN)

    t.sleep(3)

    cls()
    try:
        sinif = net.checkRegistrationTime(token)['kayitZamanKontrolResult']['sinif']
    except:
        print('hata, sınıf bilgisi alınamadı')
    match sinif:
        case 1:
            regDate = '2025-09-16 17:26:30'
        case 2:
            regDate = '2025-09-19 10:00:00'
        case 3:
            regDate = '2025-09-18 14:00:00'
        case 4:
            regDate = '2025-09-18 10:00:00'
        case _:
            print('Kayıt tarihi belirlenemedi.')
            regDate = manualDate()
            if regDate:
                print('Tarih başarıyla kaydedildi : ', regDate)
    if sinif in [1,2,3,4]:
        print('Normal kayıt tarihiniz : ',regDate)
        print('[1] Kayıt tarihi doğru. / [2] Başka bir tarih girmek istiyorum / [3] Manuel olarak dersleri zamanında yollamak istiyorum ')
        ans = input('Seçim : ')
        match ans:
            case '1':
                autoTrigger(regDate)
            case '2':
                regDate = manualDate()
                autoTrigger(regDate)
            case '3':
                manualTrigger()


main()