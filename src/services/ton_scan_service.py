import requests


class TonAPIClientError(Exception):
    pass


class TonAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def _request(self, address, params=None):
        params = {} if params is None else params
        end_point = self.base_url + address
        response = requests.get(end_point, params)
        if response.status_code != 200:
            raise TonAPIClientError(
                f"Ton Scan Service response with error code: {response.status_code}, error: {response.text}")
        return response.json()

    def address_list(self, page=0, count=100):
        addresses = self._request("/address_list/", {"page": page, "count": count})
        return addresses

    def address_details(self, address):
        details = self._request(f"/address_details/{address}/")
        return details
