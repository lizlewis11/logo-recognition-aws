# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

############################
# This file contains code to start the aws model
# Specify the project_arn, model_arn, version_name as per your aws configuration
############################

import boto3

def start_model(project_arn, model_arn, version_name, min_inference_units):
    client = boto3.client('rekognition')

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response = client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        # Get the running status
        describe_response = client.describe_project_versions(ProjectArn=project_arn,
                                                             VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
    except Exception as e:
        print(e)

    print('Done...')


def main():
    project_arn = 'arn:aws:rekognition:us-east-1:836696572753:project/IPL_logo/1616239881067'
    model_arn = 'arn:aws:rekognition:us-east-1:836696572753:project/IPL_logo/version/IPL_logo.2021-03-22T15.37.44/1616407665444'
    min_inference_units = 1
    version_name = 'IPL_logo.2021-03-22T15.37.44'
    start_model(project_arn, model_arn, version_name, min_inference_units)


if __name__ == "__main__":
    main()