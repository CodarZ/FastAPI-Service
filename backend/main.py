#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World!'}
