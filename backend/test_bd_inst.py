#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.traffic_dtp.db.session import Base as SessionBase
from src.traffic_dtp.db.models.user import User
print("Base в session:", id(SessionBase))
print("Base в User:", id(User.__base__))
print("Одинаковые?", SessionBase is User.__base__)  # False ← ПРОБЛЕМА!