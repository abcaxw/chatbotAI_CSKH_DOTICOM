import boto3
import dlog
from dconfig import config_object


class MinioService:
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name):
        self.client = None
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key

    def connect(self):
        try:
            self.client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
            dlog.dlog_i("Connect to Minio successfully")
        except Exception as e:
            dlog.dlog_e(f"Connect to Minio failed: {str(e)}")

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            dlog.dlog_i("Disconnected from Minio successfully")

    def upload_file(self, file_path, key, doc_type="pdf"):
        try:
            if self.client is None:
                self.connect()
            # Đặt header ContentDisposition để hiển thị file inline
            metadata = {
                "ContentDisposition": "inline"
            }
            if doc_type != "image":
                metadata["ContentType"] = "application/pdf"
            else:
                metadata["ContentType"] = get_content_type(key)
            self.client.upload_file(file_path, self.bucket_name, key, ExtraArgs=metadata)
            dlog.dlog_i(f"Upload file {file_path} to Minio successfully")
        except Exception as e:
            dlog.dlog_e(f"Upload file {file_path} to Minio failed: {str(e)}")

    def delete_file(self, key):
        try:
            if self.client is None:
                self.connect()
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            dlog.dlog_i(f"Delete file {key} from Minio successfully")
        except Exception as e:
            dlog.dlog_e(f"Delete file {key} from Minio failed: {str(e)}")

    def get_url_file(self, key, doc_type="pdf"):
        try:
            if self.client is None:
                self.connect()
            # Thêm tham số ResponseContentDisposition để trình duyệt mở file trực tiếp

            params = {
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'ResponseContentDisposition': f'inline; filename="{key}"'
                }
            if doc_type != "image":
                params["ResponseContentType"] = "application/pdf"
            else:
                params["ResponseContentType"] = get_content_type(key)
            url = self.client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=3600
            )
            url = url.replace(config_object.DOMAIN_MINIO, config_object.DOMAIN_SERVER)
            return url
        except Exception as e:
            dlog.dlog_e(f"Get url file {key} from Minio failed: {str(e)}")

def get_content_type(key):

    extension = key.split('.')[-1].lower()

    content_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
    }
    return content_types.get(extension, 'application/octet-stream')