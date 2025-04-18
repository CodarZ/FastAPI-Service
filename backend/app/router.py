#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from backend.common.response.base import ResponseModel
from backend.core.config import settings

router = APIRouter()


@router.get('/', response_model=ResponseModel)
def read_root():
    return ResponseModel(data=settings)
