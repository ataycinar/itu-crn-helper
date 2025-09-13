import network_handler as net
import os
import logger
import time as t
import pwinput
import sys

tokenPath = ''

def saveToken(token):
    personalInfo = net.getPersonalInfo(token)
    if personalInfo == None: # if token is not valid #
        return False
    tcNo = personalInfo['kimlikNo'] # assuming getPersonalInfo(token) returned valid info #
    filename = f'{tcNo}.token' 
    path = f'tokens/{filename}'
    os.makedirs("tokens", exist_ok=True)
    with open(path , 'w') as file:
        file.write(token)
    logger.info(f'Token başarıyla kaydedildi. {path}')
    # token file could be saved with encryption #
    return path

def readToken(path):
    with open(path , 'r') as file:
        return file.read()
    
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
        token = input()
        if token == '':
            print('Lütfen bir token girin')
            t.sleep(2)
        elif not token.startswith('Bearer '):
            print("Tokenin başında 'Bearer' olduğundan emin olun")
        else:
            path = saveToken(token)
            if  path != False:
                return path
            else:
                print("Token ile giriş yapılamadı. Lütfen kontrol edin")

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
            invalidCRN.append(CRNinput)
        else:
            validCRN.append(CRNinput)

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

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

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
            tokenPath = saveToken(token)
            if token == None:
                t.sleep(3)
                continue
            elif tokenPath != False:
                break
        case '2':
            tokenPath = getTokenManual()
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

if not net.checkRegistrationTime(readToken(tokenPath))['ogrenciSinifaKayitOlabilir']:
    print('Kayıt zamanı henüz başlamadı bekleniyor...\n')
    while True:
            current_time = t.strftime("%H:%M:%S")
            # Print clock, '\r' returns cursor to start of the line
            sys.stdout.write("\rSaat:" + current_time)
            sys.stdout.flush()
            t.sleep(1)
print('test')

