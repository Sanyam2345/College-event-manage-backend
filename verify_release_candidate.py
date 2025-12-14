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

# Import Routers
from fastapi import HTTPException
import routers.events as events_router

class ReleaseCandidateTest(unittest.TestCase):
    
    def setUp(self):
        self.db = MagicMock()
        self.admin = MagicMock()
        self.admin.is_admin = True
        self.user = MagicMock()
        self.user.id = 101

    def test_admin_update_status_flow(self):
        """Test Admin changing event status (UPCOMING -> CANCELLED) and its effect."""
        print("\n--- Test 1: Admin Status Transition ---")
        
        # Mock existing event
        event = MagicMock()
        event.id = 1
        event.status = "UPCOMING"
        event.title = "Original Title"
        
        self.db.query.return_value.filter.return_value.first.return_value = event
        
        # Update Payload
        update_data = MagicMock()
        update_data.dict.return_value = {"status": "CANCELLED", "title": "Cancelled Event"}
        
        # Call Update API
        updated = events_router.update_event(event_id=1, event=update_data, db=self.db, current_user=self.admin)
        
        # Verify
        self.assertEqual(event.status, "CANCELLED")
        self.assertEqual(event.title, "Cancelled Event")
        print("PASS: Admin successfully changed status to CANCELLED.")

    def test_admin_shrink_capacity_dangerous(self):
        """Test Edge Case: Admin shrinks capacity BELOW current registration count."""
        print("\n--- Test 2: Dangerous Capacity Shrink ---")
        
        # Event has 50 registrations, Capacity 100
        event = MagicMock()
        event.registrations = [1] * 50 # 50 items
        event.capacity = 100
        
        self.db.query.return_value.filter.return_value.first.return_value = event
        
        # Admin shrinks to 10
        update_data = MagicMock()
        update_data.dict.return_value = {"capacity": 10}
        
        # Logic allows it (standard behavior), but we check if it crashes
        try:
            events_router.update_event(event_id=1, event=update_data, db=self.db, current_user=self.admin)
            print("PASS: System survived dangerous capacity shrink. (Business Decision: Allowed)")
            # Note: This means existing users are safe, but new ones blocked. Valid logic.
        except Exception as e:
            self.fail(f"FAIL: Logic crashed on capacity shrink: {e}")

    def test_conflict_warning_persistence(self):
        """Verify conflict warning logic remains robust."""
        print("\n--- Test 3: Conflict Warning Logic ---")
        
        # Upcoming event
        event = MagicMock()
        event.date_time = datetime.utcnow()
        event.status = "UPCOMING"
        event.capacity = 100
        event.registrations = []
        
        # DB finds overlap
        overlapping_reg = MagicMock()
        overlapping_reg.event.title = "Existing Class"
        
        # Mock chain for 'overlapping' check
        # query(Registration).join(Event).filter(...).first()
        self.db.query.return_value.filter.return_value.first.return_value = event # Event exists
        self.db.query.return_value.filter.return_value.filter.return_value.first.return_value = None # Not registered yet
        
        # The key is the overlap query
        # We need a side_effect or distinct mock for the join query
        # Simulating overlap found:
        self.db.query.return_value.join.return_value.filter.return_value.first.return_value = overlapping_reg
        
        # Register
        res = events_router.register_for_event(event_id=1, db=self.db, current_user=self.user)
        
        # Verify warning attached
        self.assertIn("time conflict", res.conflict_warning)
        print("PASS: Conflict warning correctly generated.")

if __name__ == '__main__':
    unittest.main()
