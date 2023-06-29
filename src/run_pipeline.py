from kfp.v2 import compiler
from google.cloud import aiplatform
from google.cloud import storage

from pipeline import pipeline


def main():

    from datetime import datetime
    import pytz

    import os
    import yaml

    # Set up variables:
    file_dir = os.path.dirname(os.path.realpath("__file__"))
    file_name = os.path.join(file_dir, "../config/pipeline_config.yaml")
    file_name = os.path.abspath(os.path.realpath(file_name))

    with open(file_name, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    tz = pytz.timezone("US/Eastern")
    EXECUTION_TS = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    DISPLAY_NAME = "pipeline-automl-training-online-retail-example-{}".format(EXECUTION_TS)

    PROJECT_ID = config["GCP_PROJECT"]
    LOCATION = config["LOCATION"]
    BUCKET_NAME = config["BUCKET_NAME"]

    PIPELINE_ROOT = "gs://{}/online_retail_example/pipeline_root".format(BUCKET_NAME)
    SERVICE_ACCOUNT = config["SVC_ACCT"]
    TEMPLATE_JSON_PATH_LOCAL = "automl_training_pipeline.json"
    TEMPLATE_JSON_PATH = "gs://{}/online_retail_example/pipeline_root/{}".format(
        BUCKET_NAME, TEMPLATE_JSON_PATH_LOCAL
    )

    # Compile kfp pipeline:
    compiler.Compiler().compile(
        pipeline_func=pipeline, package_path=TEMPLATE_JSON_PATH_LOCAL
    )

    # Copy json file to GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"online_retail_example/pipeline_root/{TEMPLATE_JSON_PATH_LOCAL}")

    blob.upload_from_filename(TEMPLATE_JSON_PATH_LOCAL)

    print(
        "File {} uploaded to {}.".format(
            TEMPLATE_JSON_PATH_LOCAL, TEMPLATE_JSON_PATH_LOCAL
        )
    )

    # run pipeline
    job = aiplatform.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path=TEMPLATE_JSON_PATH,
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
        project=PROJECT_ID,
        location=LOCATION,
        parameter_values={
            "project": PROJECT_ID,
            "data_path": 'gs://analytics-ml-insights-support-dxz845m-bucket/online_retail_example/data/OnlineRetail.csv',
            "bucket": BUCKET_NAME,
        },
    )

    job.submit(service_account=SERVICE_ACCOUNT)


if __name__ == "__main__":
    main()
