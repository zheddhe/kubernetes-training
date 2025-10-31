from sqlalchemy import create_engine, MetaData, text, Integer, String
from sqlalchemy.schema import Column, Table
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI
from pydantic import BaseModel
import os
import logging

app = FastAPI()

# lire les variables d'env des secrets
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")
# lire les variables d'env du service kubernetes mysql
mysql_host = os.getenv("MYSQL_SERVICE_HOST")
mysql_port = os.getenv("MYSQL_SERVICE_PORT")

# # on utilise le logger d'uvicorn pour donner des informations pour la mise au point
# logger = logging.getLogger("uvicorn")
# logger.info("=== ENV DEBUG ===")
# logger.info(f"MYSQL_USER: {mysql_user}")
# logger.info(f"MYSQL_PASSWORD: {mysql_password}")
# logger.info(f"MYSQL_DATABASE: {mysql_database}")
# logger.info(f"MYSQL_SERVICE_HOST: {mysql_host}")
# logger.info(f"MYSQL_SERVICE_PORT: {mysql_port}")
# logger.info("=================")
# logger.info(os.environ)

conn_string = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

mysql_engine = create_engine(conn_string)

metadata = MetaData()

class TableSchema(BaseModel):
    table_name: str
    columns: dict

@app.get("/tables")
async def get_tables():
    with mysql_engine.connect() as connection:
        results = connection.execute(text('SHOW TABLES;'))
        dict_res = {}
        dict_res['database'] = [str(result[0]) for result in results.fetchall()]
        return dict_res

@app.put("/table")
async def create_table(schema: TableSchema):
    columns = [Column(col_name, eval(col_type)) for col_name, col_type in schema.columns.items()]
    table = Table(schema.table_name, metadata, *columns)
    try:
        metadata.create_all(mysql_engine, tables=[table], checkfirst=False)
        return f"{schema.table_name} successfully created"
    except SQLAlchemyError as e:
        return dict({"error_msg": str(e)})
