import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Ensure backend directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

sys.modules['database'] = MagicMock()
sys.modules['database'].Base = object
sys.modules['models'] = MagicMock()

from fastapi import HTTPException
import routers.events as events_router

def test_expired_event_bypass():
    print("Testing Security Fix: Direct Registration for Expired Event...")
    
    # 1. Mock Event (Expired but status says UPCOMING - simulates the Loophole)
    past_time = datetime.utcnow() - timedelta(hours=1)
    
    expired_event = MagicMock()
    expired_event.id = 1
    expired_event.title = "Expired Event"
    expired_event.status = "UPCOMING" # The loophole setting
    expired_event.date_time = past_time
    expired_event.capacity = 100
    expired_event.registrations = []
    
    # 2. Mock DB
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = expired_event
    
    # 3. Mock User
    user = MagicMock()
    user.id = 123
    
    # 4. Attempt Registration
    try:
        events_router.register_for_event(event_id=1, db=db, current_user=user)
        print("FAIL: Registration succeeded for expired event!")
    except HTTPException as e:
        if "Expired" in e.detail:
            print(f"PASS: Blocked expired event with error: {e.detail}")
        else:
            print(f"FAIL: Wrong error message: {e.detail}")

if __name__ == "__main__":
    test_expired_event_bypass()
