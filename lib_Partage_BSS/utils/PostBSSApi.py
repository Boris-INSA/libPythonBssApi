# -*-coding:Latin-1 -*

import requests

from lib_Partage_BSS.utils.ParseBSSResponse import parseResponse


def postBSS(url, data):
    """
    Permet de r�cup�rer la r�ponse d'une requ�te aupr�s de l'API BSS
    :param url: url de l'action demand� avec si n�cessaire le token
    :param data: le body de la requ�te post
    :return: BSSResponse la reponse de l'API BSS
    """

    return parseResponse(requests.post(url, data).text)
