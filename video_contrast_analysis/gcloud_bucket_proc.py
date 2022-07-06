# -*- coding: utf-8 -*-

"""
Google Cloud Bucket module, with functions to:
  - watch bucket for changes;
  - run when supported file is uploaded to bucket;
  - upload result of run to same bucket.
"""

import json
from datetime import datetime
from socket import gethostname
from time import sleep

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
        pass  # TODO


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
        print("Received message:\n")
        message.ack()
        attributes = message.attributes
        data = message.data.decode("utf-8")

        # event_type = attributes["eventType"]
        # bucket_id = attributes["bucketId"]
        object_id = attributes["objectId"]
        # generation = attributes["objectGeneration"]
        pp(attributes)

        if attributes["payloadFormat"] == "JSON_API_V1":
            object_metadata = json.loads(data)
            # size = object_metadata["size"]
            # content_type = object_metadata["contentType"]
            # metageneration = object_metadata["metageneration"]
            pp(object_metadata)

        if (
            message.attributes.eventType == "OBJECT_FINALIZE"
        ):  # TODO: check that the content_type is supported by opencv
            # new file was created / updated
            in_fname = "video"
            out_fname = "video_contrast_analysis.srt"

            try:
                with open(in_fname, "wb") as f:
                    storage_client.download_blob_to_file(object_id, f)
                video_contrast_analysis(in_fname, out_fname)
            except:
                print(
                    "Processing step failed on {!r} to {!r}".format(in_fname, out_fname)
                )

            try:
                blob = bucket_obj.blob("{}_{}".format(object_id, out_fname))
                blob.upload_from_filename(out_fname)
            except:
                print("Failed to upload {!r} to {!r}".format(out_fname, object_id))

    return callback


def auth_and_return_client():
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
    return storage.Client(
        project=CONFIG["user"]["google_project_id"], credentials=creds
    )


def start():
    """
    0. Authenticate;
    1. Create topic;
    2. Subscribe bucket to topic;
    3. Process objects in bucket;
    4. Upload process result back to bucket
    """
    storage_client = auth_and_return_client()

    # create topic to listen to the bucket
    topic_name = gethostname()

    bucket_obj = storage_client.bucket(CONFIG["user"]["google_bucket_name"])
    notification = bucket_obj.notification(topic_name)
    notification.create()

    # define path to subscribe to
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        CONFIG["user"]["google_project_id"], topic_name
    )

    # subscribe to the subscription path
    subscriber.subscribe(
        subscription_path, callback=mk_callback(storage_client, bucket_obj)
    )

    print("Listening for messages on {}".format(subscription_path))

    # TODO: [question for Sam] this may not be needed depends if this is done elsewhere
    # The subscriber is non-blocking, so we must keep the main thread from
    # exiting to allow it to process messages in the background.
    while True:
        sleep(60)

    # TODO: [question for Sam] when instance has ended need to delete the subscription that was created
    # notification.delete()


if __name__ == "__main__":
    start()
