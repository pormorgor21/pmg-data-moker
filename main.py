import pandas as pd
import random as rd
import re
import io

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
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
@app.get("/mocked", response_class=HTMLResponse)
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
        if re.findall(r'is_plaintext=YES', str(request.query_params)):
            return templates.TemplateResponse("mocked_csv.html", {
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
