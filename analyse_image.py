#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

############################
# This file contains code to identify logos on an image which is stored in S3 bucket
# To run: analyse_image.py -i ferrari-logo-vs-porsche-logo.jpg
# Modify the model path, bucket and image path as per your aws configuration
############################

import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import time
import argparse

def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)
    i = 0

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            #fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
            draw.text((left,top), customLabel['Name'], fill='#00d400')

            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill='#00d400', width=5)

    imagename = "output_" + str(i) + ".jpg"
    image.save(imagename)
    i = i + 1
    image.show()

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')
    start_time = time.perf_counter()

    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    stop_time = time.perf_counter()
    elapsed_time = stop_time - start_time
    # For object detection use case, uncomment below code to display image.
    display_image(bucket,photo,response)
    print("Time in secs:",elapsed_time)
    return len(response['CustomLabels'])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i","--image",help="image name")
    args = vars(ap.parse_args())

    bucket='bclogobucket'
    photo='Test_images/' + str(args["image"])

    # Specify the model path as per your aws configuration
    model = 'arn:aws:rekognition:us-east-1:836696572753:project/IPL_logo/version/IPL_logo.2021-03-22T15.37.44/1616407665444'
    min_confidence=70

    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    print("Custom labels detected: " + str(label_count))

#analyse_image.py -i ferrari-logo-vs-porsche-logo.jpg
if __name__ == "__main__":
    main()
