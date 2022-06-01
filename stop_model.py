# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

############################
# This file contains code to stop the aws model
# Specify the model_arn as per your aws configuration
############################

import boto3

def stop_model(model_arn):
    client = boto3.client('rekognition')

    print('Stopping model:' + model_arn)

    # Stop the model
    try:
        response = client.stop_project_version(ProjectVersionArn=model_arn)
        status = response['Status']
        print('Status: ' + status)
    except Exception as e:
        print(e)

    print('Done...')

def main():

    model_arn = 'arn:aws:rekognition:us-east-1:836696572753:project/IPL_logo/version/IPL_logo.2021-03-22T15.37.44/1616407665444'
    stop_model(model_arn)


if __name__ == "__main__":
    main() 