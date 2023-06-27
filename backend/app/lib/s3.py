import pathlib
import secrets
from os import path
from typing import TYPE_CHECKING, List, Optional, Tuple

from aiobotocore.session import get_session
from litestar.datastructures import UploadFile
from pydantic import BaseModel

from app.env import SETTINGS
from app.errors import FileTooBig, UnsupportedFileType

if TYPE_CHECKING:
    from types_aiobotocore_s3 import S3Client


def format_path(*paths: str) -> str:
    return path.join(SETTINGS.s3.folder, *paths)


def s3_create_client() -> "S3Client":
    session = get_session()
    return session.create_client(
        service_name="s3",
        region_name=SETTINGS.s3.region_name,
        aws_secret_access_key=SETTINGS.s3.secret_access_key,
        aws_access_key_id=SETTINGS.s3.access_key_id,
        endpoint_url=SETTINGS.s3.endpoint_url,
    )


class UploadedFile(BaseModel):
    size: int
    file_id: str
    path: str


async def s3_upload_file(
    file: UploadFile,
    path: Tuple[str, ...],
    max_size: int,
    allowed_extensions: List[str],
    filename: Optional[str] = None,
) -> UploadedFile:
    file_ext = pathlib.Path(file.filename).suffix

    if file_ext not in allowed_extensions:
        raise UnsupportedFileType()

    total_size = 0
    part_number = 0
    parts = []

    if filename:
        file_id = filename
    else:
        file_id = secrets.token_urlsafe()

    filename_ext = f"{file_id}{file_ext}"
    formatted_path = format_path(*path, filename_ext)

    async with s3_create_client() as client:
        multipart = await client.create_multipart_upload(
            Bucket=SETTINGS.s3.bucket,
            Key=formatted_path,
        )

        while data := await file.read(SETTINGS.s3.chunk_size):
            total_size += len(data)
            part_number += 1

            if total_size > max_size:
                await client.abort_multipart_upload(
                    Bucket=SETTINGS.s3.bucket,
                    Key=formatted_path,
                    UploadId=multipart["UploadId"],
                )

                raise FileTooBig()

            part = await client.upload_part(
                Bucket=SETTINGS.s3.bucket,
                Key=formatted_path,
                PartNumber=part_number,
                UploadId=multipart["UploadId"],
                Body=data,
            )
            parts.append({"PartNumber": part_number, "ETag": part["ETag"]})

        await client.complete_multipart_upload(
            Bucket=SETTINGS.s3.bucket,
            Key=formatted_path,
            UploadId=multipart["UploadId"],
            MultipartUpload={"Parts": parts},
        )

    return UploadedFile(
        size=total_size,
        file_id=filename_ext,
        path=formatted_path,
    )
