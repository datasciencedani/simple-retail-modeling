![](assets/images/cover.png)
## About 🔎

A while back, for a job interview, I was asked to use a given CSV file with some transactional retail data to create a model that would **predict if a customer would make another purchase or not**. At that time I didn't finish the problem, but I discovered the data was actually a Kaggle dataset called: [Online retail dataset](https://www.kaggle.com/datasets/lakshmi25npathi/online-retail-dataset). The dataset contains over a year of transactions made between December 2009 and December 2011. The file the company shared with me contained data only for the period 2010-2011. 

The columns we find on the data are: 
- Date of the transaction
- Transaction ID
- Product Stock Code
- Product Description
- Product Quantity
- Product Unit price
- Customer ID  

**Note:** There's an entrance for each product bought on a transaction. 

If you're currently going through this repository you will find the answer I provided to my interviewer, which is some data exploration, preparation, and a first model using Google Cloud's AutoML. I was planning to finish this example but got caught up in other personal/professional projects that took 100% of my attention. Still, didn't want to leave this project stored on my computer, so thought of making it public on GitHub so that anyone that may like can use the idea to practice their modeling skills.   

> Why would someone want to predict the probability of a customer having a future purchase? This prediction could be used to identify the customers who will not buy and target them with discounts and marketing (also saving the cost of applying discounts to customers who were already going to buy).

## My answer 🚀

### Data exploration & preparation 

The first thing we did in our project was explore the data and prepare it for modeling (see [EDA & Preparation Notebook](notebooks/00_eda_and_prep.ipynb)). We analyzed each variable and did transformations such as: justifying the removal of missing `CustomerId` values, scoping our modeling to the United Kingdom market, and identifying and removing useless transactions (as system transactions or cancellation captures).

For further analyses, we propose: 
- Expanding the analysis to other markets outside the UK.
- Analyzing Pro customers (customers with very high quantity orders).

### Label & Feature creation

The next thing we did was create our label (`FuturePurchase`) and features:
- `Description`: A text variable with the descriptions of all the products bought by a customer in a transaction.
- `TotalPaid`: The total amount of money paid by the customer for the whole transaction.
- `InvoiceDate`: The date of the purchase.
- `PurchaseNumber`: The purchase number for that customer (1st purchase of the customer, 2nd purchase of the customer, etc).

We created a data frame with this label and features so that we could feed it to a model as a next step.

### Modeling POC

With the new data frame, the next thing we wanted to do was test our hypothesis. Can we use those `features` (and our created `label`) to predict if a customer will make a future purchase?

We decided to test our model hypothesis using [Google Cloud's AutoML](https://cloud.google.com/vertex-ai/docs/tabular-data/tabular101) (see [Modeling POC PDF](assets/docs/00_modeling_poc_automl.pdf)). AutoML is a great alternative to test a Machine Learning model without taking a lot of time in feature preparation and model selection. AutoML performs [variable transformations](https://cloud.google.com/vertex-ai/docs/datasets/data-types-tabular) and uses ensemble tree-based/deep-learning techniques to create a model.

After creating a new [Vertex Dataset](https://cloud.google.com/vertex-ai/docs/training/using-managed-datasets) with our prepared data, and running an AutoML training model for an hour, these are the results we got (check all the previous links for more information on Google's AutoML). 

![Alt text](assets/images/automl.png)

Unfortunately, our resulting model did not have a great performance in identifying customers who would not make a future purchase. But we could link this behavior back to the way we were obtaining our problem's label. Overall, this first approach was incredibly helpful in identifying possible causes of unwanted behavior so that we would be able to iterate and try different ways of creating features and labels to solve our problem.

In the [Modeling POC document](assets/docs/00_modeling_poc_automl.pdf), you will find we propose obtaining a `new_label` by using more information on the distribution of time between purchases. Removing assumptions about customers' next purchase if we don't have enough information.

The next steps on our modeling journey would be:
- Perform experiments with new label calculation.
- Engineer features that would provide our model with more context on the customers' purchase history (such as the time since the last purchase, or different techniques to embed and aggregate purchase product descriptions).
- Try out custom-trained models (start with tree-based to handle highly skewed variables) and perform experiments with hyperparameter tuning.

### Beginnings of Model Deployment

The final thing we did on our project was prepare for model deployment. Machine Learning pipelines are used to orchestrate and automate workflows as model training. A pipeline component is simply the containerized code that performs a step in your workflow. Remember we performed a series of steps to transform our source data into the modeling dataset we would use as input for our model? Under the `src/components` folder, you will find the [Python script](src/components/data_preprocessing_00.py) that contains an automation of those data transformations. This component could be part of a training and inference pipeline. 

What we did to show a glimpse of further work was creating a simple training pipeline, performing a data preprocessing step, followed by the creation of a dataset (data version control), and training a model (see [Pipeline Code](src/pipeline.py)).

![Alt text](assets/images/vertex-pipeline.png)

We build our model pipeline using the [Kubeflow SDK](https://cloud.google.com/vertex-ai/docs/pipelines/build-pipeline#build-pipeline) and leveraging the [library of pre-written components](https://cloud.google.com/vertex-ai/docs/pipelines/gcpc-list) provided by Google.

The next step in building the pipeline would be adding model evaluation and a deployment condition (if we want to deploy or model to an endpoint to generate online predictions).

![Alt text](assets/images/complete-vertex-pipeline.png)

> Source: [Use Vertex Pipelines to build an AutoML classification end-to-end workflow](https://cloud.google.com/blog/topics/developers-practitioners/use-vertex-pipelines-build-automl-classification-end-end-workflow)

Additionally, it's important to plan for:  
- Model performance and data monitoring (that can be automatically obtained when using [Vertex AI Batch Predictions](https://cloud.google.com/vertex-ai/docs/model-monitoring/model-monitoring-batch-predictions)).  
- Automatic pipeline running ([scheduling](https://cloud.google.com/vertex-ai/docs/pipelines/schedule-pipeline-run) or [triggering](https://cloud.google.com/vertex-ai/docs/pipelines/trigger-pubsub)). 
- CI/CD environment (ex. [GitHub actions workflow](https://docs.github.com/en/actions/using-workflows) that compiles, stores, and runs test pipelines jobs when changes are pushed to a repository).    

- - -
    🚨Disclaimer:

    The project in this repository is not completely finished, but it can serve as an example of how an idea of an ML project can take various iterations to be done. 

- - -
Any suggestions or doubts? Please reach out! I'll be happy to connect.

**👥 LinkedIn:** [linkedin.com/in/datasciencedani](http://www.linkedin.com/in/datasciencedani)  
**🐦 Twitter:** [twitter.com/datasciencedani](https://twitter.com/datasciencedani)  
**📨 Email:** [datasciencedani@gmail.com](datasciencedani@gmail.com)  
**🌐 Site:** [datasciencedani.super.site](https://datasciencedani.super.site)
