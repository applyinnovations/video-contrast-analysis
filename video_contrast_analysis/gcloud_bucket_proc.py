# -*- coding: utf-8 -*-

"""
Google Cloud Bucket module, with functions to:
  - watch bucket for changes;
  - run when supported file is uploaded to bucket;
  - upload result of run to same bucket.
"""

import json

from datetime import datetime

from google.auth.credentials import CredentialsWithQuotaProject

from video_contrast_analysis.globals import CONFIG, CONFIG_FILEPATH

from google.cloud import storage, pubsub_v1

from analysis import video_contrast_analysis

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


project_id = CONFIG["user"]["google_project_id"]
creds = CredentialsRefreshable()
creds.token = CONFIG["user"]["google_access_token"]
creds._quota_project_id = project_id
creds.expiry = datetime.utcfromtimestamp(
    int(CONFIG["user"]["google_access_token_expiry"])
)
storage_client = storage.Client(
    project=project_id, credentials=creds
)

# create topic to listen to the bucket
topic_name = "" # TODO: this should be unique per cloud instance
bucket = storage_client.bucket(CONFIG["user"]["google_bucket_name"])
notification = bucket.notification(topic_name)
notification.create()

# define path to subscribe to
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, topic_name)

# define callback to run when subscription received
def callback(message):
    print("Received message:\n")
    message.ack()
    attributes = message.attributes
    data = message.data.decode("utf-8")
    
    # event_type = attributes["eventType"]
    # bucket_id = attributes["bucketId"]
    object_id = attributes["objectId"]
    # generation = attributes["objectGeneration"]
    print(attributes)

    if attributes["payloadFormat"] == "JSON_API_V1":
        object_metadata = json.loads(data)
        # size = object_metadata["size"]
        # content_type = object_metadata["contentType"]
        # metageneration = object_metadata["metageneration"]
        print(object_metadata)

    if message.attributes.eventType == "OBJECT_FINALIZE": # TODO: check that the content_type is supported by opencv
        # new file was created / updeated
        in_fname = 'video'
        out_fname = 'video_contrast_analysis.srt'

        try:
            with open(in_fname, 'wb') as f:
                storage_client.download_blob_to_file(object_id, f)
            video_contrast_analysis(in_fname, out_fname)
            blob = bucket.blob("{}_{}".format(object_id, out_fname))
            blob.upload_from_filename(out_fname)

        except:
            print('Processing step failed')

# subscribe to the subscription path
subscriber.subscribe(subscription_path, callback=callback)

print("Listening for messages on {}".format(subscription_path))

# TODO: [question for Sam] this may not be needed depends if this is done elsewhere
# The subscriber is non-blocking, so we must keep the main thread from
# exiting to allow it to process messages in the background.
while True:
    time.sleep(60) 

# TODO: [question for Sam] when instance has ended need to delete the subscription that was created
# notification.delete()