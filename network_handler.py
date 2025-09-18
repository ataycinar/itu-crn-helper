import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re
import logger
from datetime import datetime, timedelta

ua = UserAgent()
random_ua = ua.random

def log_response(response, request_name="Request"):
    """
    Comprehensive logging function for HTTP responses
    Logs status code, headers, and response body
    """
    logger.debug(f"=== {request_name} ===")
    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"URL: {response.url}")
    logger.debug(f"Headers: {dict(response.headers)}")
    
    # Log response body, handling different content types
    try:
        if response.headers.get('content-type', '').startswith('application/json'):
            logger.debug(f"Response Body (JSON): {response.json()}")
        elif response.headers.get('content-type', '').startswith('text/'):
            # Truncate HTML content if too long
            body = response.text
            if len(body) > 1000:
                logger.debug(f"Response Body (truncated): {body[:1000]}...")
            else:
                logger.debug(f"Response Body: {body}")
        else:
            logger.debug(f"Response Body Length: {len(response.content)} bytes")
    except Exception as e:
        logger.debug(f"Error reading response body: {e}")
    
    logger.debug(f"=== End {request_name} ===\n")


# getToken function #
# parameters: ITUGiris username/email , ITUGiris password #
# output: 'Authorization' header for provided user credentials #
# example output -> 'Bearer QwNWFiYWIiLCJ...' 

def getToken(username,password):

    # accessing OBS. #
    OBSfirstRequest = requests.get('https://obs.itu.edu.tr/login/auth/login?ReturnUrl=/ogrenci/')

    log_response(OBSfirstRequest, "OBS First Request")

    # redirect to a ITU Giris url. #
    loginUrl = OBSfirstRequest.url 

    # parsing VIEWSTATE and EVENTVALIDATION from html since its a must. #
    soup = BeautifulSoup(OBSfirstRequest.text, 'html.parser')
    
    # searching values and setting variables. #
    viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

    # creating data for login. (some random shit) #
    loginData = {
    '__VIEWSTATE': viewstate, 
    '__EVENTVALIDATION': eventvalidation,
    'ctl00$ContentPlaceHolder1$tbUserName': username,
    'ctl00$ContentPlaceHolder1$tbPassword': password,
    'ctl00$ContentPlaceHolder1$btnLogin': 'Giriş / Login',
    }

    # same random user-agent for request. #
    loginHeader= {'User-Agent' : random_ua} 

    # sending user name and password for login. # # !!! 'cookieCheck' is mandatory and used for acknowledging with ITU Giris system that cookies will be used from now on !!! #
    
    loginRequest = requests.post(loginUrl, data=loginData, headers=loginHeader, cookies={'cookieCheck' : 'true'}, allow_redirects=False) 
    
    log_response(loginRequest, "Login Request")

    if not 'Location' in loginRequest.headers:
        return None

    # got a url to be redirected back to OBS again. #
    obsRedirectUrl=loginRequest.headers['Location']

    # accessing redirected url. #
    obsRedirectRequest = requests.get(obsRedirectUrl ,allow_redirects=False)

    log_response(obsRedirectRequest, "OBS Redirect Request")

    # gathered a cookie called 'LoginCookie'. parsing that from 'Set-Cookie' header. #
    obsRedirectCookies = obsRedirectRequest.headers['Set-Cookie']

    match = re.search(r'LoginCookie=(.*?);', obsRedirectCookies) # searching with re for a pattern where a substring starts with 'LoginCookie=' and ends with ';'. #
    if match: # if its found #
        LoginCookie = match.group(1) # assing that substring to variable. #

    # selecting the identity with a request using the 'LoginCookie'. #
    identityRequest = requests.get('https://obs.itu.edu.tr/login/SelectIdentity?returnURL=/ogrenci/', cookies={'LoginCookie':LoginCookie},allow_redirects=False)

    log_response(identityRequest, "Identity Request")

    # got redirected to a identity url with a certain subSessionId other then the initial one. #
    identityRedirectUrl = 'https://obs.itu.edu.tr' + identityRequest.headers['Location']

    # accessing to that redirect url #
    setIdentityRequest = requests.get(identityRedirectUrl, cookies={'LoginCookie':LoginCookie}, allow_redirects=False)

    log_response(setIdentityRequest, "Set Identity Request")

    # selected the identity and redirected back to OBS as a student. #
    ogrenciRedirect = 'https://obs.itu.edu.tr' + setIdentityRequest.headers['Location']
    ogrenciLoginRequest = requests.get(ogrenciRedirect,cookies={'LoginCookie':LoginCookie},allow_redirects=False)

    log_response(ogrenciLoginRequest, "Ogrenci Login Request")

    # gathered some cookies including 'OgrenciCookie' , which allows to get our JWT by itself. #
    ogrenciAllCookies = ogrenciLoginRequest.headers['Set-Cookie']

    # doing the same search procedure but for 'OgrenciCookie'. #
    match = re.search(r'OgrenciCookie=(.*?);', ogrenciAllCookies)

    if match:
        OgrenciCookie = match.group(1)
    
    # getting users JWT with 'OgrenciCookie'. we also put 'Bearer ' to the front because thats how its used in headers. #
    jwt_response = requests.get('https://obs.itu.edu.tr/ogrenci/auth/jwt',cookies={'OgrenciCookie':OgrenciCookie})
    log_response(jwt_response, "JWT Request")
    jwt = 'Bearer ' + jwt_response.text

    # ending of function #
    return jwt


