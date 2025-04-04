import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, AddressRequest

# Тестовая база данных (в памяти)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц
Base.metadata.create_all(bind=engine)


def test_db_inserts_record():
    db = TestingSessionLocal()
    test_record = AddressRequest(
        address="TTp3Vr6BWUZc9nz8bYgaQZ43Dwq2V7YV7h",
        trx_balance="1.0",
        bandwidth="10",
        energy="20",
    )
    db.add(test_record)
    db.commit()
    db.refresh(test_record)

    result = (
        db.query(AddressRequest)
        .filter(AddressRequest.address == "TTp3Vr6BWUZc9nz8bYgaQZ43Dwq2V7YV7h")
        .first()
    )
    assert result is not None
    assert result.trx_balance == "1.0"
