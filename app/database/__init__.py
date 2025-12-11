from database.milvus_service import MilvusService
from database.minio_service import MinioService
from database.mysql_service import MySQLService
from dconfig import config_object
import dlog

milvus_service = None
try:
    URI_CONNECTION_MILVUS = config_object.URI_CONNECTION_MILVUS
    TOKEN_CONNECTION_MILVUS = config_object.TOKEN_CONNECTION_MILVUS
    MILVUS_DATABASE_NAME = config_object.MILVUS_DATABASE_NAME
    milvus_service = MilvusService(uri_connection=URI_CONNECTION_MILVUS, token=TOKEN_CONNECTION_MILVUS,
                                   database_name=MILVUS_DATABASE_NAME)
    dlog.dlog_i("---INIT---:  milvus service successful")
except Exception as e:
    dlog.dlog_e(f"---INIT---:  milvus service Unsuccessful {e}")

mysql_service = None
try:
    URI_CONNECTION_MYSQL = config_object.URI_CONNECTION_MYSQL
    DB_NAME_MYSQL = config_object.DB_NAME_MYSQL
    USER_NAME_MYSQL = config_object.USER_NAME_MYSQL
    PASSWORD_MYSQL = config_object.PASSWORD_MYSQL
    mysql_service = MySQLService(host=URI_CONNECTION_MYSQL, user=USER_NAME_MYSQL, password=PASSWORD_MYSQL,
                                 database=DB_NAME_MYSQL)
    mysql_service.create_tables()
    dlog.dlog_i("---INIT---:  mysql service successful")
except Exception as e:
    dlog.dlog_e(f"---INIT---:  mysql service Unsuccessful {e}")

minio_service = None
try:
    minio_service = MinioService(config_object.URI_CONNECTION_MINIO, config_object.ACCESS_KEY_MINIO,
                                 config_object.SECRET_KEY_MINIO, config_object.BUCKET_NAME_MINIO)
    dlog.dlog_i("---INIT---:  minio service successful")
except Exception as e:
    dlog.dlog_e(f"---INIT---:  minio service Unsuccessful {e}")
