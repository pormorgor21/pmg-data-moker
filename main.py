import pandas as pd
import random as rd
import re
import io

from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from template_data import *

app = FastAPI(
    title="Data Mocker API",
    description="This is a simplest data mocker way",
    version="1.4.0",
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def getTemplateData(params):
    keys = params.count("_key")

    # Get All Keys
    tmp_data = {}
    html_keys = ["_key"+str(i) for i in range(1, keys+1)]
    keys = []
    for i in range(1, len(html_keys) + 1):
        pattern = "_key%s=(.+)&_val%s" % (i, i)
        res = re.findall(r'%s' % (pattern), params)[0]
        keys.append(res)
    # Get All Values
    for i in range(0, len(keys)):
        if i == len(keys) - 1:
            pattern = "_val%s=(.+)&rowno" % (i + 1)
        else:
            pattern = "_val%s=(.+)&_key%s" % (i + 1, i+2)
        vals = re.findall(r'%s' % (pattern), params)[0]
        tmp_data[keys[i]] = vals.split("%2C")
    keys.append("id")
    return keys, tmp_data



# Index
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Data Mocker",
        "status": True,
    })

# Mocking Page


@app.get("/mock", response_class=HTMLResponse)
async def mock(request: Request):
    # check colno is integer
    try:
        colno = int(str(request.query_params).replace("colno=", ""))
        return templates.TemplateResponse("mock.html", {
            "request": request,
            "title": "Data Mocker",
            "colno": [index for index in range(1, colno + 1)]
        })
    except:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "title": "Data Mocker",
            "status": False
        })

# Mocked Page
# @app.get("/mocked", response_class=HTMLResponse)


@app.get("/mocked")
async def mock(request: Request):
    if re.findall(r'rowno=[0-9]+', str(request.query_params)):
        rowNo = int(re.findall(
            r'rowno=[0-9]+', str(request.query_params))[0].replace("rowno=", ""))
        keys, raw_data = getTemplateData(str(request.query_params))
        data = []
        for index in range(0, rowNo):
            tmp = {}
            tmp["id"] = index + 1
            for key in raw_data:
                tmp[key] = raw_data[key][rd.randint(0, len(raw_data[key]) - 1)]
            data.append(tmp)

        # Define Ouput Type
        if re.findall(r'api_mode=TRUE', str(request.query_params)):
            return {
                "Message": "Data Mocker",
                "status": "OK",
                "mocked_data": data
            }
        else:
            return templates.TemplateResponse("mocked.html", {
                "request": request,
                "title": "Data Mocker",
                "status": True,
                "keys": keys,
                "data": data,
            })

    else:
        return templates.TemplateResponse("mocked.html", {
            "request": request,
            "title": "Data Mocker",
            "status": False,
        })


# How to Use Page
@app.get("/howtouse", response_class=HTMLResponse)
async def howto(request: Request):
    return templates.TemplateResponse("howtouse.html", {
        "request": request,
        "title": "Data Mocker"
    })

@app.get("/howtouse_api", response_class=HTMLResponse)
async def howto(request: Request):
    return templates.TemplateResponse("howtouse_api.html", {
        "request": request,
        "title": "Data Mocker"
    })


@app.post("/mock")
async def getData(request: Request):
    body = await request.json()
    try:
        rowNo = body["rowNo"]

        data = []

        for index in range(0, rowNo):
            tmp = {}
            tmp["id"] = index + 1
            for key in body:
                if key != "rowNo":
                    tmp[key] = body[key][rd.randint(0, len(body[key]) - 1)]
            data.append(tmp)

        return {
            "Message": "Data Mocker",
            "status": "OK",
            "mocked_data": data
        }
    except:
        return {
            "Message": "Data Mocker",
            "status": "Failed",
            "description": "Your Request Body have no 'rowNo'."
        }

@app.post("/th_province")
def getProvince():
    return {
        "Message": "Data Mocker",
        "status": "True",
        "province": TH_PROVINCE
    }

@app.post("/th_amphur")
def getAmphur():
    return {
        "Message": "Data Mocker",
        "status": "True",
        "province": TH_AMPHUR
    }

@app.post("/th_tambon")
def getTambon():
    return {
        "Message": "Data Mocker",
        "status": "True",
        "tambon": TH_TAMBON
    }