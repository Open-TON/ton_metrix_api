# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()


def request_to_ton_api(url_request: str):
    print(url_request)
    response = requests.get(url_request)
    data = response.json()

    return data


# get transactions by block:
@app.get("/api/v1/blockchain/blocks/{block_id}/transactions")
def read_item(block_id: str):
    url_request = "https://tonapi.io/v2/blockchain/blocks/"+block_id+"/transactions"
    return request_to_ton_api(url_request)


# get transactions by account:
@app.get("/api/v1/blockchain/accounts/{account_id}/transactions")
def read_item(account_id: str):
    url_request = "https://tonapi.io/v2/blockchain/accounts/"+account_id+"/transactions"
    return request_to_ton_api(url_request)

@app.get("/api/v1/")
def welcome():
    return "Open TON API v1"

@app.get("/api/v1/{request:path}")
def read_item(request: str):
    print(request)
    url_request = "https://tonapi.io/v2/" + request
    return request_to_ton_api(url_request)