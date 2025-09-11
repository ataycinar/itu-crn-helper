import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re

ua = UserAgent()
random_ua = ua.random

def courseRequest(Ecrn,Scrn=[]):
    # a function that handles the courseRequests through the API endpoint. #
    return None

def getToken(username,password):

    # accessing OBS. #
    OBSfirstRequest = requests.get('https://obs.itu.edu.tr/login/auth/login?ReturnUrl=/ogrenci/') 

    # redirects us to a ITU Giris url. #
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

    # using the same random user-agent for request. #
    loginHeader= {'User-Agent' : random_ua} 

    # sending user name and password for login. # # !!! 'cookieCheck' is mandatory and used for acknowledging with ITU Giris system that we will be using cookies from now on !!! #
    loginRequest = requests.post(loginUrl, data=loginData, headers=loginHeader, cookies={'cookieCheck' : 'true'}, allow_redirects=False) 
    
    # we get a url to be redirected back to OBS again. #
    obsRedirectUrl=loginRequest.headers['Location']

    # accessing redirected url. #
    obsRedirectRequest = requests.get(obsRedirectUrl ,allow_redirects=False)

    # we gathered a cookie called 'LoginCookie'. now we'll be parsing that from 'Set-Cookie' header. #
    obsRedirectCookies = obsRedirectRequest.headers['Set-Cookie']

    match = re.search(r'LoginCookie=(.*?);', obsRedirectCookies) # with re library we are search a pattern where a substring starts with 'LoginCookie=' and ends with ';'. #
    if match: # if its found #
        LoginCookie = match.group(1) # assing that substring to variable. #

    # now we should select our identity with a request using our 'LoginCookie'. #
    identityRequest = requests.get('https://obs.itu.edu.tr/login/SelectIdentity?returnURL=/ogrenci/', cookies={'LoginCookie':LoginCookie},allow_redirects=False)

    # we got redirected to a identity url with a certain subSessionId other then the initial one. #
    identityRedirectUrl = 'https://obs.itu.edu.tr' + identityRequest.headers['Location']

    # accessing to that redirect url #
    setIdentityRequest = requests.get(identityRedirectUrl, cookies={'LoginCookie':LoginCookie}, allow_redirects=False)

    # now we selected our identity and redirected back to OBS as a student. #
    ogrenciRedirect = 'https://obs.itu.edu.tr' + setIdentityRequest.headers['Location']
    ogrenciLoginRequest = requests.get(ogrenciRedirect,cookies={'LoginCookie':LoginCookie},allow_redirects=False)

    # we again gathered some cookies including 'OgrenciCookie' , which allows us to get our JWT by itself. #
    ogrenciAllCookies = ogrenciLoginRequest.headers['Set-Cookie']

    # doing the same search procedure but for 'OgrenciCookie'. #
    match = re.search(r'OgrenciCookie=(.*?);', ogrenciAllCookies)

    if match:
        OgrenciCookie = match.group(1)
    
    # getting our JWT with 'OgrenciCookie'. we also put 'Bearer ' to the front because thats how we use it in headers. #
    jwt = 'Bearer ' + requests.get('https://obs.itu.edu.tr/ogrenci/auth/jwt',cookies={'OgrenciCookie':OgrenciCookie}).text

    # ending our function #
    return jwt