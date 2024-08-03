from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.models import User
from models.schemas import UserList, UserOut, UserUpdate, DeleteUserRequest
from utils.token import decode_access_token, update_token

router = APIRouter()