# courseRequest function #
# sends the provided CRNs both for adding and removing to the API endpoint without any delay. so if it gets called it will be sent to server immediately depending on your connection and server load #
# parameters: 'Authorization' header as string, **CRNs you would like to add as a list of strings, **CRNs you would like to remove as a list of strings #
# important !!! : added and removed CRN lists are both optional but one must be provided to function correctly #
# output: response object -to allow parsing of both response text and headers- #

def courseRequest(token,eCRN=[],sCRN=[]):

    apiEndpoint = 'https://obs.itu.edu.tr/api/ders-kayit/v21'

    # constructing the data for the api requests according to the provided eCRN and sCRN #
    crnData = {'ECRN':eCRN , 'SCRN':sCRN} 

    # defining the 'authorization' header as the provided bearer token and setting the user-agent #
    authHeader = {'Authorization' : token, 'User-Agent': random_ua}  

    # sending the request without any delay #
    response = requests.post(apiEndpoint,json=crnData,headers=authHeader)
    
    log_response(response, "Course Registration Request")

    return response


# getLastRequests function #
# gets last 50 requests for course registration requests #
# HAS A DELAY OF NEARLY 60 SECS #
# means that any request that will be made will appear after 60 seconds #
# parameters : 'Authorization' header as string #
# output: response as json #

def getLastRequests(token):
    
    apiEndpoint = 'https://obs.itu.edu.tr/api/ogrenci/Sinif/DersKayitIstekleri'

    header = {'Authorization':token , 'User-Agent':random_ua}

    responseData = requests.get(apiEndpoint,headers=header)
    
    log_response(responseData, "Get Last Requests")

    response = responseData.json()

    return response

def getPersonalInfo(token):

    apiEndpoint = 'https://obs.itu.edu.tr/api/ogrenci/KisiselBilgiler/'

    header = {'Authorization':token , 'User-Agent':random_ua}

    responseData = requests.get(apiEndpoint,headers=header)
    responseData.encoding = 'utf-8'
    
    log_response(responseData, "Get Personal Info")
    
    if responseData.status_code == 401:
        logger.error('HTTP 401 Error Token hatalı olabilir')
        return None
    return responseData

def checkRegistrationTime(token):

    apiEndpoint = 'https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu'

    header = {'Authorization':token , 'User-Agent':random_ua}

    responseData = requests.get(apiEndpoint,headers=header)

    responseData.encoding = 'utf-8'
    
    log_response(responseData, "Check Registration Time")

    return responseData.json()

def checkToken(token):
    apiEndpoint = 'https://obs.itu.edu.tr/api/ogrenci/OgrenciYetkiListesi'
    header = {'Authorization':token , 'User-Agent':random_ua}
    responseData = requests.get(apiEndpoint,headers=header)
    
    log_response(responseData, "Check Token")
    
    if responseData.status_code != 200:
        return False
    responseData.encoding = 'utf-8'
    jsonData = responseData.json()
    if 'ogrenci' in str(jsonData['kisiYetkiListesi']):
        return True
    else:
        return False
    

def getServerTime():
    url = 'https://obs.itu.edu.tr/'
    try:
        response = requests.get(url,allow_redirects=False)
        
        log_response(response, "Get Server Time")
        
        gmtDate = datetime.strptime(response.headers['Date'], "%a, %d %b %Y %H:%M:%S %Z")
        trDate = gmtDate + timedelta(hours=3)
        return trDate.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return response.text

def getCRNinfo(token,crnList):
    apiEndpoint = 'https://obs.itu.edu.tr/api/TaslakKontrolAPI/v1/'
    crnData = {'ecrn':crnList}
    header = {'Authorization':token , 'User-Agent':random_ua}
    response = requests.post(apiEndpoint,headers=header,json=crnData)
    
    log_response(response, "Get CRN Info")
    
    try:
        return response.json()['ecrnResultList']
    except:
        logger.error('OBS üzerinden bilgiler alınırken bir hata oldu.')
        logger.debug(response.text)
        return None
    

def isTaslakActive(token):
    apiEndpoint = 'https://obs.itu.edu.tr/api/ogrenci/DersKayitTaslak/KayitZamaniKontrolu'
    header = {'Authorization':token , 'User-Agent':random_ua}
    try:
        response = requests.get(apiEndpoint,headers=header)
        
        log_response(response, "Is Taslak Active")
        
        return response.json()['kayitZamanKontrolResult']['ogrenciTaslakOlusturabilir']
    except:
        logger.error('Bir hata oldu.')
        logger.debug('Taslak kayıt takvimi verisi alınamadı')
        return False