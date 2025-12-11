#!/bin/bash

# Chạy container Docker với các biến môi trường được thiết lập
sudo docker run -p 8000:3000 \
    -e MILVUS_URL=http://localhost:19530 \
    -e MILVUS_AUTH_ENABLE=true \
    -e MILVUS_USERNAME="root" \
    -e MILVUS_PASSWORD="Milvus" \
    zilliz/attu:v2.4
