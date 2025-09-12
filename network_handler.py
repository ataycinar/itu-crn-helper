import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re

ua = UserAgent()
random_ua = ua.random

# getToken function #
# parameters: ITUGiris username/email , ITUGiris password #
# output: 'Authorization' header for provided user credentials #
# example output -> 'Bearer QwNWFiYWIiLCJ...' 

def getToken(username,password):

    # accessing OBS. #
    OBSfirstRequest = requests.get('https://obs.itu.edu.tr/login/auth/login?ReturnUrl=/ogrenci/') 

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
    
    # got a url to be redirected back to OBS again. #
    obsRedirectUrl=loginRequest.headers['Location']

    # accessing redirected url. #
    obsRedirectRequest = requests.get(obsRedirectUrl ,allow_redirects=False)

    # gathered a cookie called 'LoginCookie'. parsing that from 'Set-Cookie' header. #
    obsRedirectCookies = obsRedirectRequest.headers['Set-Cookie']

    match = re.search(r'LoginCookie=(.*?);', obsRedirectCookies) # searching with re for a pattern where a substring starts with 'LoginCookie=' and ends with ';'. #
    if match: # if its found #
        LoginCookie = match.group(1) # assing that substring to variable. #

    # selecting the identity with a request using the 'LoginCookie'. #
    identityRequest = requests.get('https://obs.itu.edu.tr/login/SelectIdentity?returnURL=/ogrenci/', cookies={'LoginCookie':LoginCookie},allow_redirects=False)

    # got redirected to a identity url with a certain subSessionId other then the initial one. #
    identityRedirectUrl = 'https://obs.itu.edu.tr' + identityRequest.headers['Location']

    # accessing to that redirect url #
    setIdentityRequest = requests.get(identityRedirectUrl, cookies={'LoginCookie':LoginCookie}, allow_redirects=False)

    # selected the identity and redirected back to OBS as a student. #
    ogrenciRedirect = 'https://obs.itu.edu.tr' + setIdentityRequest.headers['Location']
    ogrenciLoginRequest = requests.get(ogrenciRedirect,cookies={'LoginCookie':LoginCookie},allow_redirects=False)

    # gathered some cookies including 'OgrenciCookie' , which allows to get our JWT by itself. #
    ogrenciAllCookies = ogrenciLoginRequest.headers['Set-Cookie']

    # doing the same search procedure but for 'OgrenciCookie'. #
    match = re.search(r'OgrenciCookie=(.*?);', ogrenciAllCookies)

    if match:
        OgrenciCookie = match.group(1)
    
    # getting users JWT with 'OgrenciCookie'. we also put 'Bearer ' to the front because thats how its used in headers. #
    jwt = 'Bearer ' + requests.get('https://obs.itu.edu.tr/ogrenci/auth/jwt',cookies={'OgrenciCookie':OgrenciCookie}).text

    # ending of function #
    return jwt


# courseRequest function #
# sends the provided CRNs both for adding and removing to the API endpoint without any delay. so if it gets called it will be sent to server immediately depending on your connection and server load #
# parameters: 'Authorization' header as string, **CRNs you would like to add as a list of strings, **CRNs you would like to remove as a list of strings #
# important !!! : added and removed CRN lists are both optional but one must be provided to function correctly #
# output: response as string #
# example output : {"ecrnResultList":[],"scrnResultList":[{"crn":"1111","operationFinished":true.... #

def courseRequest(token,eCRN=[],sCRN=[]):

    apiEndpoint = 'https://obs.itu.edu.tr/api/ders-kayit/v21'

    # constructing the data for the api requests according to the provided eCRN and sCRN #
    crnData = {'ECRN':eCRN , 'SCRN':sCRN} 

    # defining the 'authorization' header as the provided bearer token and setting the user-agent #
    authHeader = {'Authorization' : token, 'User-Agent': random_ua}  

    # sending the request without any delay #
    response = requests.post(apiEndpoint,json=crnData,headers=authHeader)

    return response.text


# getLastRequests function #
# gets 

def getLastRequests(token):
    
    apiEndpoint = 'https://obs.itu.edu.tr/api/ogrenci/Sinif/DersKayitIstekleri'

    header = {'Authorization':token , 'User-Agent':random_ua}

    responsedata = requests.get(apiEndpoint,headers=header)

    response = responsedata.json()

    return response