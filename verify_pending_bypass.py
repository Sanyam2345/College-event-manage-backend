import sys
import os
import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

# Create absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Mock modules
sys.modules['database'] = MagicMock()
sys.modules['database'].Base = object
sys.modules['models'] = MagicMock()

from fastapi import HTTPException
import routers.events as events_router

class PendingBypassTest(unittest.TestCase):
    
    def test_pending_event_registration(self):
        print("\n--- Testing PENDING Event Registration ---")
        
        # Mock PENDING Event (Future date, so not expired)
        pending_event = MagicMock()
        pending_event.id = 1
        pending_event.title = "Pending Event"
        pending_event.status = "PENDING"
        pending_event.date_time = datetime.utcnow() + timedelta(days=10)
        pending_event.capacity = 100
        pending_event.registrations = []

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = pending_event
        db.query.return_value.filter.return_value.filter.return_value.first.return_value = None # No existing reg
        
        user = MagicMock()
        user.id = 555

        try:
            events_router.register_for_event(event_id=1, db=db, current_user=user)
             # If we reach here, it failed to block
            print("FAIL: Vulnerability Confirmed! Registered for PENDING event.")
            # In validation script, we want to Assert it RAISES
            # So if it doesn't raise, we fail.
            self.fail("Security Vulnerability: PENDING event registration succeeded.")
        except HTTPException as e:
            if "not approved" in str(e.detail).lower() or "pending" in str(e.detail).lower():
                print(f"PASS: Blocked PENDING event. Message: {e.detail}")
            else:
                # If it raises some other error (like expired), that's cleaner but here we expect Status error
                print(f"PASS (Alternative Error): {e.detail}")

if __name__ == '__main__':
    unittest.main()
