import sys
from sqlalchemy import inspect
from sqlalchemy.schema import UniqueConstraint
import models
import schemas
from pydantic.fields import FieldInfo

def verify_hardening():
    print("Verifying hardening measures...")
    errors = []

    # 1. Verify UniqueConstraint on Registration
    print("- Checking Database Constraints...")
    found_uq = False
    if hasattr(models.Registration, '__table_args__'):
        for arg in models.Registration.__table_args__:
            if isinstance(arg, UniqueConstraint):
                if 'user_id' in arg.columns and 'event_id' in arg.columns:
                    found_uq = True
                    print("  [OK] UniqueConstraint('user_id', 'event_id') found on Registration model.")
    
    if not found_uq:
        errors.append("Missing UniqueConstraint on Registration model.")

    # 2. Verify max_length on Pydantic Schemas
    print("- Checking API Schema Validations...")
    schema_checks = [
        (schemas.UserCreate, 'email', 255),
        (schemas.UserCreate, 'full_name', 100),
        (schemas.EventCreate, 'title', 200),
    ]

    for schema_cls, field_name, expected_len in schema_checks:
        field = schema_cls.model_fields[field_name]
        # Pydantic v2 stores max_length in metadata
        has_len = False
        for meta in field.metadata:
            if hasattr(meta, 'max_length') and meta.max_length == expected_len:
                has_len = True
                print(f"  [OK] {schema_cls.__name__}.{field_name} has max_length={expected_len}")
        
        if not has_len:
             errors.append(f"Missing max_length={expected_len} on {schema_cls.__name__}.{field_name}")

    if errors:
        print("\nERRORS FOUND:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nSUCCESS: All hardening measures verified internally.")

if __name__ == "__main__":
    verify_hardening()
