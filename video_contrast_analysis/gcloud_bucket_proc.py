# -*- coding: utf-8 -*-

"""
Google Cloud Bucket module, with functions to:
  - watch bucket for changes;
  - run when supported file is uploaded to bucket;
  - upload result of run to same bucket.
"""
from datetime import datetime

from google.auth.credentials import CredentialsWithQuotaProject

from video_contrast_analysis.globals import CONFIG, CONFIG_FILEPATH

from google.cloud import storage

if CONFIG is None:
    raise FileNotFoundError(
        '{CONFIG_FILEPATH!r} must be present for "gcloud_bucket_proc.py" to run'.format(
            CONFIG_FILEPATH=CONFIG_FILEPATH
        )
    )


class CredentialsRefreshable(CredentialsWithQuotaProject):
    def with_quota_project(self, quota_project_id):
        self._quota_project_id = quota_project_id
        return self

    def refresh(self, request):
        pass  # TODO


creds = CredentialsRefreshable()
creds.token = CONFIG["user"]["google_access_token"]
creds._quota_project_id = CONFIG["user"]["google_project_id"]
creds.expiry = datetime.utcfromtimestamp(
    int(CONFIG["user"]["google_access_token_expiry"])
)
storage_client = storage.Client(
    project=CONFIG["user"]["google_project_id"], credentials=creds
)
print("storage_client.list_buckets:", list(storage_client.list_buckets()), ";")
