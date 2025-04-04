from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from tronpy import Tron
from typing import List, Generator

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
tron_client = Tron()


class AddressRequest(Base):
    __tablename__ = "address_requests"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    trx_balance = Column(String)
    bandwidth = Column(String)
    energy = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


# Pydantic модель для ответа
class AddressRequestResponseSchema(BaseModel):
    address: str
    trx_balance: str
    bandwidth: str
    energy: str
    timestamp: datetime

    # Обновляем конфигурацию для Pydantic V2
    model_config = ConfigDict(
        from_attributes=True
    )  # Заменили orm_mode на from_attributes


class AddressRequestSchema(BaseModel):
    address: str


class PaginatedResponse(BaseModel):
    total: int
    items: List[AddressRequestResponseSchema]


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/address/", response_model=AddressRequestResponseSchema)
def fetch_tron_address(
    data: AddressRequestSchema, db: Session = Depends(get_db)
) -> AddressRequestResponseSchema:
    try:
        address = data.address
        account_info = tron_client.get_account(address)
        resources = tron_client.get_account_resource(address)

        trx_balance = str(
            account_info.get("balance", 0) / 1_000_000
        )  # Convert from Sun to TRX
        bandwidth = str(resources.get("freeNetUsed", 0))
        energy = str(resources.get("EnergyUsed", 0))

        new_request = AddressRequest(
            address=address, trx_balance=trx_balance, bandwidth=bandwidth, energy=energy
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        # Возвращаем Pydantic модель, которая будет сериализована
        return new_request
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/addresses/", response_model=PaginatedResponse)
def get_address_requests(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
) -> PaginatedResponse:
    records = (
        db.query(AddressRequest)
        .order_by(AddressRequest.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(AddressRequest).count()
    return {"total": total, "items": records}
