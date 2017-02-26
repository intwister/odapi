import requests
import json


class ODAPIClientException(Exception):
    pass


class OdApiConfg:
    def __init__(self, app_id, app_key, base_url, language):
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = base_url
        self.language = language

    @staticmethod
    def load(filepath):
        with open(filepath) as config_file:
            config = json.load(config_file)
            return OdApiConfg(
                config["app_id"],
                config["app_key"],
                config["base_url"],
                config["language"],
            )


class OdApiClient:
    def __init__(self, config):
        self.config = config

    def build_request(self, service, subpath):
        url = u"{}/{}/{}/{}".format(self.config.base_url, service, self.config.language, subpath)
        return requests.get(
            url,
            headers={
              "Accept": "application/json",
              "app_id": self.config.app_id,
              "app_key": self.config.app_key
            }
        )

    def get_word_list(self, params):
        """ Get a list of words

        Args:
            params (dict): A dictionary mapping API filters to values. e.g. {"lexicalCategory": "noun,adjective"}
            domains (str): The domains to filter the list.

        Returns:
            list: Returns a list of words or an exception for API errors.
        """
        url_params = u"%3B".join([u"{}%3D{}".format(k, v) for (k, v) in params.items() if v is not None])
        response = self.build_request("wordlist", url_params)

        if response.status_code == 200:
            return [entry["word"] for entry in response.json()["results"]]
        else:
            raise ODAPIClientException("Bad response from ODAPI: {} {}".format(response.status_code, response.text))


    def define_word(self, word):
        """ Define a word

        Args:
            word (str): The word.

        Returns:
            str: Returns a definition or an exception for API errors.
        """
        response = self.build_request("entries", word)

        if response.status_code == 200:
            result = response.json()
            print result
            try:
                return result["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]
            except:
                raise ODAPIClientException("Couldn't parse JSON in expected manner")
        else:
            raise ODAPIClientException("Bad response from ODAPI: {} {}".format(response.status_code, response.text))

