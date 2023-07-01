# -*- coding: utf-8 -*-
import requests
import os
from rate_limiter import rate_limiter

TONAPI_KEY = os.getenv("TONAPI_KEY") or None
TONAPI_BASE_URL = "https://tonapi.io/v2"


class TonAPIClientError(Exception):
    pass


class TonAPIClient:
    def _request(self, address, params=None):
        params = {} if params is None else params

        # Making a request to tonapi.io
        if TONAPI_KEY:
            response = requests.get(TONAPI_BASE_URL + address, params, headers={"Authorization": f"Bearer {TONAPI_KEY}"})
        else:
            response = requests.get(TONAPI_BASE_URL + address, params)

        # Checking the response
        if response.status_code != requests.codes.ok:
            raise TonAPIClientError(
                f"Tonapi response with error code: {response.status_code}, error: {response.text}")
        return response.json()

    @rate_limiter(limit=0.9)
    def tx_by_block(self, block_id):
        """
       Find transactions by block id.

       :param str block_id: Block id e.g. "(-1,8000000000000000,4234234)"
        """
        request_url = f"/blockchain/blocks/{block_id}/transactions"
        transactions = self._request(request_url)
        return transactions

    @rate_limiter(limit=0.9)
    def tx_by_account(self, account_id):
        """
       Find transactions by account id.

       :param str account_id: Account id in any format
        """
        request_url = f"/blockchain/accounts/{account_id}/transactions"
        transactions = self._request(request_url)
        return transactions

    @rate_limiter(limit=0.9)
    def raw_request(self, request_url, params):
        """
        Make any request to tonapi.io

        :param request_url: Endpoint. e.g. "/rates"
        :param params: Any parameters. e.g. {"tokens": "ton", "currencies": "rub"}
        """
        response = self._request(request_url, params)
        return response
