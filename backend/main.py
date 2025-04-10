#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI

from backend.core.settings import settings

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': settings.ENVIRONMENT}
