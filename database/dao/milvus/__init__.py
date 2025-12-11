from pymilvus import DataType

import dlog
from database import milvus_service
from dconfig import config_models

list_collections = milvus_service.client.list_collections()
if "chunk" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="document_id", datatype=DataType.INT64, description="document_id")
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=config_models.DIM_EMBEDDING)
    schema.add_field(field_name="content", datatype=DataType.VARCHAR, description="content", max_length=65535)
    schema.add_field(field_name="chunk_index", datatype=DataType.VARCHAR, description="chunk_index", max_length=256)

    index_params = milvus_service.client.prepare_index_params()

    index_params.add_index(
        field_name="id",
        index_type="STL_SORT"
    )

    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 128}
    )
    milvus_service.client.create_collection(
        collection_name="chunk",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection document successful")

if "faq" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=config_models.DIM_EMBEDDING)
    schema.add_field(field_name="question", datatype=DataType.VARCHAR, description="question", max_length=65535)
    schema.add_field(field_name="answer", datatype=DataType.VARCHAR, description="answer", max_length=65535)

    index_params = milvus_service.client.prepare_index_params()

    index_params.add_index(
        field_name="id",
        index_type="STL_SORT"
    )

    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 45}
    )
    milvus_service.client.create_collection(
        collection_name="faq",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection faq successful")
if "thread" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True

    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="user_id", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="platform", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="created_at", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=2)

    index_params = milvus_service.client.prepare_index_params()

    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 10}
    )
    milvus_service.client.create_collection(
        collection_name="thread",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection thread successful")
if "message" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="thread_id", datatype=DataType.INT64)
    schema.add_field(field_name="customer_id", datatype=DataType.INT64)
    schema.add_field(field_name="messages", datatype=DataType.ARRAY, element_type=DataType.VARCHAR,
                     max_length=65535, max_capacity=50)
    schema.add_field(field_name="message_type", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="message_source", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="platform", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="platform_message_ids", datatype=DataType.ARRAY, element_type=DataType.VARCHAR,
                     max_length=256, max_capacity=50)
    schema.add_field(field_name="created_at", datatype=DataType.FLOAT)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=2)
    index_params = milvus_service.client.prepare_index_params()

    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 10}
    )
    milvus_service.client.create_collection(
        collection_name="message",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection message successful")

if "customer" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="platform", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="platform_customer_id", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=2)
    index_params = milvus_service.client.prepare_index_params()

    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 10}
    )
    milvus_service.client.create_collection(
        collection_name="customer",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection message successful")

if "document" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=65535)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=2)
    index_params = milvus_service.client.prepare_index_params()

    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 10}
    )
    milvus_service.client.create_collection(
        collection_name="document",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection message successful")

if "cake" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="name", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="image_vector", datatype=DataType.FLOAT_VECTOR, dim=config_models.IMAGE_DIM_EMBEDDING)
    schema.add_field(field_name="description_vector", datatype=DataType.FLOAT_VECTOR, dim=config_models.DIM_EMBEDDING)
    schema.add_field(field_name="image_url", datatype=DataType.VARCHAR, max_length=1024)
    schema.add_field(field_name="description", datatype=DataType.VARCHAR, max_length=65535)
    schema.add_field(field_name="prices", datatype=DataType.ARRAY, element_type=DataType.FLOAT, max_capacity=15)
    schema.add_field(field_name="price_min", datatype=DataType.FLOAT)
    schema.add_field(field_name="price_max", datatype=DataType.FLOAT)
    schema.add_field(field_name="size_min", datatype=DataType.FLOAT)
    schema.add_field(field_name="size_max", datatype=DataType.FLOAT)
    schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="form", datatype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=15,
                     max_length=256)

    index_params = milvus_service.client.prepare_index_params()
    index_params.add_index(
        field_name="id",
        index_type="STL_SORT"
    )
    index_params.add_index(
        field_name="image_vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 128}
    )
    index_params.add_index(
        field_name="description_vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 128}
    )

    milvus_service.client.create_collection(
        collection_name="cake",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection cake successful")

if "bills" not in list_collections:
    schema = milvus_service.client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="bill_id", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="customer_id", datatype=DataType.INT64)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=2)
    schema.add_field(field_name="cakes_order", datatype=DataType.ARRAY, element_type=DataType.VARCHAR,
                     max_capacity=15, max_length=65535)
    schema.add_field(field_name="description", datatype=DataType.VARCHAR, max_length=65535)
    schema.add_field(field_name="status_order", datatype=DataType.INT8)  # Chuẩn hóa thành INT8
    schema.add_field(field_name="status_payment", datatype=DataType.INT8)
    schema.add_field(field_name="status_shipping", datatype=DataType.INT8)
    schema.add_field(field_name="created_at", datatype=DataType.FLOAT)  # Timestamp
    schema.add_field(field_name="update_at", datatype=DataType.FLOAT)
    index_params = milvus_service.client.prepare_index_params()
    index_params.add_index(
        field_name="id",
        index_type="STL_SORT"
    )
    index_params.add_index(
        field_name="customer_id",
        index_type="STL_SORT"  # Index cho customer_id
    )
    index_params.add_index(
        field_name="created_at",
        index_type="STL_SORT"  # Index cho created_at
    )
    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 10}
    )
    milvus_service.client.create_collection(
        collection_name="bills",
        schema=schema,
        index_params=index_params
    )
    dlog.dlog_i("---INIT--- created collection bills successful")
