# -*-coding:Latin-1 -*
import json
import hmac
import hashlib
from time import time

from lib_Partage_BSS import utils
from lib_Partage_BSS.exceptions import BSSConnexionException
from lib_Partage_BSS.exceptions import DomainException
from lib_Partage_BSS.utils.PostBSSApi import postBSS


class BSSConnexion(object):
    """
    Classe fournissant permettant de r�cuper� un token d'une dur�e de vie de 5min aupr�s de l'API BSS Partage. Elle regen�re un token lorsque celui-ci est sur le point d'expir�

    :ivar _domain: Le domaine sur le quel on souhaite travailler
    :ivar _key: La cl� associ� � notre domaine
    :ivar _timestampOfLastToken: Le timesstamp au quel on � obtenue notre dernier token. Permet de renouveller le token si celui-ci est sur le point d'�tre p�rim� ou si il l'est d�j�
    :ivar _token: Le token obtenue via l'api pour utiliser les autres m�thodes de l'API
    :ivar _url: L'url vers l'API BSS Partage (https://api.partage.renater.fr/service/domain/)
    """
    class __BSSConnexion:
        def __init__(self):
            """Constructeur de BSS connexion

               Arguments :
                    domain(string): Le domaine sur le quel on souhaite se connecter
                    key(string): La cl� associ� � notre domaine

                Retour :
                    BBSConnexion : l'objet contenant tout les param�tre pour pouvoir se connecter

                Exemple d'utilisation :
                >>>BSSConnexion("domain.com","6b7ead4bd425836e8cf0079cd6c1a05acc127acd07c8ee4b61023e19250e929c")
            """
            self._domain = ""
            self._key = {}
            """La cl� associ� � notre domaine"""
            self._timestampOfLastToken = {}
            """Le timesstamp au quel on � obtenue notre dernier token. Permet de renouveller le token si celui-ci est sur le point d'�tre p�rim� ou si il l'est d�j�"""
            self._token = {}
            """Le token obtenue via l'api pour utiliser les autres m�thodes de l'API"""
            self._url = "https://api.partage.renater.fr/service/domain/"
            """L'url vers l'API BSS Partage"""

        @property
        def url(self):
            """Getter de l'url

               Arguments : Aucun

               Retour :
                    string : url de l'API BSS Partage

                Example d'utilisation :
                    >>>con = BSSConnexion("domain.com","6b7ead4bd425836e8cf0079cd6c1a05acc127acd07c8ee4b61023e19250e929c")
                    >>>url = con.url
                    >>>print(url)
                    https://api.partage.renater.fr/service/domain/
            """
            return self._url

        @property
        def domain(self):
            """Getter du domaine

                Arguments : Aucun

                Retour :
                    string : domaine sur le quel on travail

                Example d'utilisation :
                    >>>con = BSSConnexion("domain.com","6b7ead4bd425836e8cf0079cd6c1a05acc127acd07c8ee4b61023e19250e929c")
                    >>>domain = con.domain
                    >>>print(domain)
                    domain.com
            """
            return self._domain

        def token(self, domain):
            """Getter du Token

                Arguments : Aucun

                Retour :
                    string : token permettant la connexion � l'api

                Exception:
                    BSSConnexion en cas d'Eurreur lors de la r�cup�ration du token

                Example d'utilisation :
                    >>>con = BSSConnexion("domain.com","6b7ead4bd425836e8cf0079cd6c1a05acc127acd07c8ee4b61023e19250e929c")
                    >>>token = con.token
                    >>>try:
                    ... print(token) #doctest: +ELLIPSIS
                    ...except BSSConnexionException as err:
                    ... print("BSS Erreur: {0}".format(err))
                    ...
                Description :
                    Le token ayant une dur�e de vie de 5min on le regen�re si il est plus vieux que 4min30s
                    Si l'ecart entre le timestamp actuel et le timestamp de l'obtention du dernier token est de moins de 270 secondes (4min30s) on renvoie le token actuel. Au del� on g�n�re un nouveau token
            """

            if isinstance(domain, str):
                if utils.checkIsDomain(domain):
                    if domain not in self._key:
                        json_config = open('config_lib_bss.json')
                        config = json.load(json_config)
                        self._domain = domain
                        """Le domaine sur le quel on souhaite travailler"""
                        if domain in config:
                            self._key[domain] = config[domain]
                            self._timestampOfLastToken[domain] = 0
                            self._token[domain] = ""
                        else:
                            raise DomainException()
                        json_config.close()
                    actualTimestamp = round(time())
                    if (actualTimestamp - self._timestampOfLastToken[domain]) < 270:
                        return self._token[domain]
                    else:
                        self._timestampOfLastToken[domain] = actualTimestamp
                        msg = domain + "|" + str(actualTimestamp)
                        preAuth = hmac.new(self._key[domain].encode("utf-8"), msg.encode("utf-8"), hashlib.sha1).hexdigest()
                        data = {
                            "domain": domain,
                            "timestamp": str(round(time())),
                            "preauth": preAuth
                        }
                        response = postBSS(self._url + "/Auth", data)
                        status_code = utils.changeToInt(response["status"])
                        message = response["message"]
                        if status_code == 0:
                            self._token[domain] = response["token"]
                        else:
                            raise BSSConnexionException(message)
                        return self._token[domain]
                else:
                    raise DomainException()
            else:
                raise TypeError

    instance = None

    def __new__(cls):  # _new_ est toujours une m�thode de classe
        if not BSSConnexion.instance:
            BSSConnexion.instance = BSSConnexion.__BSSConnexion()
        return BSSConnexion.instance

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, val):
        return setattr(self.instance, attr, val)

