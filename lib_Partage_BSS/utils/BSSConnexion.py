# -*-coding:Latin-1 -*
import requests
import hmac
import hashlib
from time import time
from xml.dom import minidom
from lib_Partage_BSS.exceptions.BSSConnexionException import BSSConnexionException


class BSSConnexion:
    """
    Classe permettant de r�cuperer le token pour int�rroger l'API Partage BSS

    :ivar _domain: Le domaine sur le quel on souhaite travailler
    :ivar _key: La cl� associ� � notre domaine
    :ivar _timestampOfLastToken: Le timesstamp au quel on � obtenue notre dernier token. Permet de renouveller le token si celui-ci est sur le point d'�tre p�rim� ou si il l'est d�j�
    :ivar _token: Le token obtenue via l'api pour utiliser les autres m�thodes de l'API
    :ivar _url: L'url vers l'API BSS Partage (https://api.partage.renater.fr/service/domain/)
    """

    def __init__(self, domain, key):
        """Constructeur de BSS connexion

           Arguments :
                domain(string): Le domaine sur le quel on souhaite se connecter
                key(string): La cl� associ� � notre domaine

            Retour :
                BBSConnexion : l'objet contenant tout les param�tre pour pouvoir se connecter

            Exemple d'utilisation :
            >>>BSSConnexion("domain.com","6b7ead4bd425836e8cf0079cd6c1a05acc127acd07c8ee4b61023e19250e929c")
        """
        self._domain = domain
        """Le domaine sur le quel on souhaite travailler"""
        self._key = key
        """La cl� associ� � notre domaine"""
        self._timestampOfLastToken = 0
        """Le timesstamp au quel on � obtenue notre dernier token. Permet de renouveller le token si celui-ci est sur le point d'�tre p�rim� ou si il l'est d�j�"""
        self._token = ""
        """Le token obtenue via l'api pour utiliser les autres m�thodes de l'API"""
        self._url = "https://api.partage.renater.fr/service/domain/"
        """L'url vers l'API BSS Partage"""

    @property
    def url(self):
        """Get de l'url

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

    @property
    def token(self):
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
                Si l'ecart entre le timestamp actuel et le timestamp de l'obtention du dernier token est de moins de 270 secondes (4min30s) on renvoie le token actuel. Au del� on g�n�re un nouveau token
        """
        actualTimestamp = round(time()) #Timestamp lors de l'appel de _get_token
        if (actualTimestamp-self._timestampOfLastToken) < 270: #Si il y a moin de 270seconde d'ecart on renvoie le token actuel
            return self._token
        else: #sinon on g�n�re un nouveau token
            self._timestampOfLastToken = actualTimestamp #On indique le timestamp au quel on g�n�re le nouveau token
            msg = self._domain+ "|" + str(actualTimestamp) #On constitue le message � chiffrer avec notre cl� priv�
            preAuth = hmac.new(self._key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha1).hexdigest() #On chiffre le message avec la cl� priv�
            data = { #on ajoute les param�tres au body de la requete
                "domain": self._domain,
                "timestamp": str(round(time())),
                "preauth": preAuth
            }
            response = requests.post(self._url+"/Auth", data) #On �met la requ�te et on r�cupere la r�ponse
            dom = minidom.parseString(response.text) #On parse la reponse XML obtenu
            status_code = dom.getElementsByTagName("status")[0].childNodes[0].data #On r�cup�re le code renvoy�
            message = dom.getElementsByTagName("message")[0].childNodes[0].data #On r�cup�re le message renvoy�
            if status_code == "0": #Si on obtient le code de succ�s on r�cup�re le token
                self._token = dom.getElementsByTagName("token")[0].childNodes[0].data
            else: #Sinon on l�ve une exception de type BSSConnexionException
                raise BSSConnexionException(message)
            return self._token
