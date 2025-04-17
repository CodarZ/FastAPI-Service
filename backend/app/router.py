#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from backend.core.config import settings

router = APIRouter()


@router.get('/')
def read_root():
    return settings
