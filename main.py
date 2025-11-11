from datetime import datetime,timezone
from fastapi import FastAPI, HTTPException, Request,Depends
from sqlmodel import create_engine,SQLModel,Session,select,Field
from typing import Any, Annotated,Generic,TypeVar
from contextlib import asynccontextmanager
from pydantic import BaseModel

class Campaign(SQLModel,table=True):
    campaign_id: int |None = Field(default = None,primary_key=True)
    name:str = Field(index=True)
    due_date:datetime|None = Field(default=None,index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=True, index=True)


sqllite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqllite_file_name}"

connect_args = {"check_same_thread":False}
engine = create_engine(sqlite_url,connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
    

SessionDeep = Annotated[Session,Depends(get_session)]

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
       if not session.exec(select(Campaign)).first():
           session.add_all([
               Campaign(name="Kanjut",due_date=datetime.now()),
                Campaign(name="badag",due_date=datetime.now())
           ])
           session.commit()

    yield

app = FastAPI(root_path="/api/v1",lifespan=lifespan)

T = TypeVar("T")
class Response(BaseModel,Generic[T]):
    data:T

class CampaignCreate(SQLModel):
    name:str
    due_date:datetime|None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/campaign',response_model=Response[list[Campaign]])
async def get_campaigns(session:SessionDeep):
    data = session.exec(select(Campaign)).all()
    return {"data":data}

@app.get("/campaign/{id}",response_model=Response[Campaign])
async def get_campaign(id: int,session:SessionDeep):
    data = session.get(Campaign,id)

    if not data:
        raise HTTPException(status_code=404)
    
    return {"data":data}

@app.post('/campaign',status_code=201,response_model=Response[Campaign])
async def create_campaign(body:CampaignCreate,session:SessionDeep):
    db_campaign = Campaign.model_validate(body)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data":db_campaign}


@app.put("/campaign/{id}",response_model=Response[Campaign])
async def update_campaign(campaign:CampaignCreate,id:int,session:SessionDeep):
    data = session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}


@app.delete("/campaign/{id}")
async def delete_campaign(id:int,session:SessionDeep):
    data = session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    
    session.delete(data)
    session.commit()


