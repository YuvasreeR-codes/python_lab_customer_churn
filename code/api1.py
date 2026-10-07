from fastapi import FastAPI, HTTPException, Header,Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

from fastapi.middleware.cors import CORSMiddleware

from ap12_services import get_churn_summary
from api3_v_services import get_high_risk_customers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Telecom Customer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        "%s %s - incoming request - params=%s",
        request.method,
        request.url.path,
        dict(request.query_params)
    )
    response = await call_next(request)

    logger.info(
        "%s %s - response_status=%s",
        request.method,
        request.url.path,
        response.status_code
    )

    return response


API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)
def verify_api_key(
    x_api_key: str | None = Depends(api_key_header)
):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    return x_api_key

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):

    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "status_code": 404
        }
    )

class ErrorResponse(BaseModel):
    detail: str
    status_code: int

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):

    error = ErrorResponse(
        detail=str(exc.detail),
        status_code=exc.status_code
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump()
    )


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/telecom_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class CustomerResponse(BaseModel):
    customer_id: str
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float
    churn: int

@app.get("/customer/{customer_id}", response_model=CustomerResponse , dependencies=[Depends(verify_api_key)])
def get_customer(customer_id: str):

    db = SessionLocal()

    try:
        query = text("""
            SELECT
                c.customer_id,
                f.tenure,
                dc.contract_name AS contract_type,
                s.InternetService AS internet_service,
                f.monthly_charges,
                f.churn
            FROM customers c
            JOIN fact_customer_account f
                ON c.customer_id = f.customer_id
            JOIN dim_contract dc
                ON f.contract_id = dc.contract_id
            JOIN stg_customer_raw s
                ON c.customer_id = s.customerID
            WHERE c.customer_id = :customer_id
        """)

        result = db.execute(
            query,
            {"customer_id": customer_id}
        ).mappings().first()

        if result is None:
        
            raise HTTPException(
                status_code=404,
                detail=f"Customer '{customer_id}' not found"
            )

        return CustomerResponse(**result)
    except SQLAlchemyError:
        logger.exception("Database error while fetching customer")

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        db.close()

@app.get("/churn/summary", dependencies=[Depends(verify_api_key)])
def churn_summary():

    db = SessionLocal()

    try:
        return get_churn_summary(db)
    except SQLAlchemyError:
        logger.exception("Database error while fetching churn summary")

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        db.close()

@app.get("/customers/high-risk", dependencies=[Depends(verify_api_key)])
def high_risk_customers(
    limit: int | None = 50,
    min_tenure: int | None = None,
    max_tenure: int | None = None
):
  
    db = SessionLocal()

    try:
        return get_high_risk_customers(
            db,
            limit=limit,
            min_tenure=min_tenure,
            max_tenure=max_tenure
        )
    except SQLAlchemyError:
        logger.exception("Database error while fetching high-risk customers")

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        db.close()

class CustomerFeatures(BaseModel):
    customer_id: str
    service_count: int
    tenure_bucket: str
    high_charge_flag: int
    is_long_term_customer: int
    has_streaming_bundle: int
    auto_pay_flag: int
    monthly_charges: float
    total_charges: float

@app.get(
    "/customer/{customer_id}/features",
    response_model=CustomerFeatures,
    dependencies=[Depends(verify_api_key)]
)
def get_customer_features(customer_id: str, ):

    db = SessionLocal()

    try:
        query = text("""
            SELECT
                customer_id,
                service_count,
                tenure_bucket,
                high_charge_flag,
                is_long_term_customer,
                has_streaming_bundle,
                auto_pay_flag,
                monthly_charges,
                total_charges
            FROM customer_ml_features
            WHERE customer_id = :customer_id
        """)

        result = db.execute(
            query,
            {"customer_id": customer_id}
        ).mappings().first()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer '{customer_id}' features not found"
            )

        return CustomerFeatures(**result)
    
    except SQLAlchemyError:
            logger.exception("Database error while fetching customer features")
    
            raise HTTPException(
                status_code=500,
                detail="Database unavailable"
            )
    
    finally:
        db.close()

class ChurnPredictionRequest(BaseModel):
    tenure: int
    monthly_charges: float
    contract_type: str
    service_count: int

    has_streaming_bundle: int
    auto_pay_flag: int
    internet_service: str

    @field_validator("tenure")
    @classmethod
    def validate_tenure(cls, value):
        if value < 0 or value > 100:
            raise ValueError("tenure must be between 0 and 100")
        return value

    @field_validator("monthly_charges")
    @classmethod
    def validate_monthly_charges(cls, value):
        if value <= 0:
            raise ValueError("monthly_charges must be greater than 0")
        return value

from ml4_predict import predict_churn_ml


@app.post(
    "/predict-churn",
    dependencies=[Depends(verify_api_key)]
)
def predict_churn(
    request: ChurnPredictionRequest
):

    try:

        result = predict_churn_ml(

            request.tenure,

            request.monthly_charges,

            request.contract_type,

            request.service_count,

            request.has_streaming_bundle,

            request.auto_pay_flag,

            request.internet_service
        )

        return result


    except Exception:

        logger.exception(
            "Error during churn prediction"
        )

        raise HTTPException(
            status_code=500,
            detail="Model prediction failed"
        )