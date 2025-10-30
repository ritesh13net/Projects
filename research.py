"""
1. S3 Buckets- Boto3
2. Iam Roles and Users
3. Complete Infrastructure of AWS Sagemaker, Endpoints
"""

import sagemaker
from sklearn.model_selection import train_test_split
import boto3
import pandas as pd

sm_boto3=boto3.client("sagemaker")
sess=sagemaker.Session()
region=sess.boto_session.region_name
bucket="mobsagemaker213"
print("Using bucket" + bucket)

print(region)

df=pd.read_csv("mob_price_classification_train.csv")
df.head()

df.isnull().sum()

df['price_range'].value_counts()

features=list(df.columns)

label = features.pop(-1)

x=df[features]
y=df[label]

X_train, X_test, y_train, y_test = train_test_split(x,y, test_size=0.15, random_state=0)

print(X_train.shape)
print(X_test.shape)
print(y_train.shape)
print(y_test.shape)

trainX = pd.DataFrame(X_train)
trainX[label] = y_train

testX = pd.DataFrame(X_test)
testX[label] = y_test

trainX.to_csv("train-V-1.csv",index = False)
testX.to_csv("test-V-1.csv", index = False)

## send data to S3. Sagemaker will take the data for trainign from s3
sk_prefix="sagemaker/mobile_price_classification/sklearncontainer"
trainpath=sess.upload_data(path='train-V-1.csv',bucket=bucket,key_prefix=sk_prefix)

testpath=sess.upload_data(path='test-V-1.csv',bucket=bucket,key_prefix=sk_prefix)

print(trainpath)
print(testpath)

"""#### Script used by AWS Sagemaker To Train Models"""

# Commented out IPython magic to ensure Python compatibility.
%%writefile script.py

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix,precision_score
import sklearn
import joblib
import boto3
import pathlib
from io import StringIO
import argparse
import os
import numpy as np
import pandas as pd


def model_fn(model_dir):
    clf=joblib.load(os.path.join(model_dir,"model.joblib"))

if __name__=="__main__":

    print("[Info] Extracting arguments")
    parser=argparse.ArgumentParser()

    ## Hyperparameter
    parser.add_argument("--n_estimators",type=int,default=100)
    parser.add_argument("--random_state",type=int,default=0)

    ### Data,model,and output directories
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))
    parser.add_argument("--train-file", type=str, default="train-V-1.csv")
    parser.add_argument("--test-file", type=str, default="test-V-1.csv")

    args, _ =parser.parse_known_args()

    print("SKLearn Version: ", sklearn.__version__)
    print("Joblib Version: ", joblib.__version__)

    print("[INFO] Reading data")
    print()
    train_df = pd.read_csv(os.path.join(args.train, args.train_file))
    test_df = pd.read_csv(os.path.join(args.test, args.test_file))

    features = list(train_df.columns)
    label = features.pop(-1)

    print("Building training and testing datasets")
    print()
    X_train = train_df[features]
    X_test = test_df[features]
    y_train = train_df[label]
    y_test = test_df[label]

    print('Column order: ')
    print(features)
    print()

    print("Label column is: ",label)
    print()

    print("Data Shape: ")
    print()
    print("---- SHAPE OF TRAINING DATA (85%) ----")
    print(X_train.shape)
    print(y_train.shape)
    print()
    print("---- SHAPE OF TESTING DATA (15%) ----")
    print(X_test.shape)
    print(y_test.shape)
    print()


    print("Training RandomForest Model ....")
    print()
    model=RandomForestClassifier(n_estimators=args.n_estimators,random_state=args.random_state,
                                 verbose=2,n_jobs=1)

    model.fit(X_train,y_train)

    print()

    model_path=os.path.join(args.model_dir,"model.joblib")
    joblib.dump(model,model_path)

    print("Model saved at" + model_path)

    y_pred_test = model.predict(X_test)
    test_acc = accuracy_score(y_test,y_pred_test)
    test_rep = classification_report(y_test,y_pred_test)

    print()
    print("---- METRICS RESULTS FOR TESTING DATA ----")
    print()
    print("Total Rows are: ", X_test.shape[0])
    print('[TESTING] Model Accuracy is: ', test_acc)
    print('[TESTING] Testing Report: ')
    print(test_rep)




"""### AWS Sagemaker Entry Point To Execute the Training script"""

from sagemaker.sklearn.estimator import SKLearn

FRAMEWORK_VERSION="0.23-1"

sklearn_estimator=SKLearn(
    entry_point="script.py",
    role="arn:aws:iam::788614365622:role/sagemakeraccess",
    instance_count=1,
    instance_type="ml.m5.large",
    framework_version=FRAMEWORK_VERSION,
    base_job_name="RF-custom-sklearn",
    hyperparameters={
        "n_estimators":100,
        "random_state":0
    },
    use_spot_instance=True,
    max_run=3600

)

# launch training job, with asynchronous call
sklearn_estimator.fit({"train": trainpath, "test": testpath}, wait=True)

"""### To get the model from S3"""

sklearn_estimator.latest_training_job.wait(logs="None")
artifact = sm_boto3.describe_training_job(
    TrainingJobName=sklearn_estimator.latest_training_job.name
)["ModelArtifacts"]["S3ModelArtifacts"]

artifact

"""### Deploy the Model For Endpoint"""

from sagemaker.sklearn.model import SKLearnModel
from time import gmtime,strftime


model_name="Custom-sklearn-model-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
model=SKLearnModel(
    name=model_name,
    model_data=artifact,
    role="arn:aws:iam::788614365622:role/sagemakeraccess",
    entry_point="script.py",
    framework_version=FRAMEWORK_VERSION
)

model

## Endpoint deployment
endpoint_name="Custom-sklearn-model-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
print("EndpointName={}".format(endpoint_name))

predictor=model.deploy(
    initial_instance_count=1,
    instance_type="ml.m4.xlarge",
    endpoint_name=endpoint_name

)

predictor

testX[features][0:2]



print(predictor.predict(testX[features][:2].values.tolist()))

sm_boto3.delete_endpoint(EndpointName=endpoint_name)

