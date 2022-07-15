# -*- coding: utf-8 -*-

"""
Google Cloud Bucket module, with functions to:
  - watch bucket for changes;
  - run when supported file is uploaded to bucket;
  - upload result of run to same bucket.
"""

import json
from datetime import datetime
from mimetypes import guess_type
from time import sleep

import google_auth_httplib2
import httplib2
from google.auth.credentials import CredentialsWithQuotaProject
from google.cloud import pubsub_v1, storage

from video_contrast_analysis.analysis import video_contrast_analysis
from video_contrast_analysis.globals import CONFIG, CONFIG_FILEPATH
from video_contrast_analysis.utils import pp

if CONFIG is None:
    raise FileNotFoundError(
        '{CONFIG_FILEPATH!r} must be present for "gcloud_bucket_proc.py" to run'.format(
            CONFIG_FILEPATH=CONFIG_FILEPATH
        )
    )


class CredentialsRefreshable(CredentialsWithQuotaProject):
    """
    `class` to enable credentials to be provided out-of-band
    """

    def with_quota_project(self, quota_project_id):
        """
        Set project id
        (attached to requests so that requests are not limited by global Google restrictions)

        :param quota_project_id: Project ID
        :type quota_project_id: ```str```

        :return: self
        :rtype: ```CredentialsRefreshable```
        """
        self._quota_project_id = quota_project_id
        return self

    def refresh(self, request):
        """Generate refresh token"""
        refresh_http = httplib2.Http()
        request = google_auth_httplib2.Request(refresh_http)
        response, content = request(
            "https://oauth2.googleapis.com/token?"
            "grant_type=refresh_token&"
            "client_id={client_id}&"
            "client_secret={client_secret}&"
            "refresh_token={refresh_token}".format(
                client_id=CONFIG["user"]["client_id"],
                client_secret=CONFIG["user"]["client_secret"],
                refresh_token=CONFIG["user"]["google_refresh_token"],
            )
        )
        if response.status == 200:
            self.token = response.data["access_token"]
            self.expiry = datetime.utcfromtimestamp(
                int(response.data["expires_in"])
            )
        else:
            raise Exception(response.data)


def mk_callback(storage_client, bucket_obj):
    """
    :param storage_client: storage.Client
    :type storage_client: ```storage.Client```

    :param bucket_obj: Bucket created from `storage.Client`
    :type bucket_obj: ```storage.Client.bucket```

    :return: Callback to run when subscription received
    :rtype: ```Callable[str, None]```
    """

    def callback(message):
        """callback to run when subscription received"""
        message.ack()
        pp({"message": message})
        payload_format = message.attributes["payloadFormat"]
        event_type = message.attributes["eventType"]

        if payload_format == "JSON_API_V1" and event_type == "OBJECT_FINALIZE":
            data = message.data.decode("utf-8")
            object_metadata = json.loads(data)
            print("Object finalized")
            pp({"object_metadata": object_metadata})
            if (
                "video" in object_metadata["contentType"]
                or object_metadata["contentType"] == "application/octet-stream"
            ):
                print("Video detected")
                in_fname = object_metadata["name"]
                out_fname = in_fname + ".srt"
                blob_uri = "gs://{}/{}".format(
                    object_metadata["bucket"], object_metadata["name"]
                )
                try:
                    print("Downloading file {} to {}".format(blob_uri, in_fname))
                    with open(in_fname, "wb") as f:
                        storage_client.download_blob_to_file(blob_uri, f)
                    print("File downloaded successfully")
                    if guess_type(in_fname)[0].startswith("video"):
                        print("Starting process {} => {}".format(in_fname, out_fname))
                        video_contrast_analysis(in_fname, out_fname)
                        print("Process completed")
                        blob = bucket_obj.blob(out_fname)
                        print("Created blob")
                        blob.upload_from_filename(out_fname)
                        print("Uploaded blob")
                    else:
                        print("Downloaded file does not seem like a video")
                except:
                    print(
                        "Processing step failed on {!r} to {!r}".format(
                            in_fname, out_fname
                        )
                    )
                    raise

    return callback


def get_creds():
    """
    Authenticate and return instantiated `storage.Client`

    :return: storage.Client
    :rtype: ```storage.Client```
    """
    creds = CredentialsRefreshable()
    creds.token = CONFIG["user"]["google_access_token"]
    creds._quota_project_id = CONFIG["user"]["google_project_id"]
    creds.expiry = datetime.utcfromtimestamp(
        int(CONFIG["user"]["google_access_token_expiry"])
    )
    return creds


def start():
    """
    0. Authenticate;
    1. Get topic from config;
    2. Subscribe to topic;
    3. Process objects in bucket;
    4. Upload process result back to bucket
    """
    creds = get_creds()
    storage_client = storage.Client(
        project=CONFIG["user"]["google_project_id"], credentials=creds
    )
    subscriber = pubsub_v1.SubscriberClient(credentials=creds)

    # subscribe to the subscription path
    subscription_path = CONFIG["user"]["google_backend_subscription_name"]

    bucket_obj = storage_client.bucket(CONFIG["user"]["google_bucket_name"])

    subscriber.subscribe(
        CONFIG["user"]["google_backend_subscription_name"],
        callback=mk_callback(storage_client, bucket_obj),
    )

    print("Listening for messages on", subscription_path)

    # TODO: [question for Sam] this may not be needed depends if this is done elsewhere
    # The subscriber is non-blocking, so we must keep the main thread from
    # exiting to allow it to process messages in the background.
    while True:
        sleep(60)


if __name__ == "__main__":
    start()
