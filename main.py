import network_handler as net
import os
import logger
import time as t
import pwinput
from datetime import datetime
import keyboard
import hashlib

token = ''
addCRN = []
dropCRN = []
errors = {
    "VAL02": "Ders kaydı, 'Kayıt Zamanı Engeli' sebebiyle tamamlanamamıştır.",
    "VAL03": "Ders, bu dönem alındığı için tekrar alınamamıştır.",
    "VAL04": "Ders, ders planında bulunmadığı için alınamamıştır.",
    "VAL05": "Ders, dönemlik kredi kısıtlaması sebebiyle alınamamıştır.",
    "VAL06": "Ders, yeterli kontenjan olmadığı için alınamamıştır.",
    "VAL07": "Dersten, daha önce AA alındığı için bu ders tekrar alınamamıştır.",
    "VAL08": "Ders, dersi alabilen programlar arasında programınız olmadığı için alınamamıştır.",
    "VAL09": "Ders, ders çakışması sebebiyle alınamamıştır",
    "VAL10": "Derse bu dönem kayıtlı olmadığınız için işlem yapılamamıştır.",
    "VAL11": "Ders, dersin ön şartları sağlanmadığı için alınamamıştır.",
    "VAL12": "Ders, ilgili ders kayıt döneminde bulunmamaktadır.",
    "VAL13": "Ders, geçici olarak devre dışı bırakılmıştır.",
    "VAL14": "Sistem geçici olarak devre dışı bırakılmıştır.",
    "VAL15": "Maksimum 12 adet CRN gönderebilirsiniz.",
    "VAL16": "Şu an devam eden bir işleminiz bulunmaktadır, daha sonra tekrar deneyiniz.",
    "VAL18": "Ders, etiket kısıtları sağlanmadığı için alınamamıştır.",
    "VAL19": "Ders, lisans dersi olduğu için alınamamıştır.",
    "VAL20": "Her dönem sadece 1 dersi terk edebilirsiniz.",
    "VAL21": "İstek limitini aştınız. Lütfen 1 saat sonra tekrar deneyiniz.",
    "VAL22": "Şu anki ders kayıt zamanı içerisinde dersten, daha önce CC ve üstü harf notu alındığı için bu ders yükseltmeye alınamaz."
}

def getCredentials():

    cls()
    print("Dikkat! Bu uygulama açık kaynak kodludur. Yani Github reposu üzerinden kodu inceleyip bilgilerinizi girmenin güvenli olup olmadığını inceleyebilirsiniz.")
    print("https://github.com/ataycinar/itu-auto-crn\n")
    t.sleep(3)
    cls()

    while True:
        print('Lütfen İTÜ mailinizi girin')
        email = input('İTÜ Mail:').strip()
        email = email.replace('İ', 'I').replace('ı', 'i').casefold()
        if email == '':
            logger.debug('Kullanıcı boş İTÜ Mail girdi.')
            print('İTÜ Maili girilmedi, lütfen tekrar deneyin.')
        elif not email.endswith('@itu.edu.tr'):
            logger.debug(f'Kullanıcı sonu @itu.edu.tr ile bitmeyen İTÜ Mail girdi. Girilen mail : {email}')
            print('İTÜ Maili hatalı girildi lütfen tekrar kontrol edin')
            print('Örnek bir İTÜ Mail : arican25@itu.edu.tr\n')
            t.sleep(2)
        else:
            break

    while True:
        print('Lütfen şifrenizi girin.')
        password = pwinput.pwinput()
        if password == '':
            logger.debug('Kullanıcı boş şifre girdi.')
            print('Parola girişi yapılmadı lütfen tekrar deneyin.')
        else:
            break
    hashedPass = hashlib.sha256(password.encode()).hexdigest()
    logger.debug('Şifre hashlendi')
    logger.debug(f'Kullanıcı bilgileri alındı İTÜ Mail: {email} - Şifre SHA256:{hashedPass}')
    return email , password

def getTokenManual():
    logger.debug('Manuel olarak token alınıyor.')
    while True:
        print("Lütfen tokeni girin. Örnek bir token : Bearer mYXSUtXw7CgB2xnr... ")
        global token
        token = input()
        if token == '':
            logger.debug('Boş token girildi.')
            print('Lütfen bir token girin')
            t.sleep(2)
            cls()
        elif not token.startswith('Bearer '):
            logger.debug(f'Kullanıcının girdisinde "Bearer" yok. Girdi: {token}')
            print("Tokenin başında 'Bearer' olduğundan emin olun")
        else:
            t.sleep(10)
            if net.checkToken(token):
                logger.info('Token geçerli.')
                break
            else:
                logger.info('Token geçersiz.')
                t.sleep(2)
                cls()

