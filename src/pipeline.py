from kfp.v2 import dsl
from google_cloud_pipeline_components import aiplatform as gcc_aip

from components.data_preprocessing_00 import data_preprocessing

@dsl.pipeline(
    name="pipeline-automl-training-online-retail-example",
)
def pipeline(
    project: str,
    data_path: str,
    bucket: str,
    ):
    # Preprocessing step
    model_data = data_preprocessing(
        data_path = data_path,
        bucket = bucket,
    )
    # Create Vertex dataset
    dataset = gcc_aip.TabularDatasetCreateOp(
        project = project,
        display_name = 'online-retail-example',
        gcs_source = model_data.outputs["Output"],
    )
    # AutoML training
    model = gcc_aip.AutoMLTabularTrainingJobRunOp(
        project = project,
        display_name = 'classification-online-retail-example',
        optimization_prediction_type = "classification",
        optimization_objective = "maximize-au-prc",
        budget_milli_node_hours = 3000,
        disable_early_stopping=False,
        column_specs = {
            'Description': 'text',
            'TotalPaid': 'auto',
            'InvoiceDate': 'auto',
            'PurchaseNumber': 'auto',
            },
        dataset = dataset.outputs['dataset'],
        target_column = 'FuturePurchase',
    )

    # We can further add to this pipeline, see example in: https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/pipelines/automl_tabular_classification_beans.ipynb
    # - Adding Displayed evaluation metrics
    # - Adding a deployment condition
    # - Adding endpoint deployment
    # Or, as the model is already registered in your Model Registry, you can make batch predictions.
