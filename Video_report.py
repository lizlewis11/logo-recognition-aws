############################
# This file contains code to detect logos in video and visualize the output
# Specify the video path, model as per your aws configuration
############################

import os
import boto3
import time
import argparse
import json
import cv2
import math

#visualization
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def upload_images_S3(input_dir):
    client = boto3.client('s3')

    for file in os.listdir(input_dir):
        if file.endswith(".jpg" or ".png" or ".jpeg"):
            output_file = "Video_Test/"+file
            try:
                client.upload_file(input_dir+file,'bclogobucket',output_file)
            except Exception as e:
                print(e)


def visualize_report(json_path):
    video_df = pd.read_json(json_path)

    sns.set_theme(style="darkgrid")
    print(video_df)

    plt.figure(figsize=(12, 4))

    # logonames versus visibility count
    logo_names = []

    df_value_counts = video_df.value_counts(['Name'])
    df_value_counts.reset_index()
    df_value_counts_index = df_value_counts.index.to_numpy()
    df_value_counts_index.tolist()
    df_value_counts = df_value_counts.tolist()

    for val in df_value_counts_index:
        str = ''.join(val)
        logo_names.append(str)

    g = sns.barplot(x=df_value_counts, y=logo_names)

    for patch in g.patches:
        x_val = int(patch.get_width())
        const = patch.get_height() / 2
        x = patch.get_x() + patch.get_width() + const
        y = patch.get_y() + const
        g.annotate(x_val, (x, y), ha='center')

    sns.set_palette('Set2')
    g.set_title("Distribution of visible logos")
    g.set_ylabel('Brand Logos')
    g.set_xlabel('Count')
    plt.savefig('Logo_Distribution')
    plt.show()
    dict = {'Count': df_value_counts, 'Names': logo_names}
    df = pd.DataFrame(dict)
    df.to_csv('Barplot.csv')

    # logonames versus screen area
    df_area = video_df.groupby('Name')['BBArea'].agg('sum')
    df_area = df_area * 100
    df_area = df_area.reset_index()
    df_area.columns = ['Name', 'Sum']
    df_area.sort_values(by='Sum', ascending=True, inplace=True)
    threshold = 10

    fig1, ax1 = plt.subplots()
    p = ax1.pie('Sum', labels='Name', data=df_area, autopct='%1.1f%%', startangle=0, shadow=True)
    # sns.barplot(x='Sum', y='Name',data=df_area)
    ax1.axis('equal')
    ax1.set_title('On screen brand visibility area')

    plt.savefig('Logo_Area')
    plt.show()
    dg = pd.DataFrame(df_area)
    dg.to_csv('pie_chart.csv')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v","--vid",help="path of video containing logos")
    args = vars(ap.parse_args())
    input_dir = str(args["vid"])
    start_time = time.perf_counter()

    #if images need to be uploaded on S3
    #upload_images_S3(input_dir)

    client = boto3.client('rekognition')
    model = 'arn:aws:rekognition:us-east-1:836696572753:project/IPL_logo/version/IPL_logo.2021-03-22T15.37.44/1616407665444'
    min_confidence = 70
    logos_detected = []

    cap = cv2.VideoCapture(input_dir)
    frameWidth = cap.get(3)
    frameHeight = cap.get(4)
    frameArea = frameWidth * frameHeight
    frameRate = cap.get(5)
    while cap.isOpened():
        frameID = cap.get(1)

        ret, frame = cap.read()
        if not ret:
            break
        if frameID % (math.floor(frameRate)) == 0:
            hasFrame, imageBytes = cv2.imencode(".jpg", frame)

            if hasFrame:
                start_time_inner = time.perf_counter()
                response = client.detect_custom_labels(Image= {'Bytes':imageBytes.tobytes()},
                                                       MinConfidence=min_confidence,
                                                       ProjectVersionArn=model)
                end_time_inner = time.perf_counter()
                elapsed_time_inner = end_time_inner - start_time_inner
                print("Time in inner secs:", elapsed_time_inner)

                for label in response["CustomLabels"]:
                    label["Timestamp"] = (frameID/frameRate)*1000
                    W = label["Geometry"]["BoundingBox"]["Width"]
                    H = label["Geometry"]["BoundingBox"]["Height"]

                    label["BBArea"] = W * H
                    logos_detected.append(label)

    stop_time = time.perf_counter()
    elapsed_time = stop_time - start_time
    print("Time in secs:", elapsed_time)

    videoFile = input_dir.split(".")[-2]
    with open(videoFile + ".json", "w") as f:
        f.write(json.dumps(logos_detected)) #stored in json_path
    cap.release()

    json_path = "C:\\VID_20210407_154015_over94_95_96.json"
    visualize_report(json_path)


if __name__ == "__main__":
    main()