def getCRNinput(addRemove):
    while True:
        crnListString = input("CRN'ler : ")
        crnList = crnListString.split()
        for crn in crnList:
            try:
                int(crn)
            except:
                logger.info(f"Geçersiz CRN : '{crn}'")
                crnList.remove(crn)
        for crn in crnList:
            if len(crn)<4 or len(crn)>5:
                logger.error(f'{crn} - Geçersiz CRN silindi. CRN 4 yada 5 rakamdan oluşmalıdır.')
                crnList.remove(crn)
        break
    if net.isTaslakActive(token) and addRemove == 'add':
        crnData = net.getCRNinfo(token,crnList)
        if crnData == None:
            logger.info("Girilen CRN'ler olduğu gibi kullanılacak.")
        else:
            for crn in crnData:
                if crn['statusCode'] == 0:
                    logger.info(f"Geçerli CRN : {crn['crn']} - {crn['dersKodu']} - {crn['dersAdi']}")
                else:
                    errorCode = crn['taslakKontrolResultList'][0]['resultCode']
                    errorData = crn['taslakKontrolResultList'][0]['resultData']
                    if errorCode in errors.keys():
                        logger.error(f"{crn['crn']} nolu CRN alınamaz. Sebep : {errors[errorCode]}")
                    else:
                        logger.error(f"Taslak verilerine göre bilinmeyen bir sebeple {errorCode} nolu CRN'yi alamazsınız.")
                    logger.debug(f"HATA KODU : {errorCode}")
                    logger.debug(f"HATA DETAYI : {errorData}")
                    while True:
                        print("Yine de bu CRN'yi kullanmak ister misiniz ? [E]vet / [Hayır]")
                        ans = input()
                        if ans in ['E', 'e']:
                            logger.info(f"Geçersiz CRN kullanılıyor. {crn}")
                            t.sleep(3)
                            break
                        elif ans in ['H', 'h']:
                            crnList.remove(crn['crn'])
                            logger.info(f'Geçersiz CRN silindi. {crn['crn']}')
                            t.sleep(2)
                            break
                        else:
                            print('Lütfen geçerli bir cevap girin.')
        return crnList
    else:
        logger.info('CRN girişi tamamlandı')
        return crnList
                        

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
    print("Dersleri yollamak istediğinizde herhangi bir tuşa basabilirsiniz. ESC'ye basarak CRN'leri değiştirebilir ya da tarih girip otomatik olarak yollayabilirsiniz.")
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'esc':
                print("Manuel kayıt iptal edildi. [1] CRN'leri değiştirebilir ya da [2] Otomatik kayıt kullanabilirsiniz.")
                ans = input()
                return ans
            else:
                request = net.courseRequest(token, addCRN, dropCRN)
                logger.info('Ders kayıt isteği yollanıyor...')
                try:
                    logger.debug(request.json())
                    return True
                except Exception:
                    logger.debug(request.text)
                    return False

def autoTrigger(regDate):
    print('Kayıt saati bekleniyor...')
    regDate = datetime.strptime(regDate, "%Y-%m-%d %H:%M:%S")
    while True:
        serverTime = net.getServerTime()
        print('ÖBS Saati   :' , serverTime)
        print('Kayıt Saati :' , regDate)
        serverTime = datetime.strptime(serverTime, "%Y-%m-%d %H:%M:%S")
        if serverTime >= regDate:
            print('Kayıt vakti geldi. Ders kayıt isteği yollanıyor...')
            request = net.courseRequest(token,addCRN,dropCRN)
            try:
                jsonResp = request.json()
                logger.debug(jsonResp)
                logger.info('Ders kayıt isteği başarı ile yollandı!')
            except:
                logger.debug(request.text)
                logger.error('Ders kayıt isteği yollanırken bir hata oluştu. Server ile alakalı bir durum olabilir. 3 Saniyede bir istek yollanmaya devam ediliyor...')
                return False
            print(addCRN,dropCRN)
            return True
        t.sleep(0.5)
        cls()

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():

    global addCRN
    global dropCRN
    global token
    cls()

    print("Merhaba, İTÜ ÖBS uygulamasına giriş yapmak için bir token'a ihtiyaç var.\n")
    t.sleep(3)

    while True:
        cls()
        print("[1] İTÜ mail ve şifre ile token'ı otomatik olarak çek.")
        print("[2] Manuel olarak JWT gir.")
        print('Lütfen bir seçimde bulunun.\n')
        match input():
            case '1':
                email,password = getCredentials()
                token = net.getToken(email,password)
                if token == None:
                    cls()
                    logger.error('Kullanıcı adı veya şifre yanlış.')
                    t.sleep(3)
                    continue
                else:
                    break
            case '2':
                token = getTokenManual()
                break
            case _:
                print('Lütfen bir seçim yapın. 1 veya 2.')

    t.sleep(2)

    cls()

    print("Eklemek istediğiniz CRN'leri aralarında birer boşluk bırakıp girin.\nEğer herhangi bir CRN eklemek istemiyorsanız boş bırakın.\n")

    addCRN = getCRNinput('add')

    t.sleep(2)

    print("Eklenecek olan CRN'ler tamamlandı. Bırakılacak olanlara geçiliyor...\n")

    t.sleep(2)

    cls()

    print("Bırakmak istediğiniz CRN'leri aralarında birer boşluk bırakıp girin.\nEğer herhangi bir CRN bırakmak istemiyorsanız boş bırakın.\n")

    t.sleep(2)

    dropCRN = getCRNinput('remove')

    t.sleep(2)

    print('\nCRN girişleri başarıyla tamamlandı\n')
    t.sleep(1)
    cls()
    logger.info(f"Eklenecek olan CRN'ler : {addCRN}")
    logger.info(f"Bırakılacak olan CRN'ler : {dropCRN}")

    t.sleep(3)

    cls()
    try:
        sinif = net.checkRegistrationTime(token)['kayitZamanKontrolResult']['sinif']
    except:
        print('hata, sınıf bilgisi alınamadı')
    match sinif:
        case 1:
            regDate = '2025-09-17 22:18:30'
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
        ans = input('')
        match ans:
            case '1':
                autoTrigger(regDate)
            case '2':
                regDate = manualDate()
                autoTrigger(regDate)


main()
