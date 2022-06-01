############################
# This file contains code to create aws manifest file from an existing annotations file
# Download flickr_logos_27_dataset and specify its path
# Also, modify the images, label and manifest path as per your aws configuration
############################

import json
import cv2
import os

# Specify the path names of existing dataset
classlabels_file =  "C:\\flickr_logos_27_dataset\\obj.names"
annotations_file = "C:\\flickr_logos_27_dataset\\flickr_logos_27_dataset_training_set_annotation.txt"
image_basepath = "C:\\flickr_logos_27_dataset\\flickr_logos_27_dataset_images\\"

s3_bucket = ""
aws_s3url_images = "s3://bclogobucket/flickr_logos_27_dataset_images/"
aws_s3url_manifest = "s3://bclogobucket/manifests/"
aws_s3url_label = "s3://bclogobucket/custom-labels/"

#dict containing all images
dict_images = {}
label_attribute ='bounding-box'

dict_objnames = {}

if os.path.exists("custom_labels.manifest"):
    os.remove("custom_labels.manifest")

with open(classlabels_file,"r") as readclasslabels_file:
    count = 1
    for objline in readclasslabels_file:
        class_label = objline.strip()
        dict_objnames[class_label] = count
        count = count + 1

#print(dict_objnames)

with open(annotations_file,"r") as read_file:
    for line in read_file:
        image_name,label,id,startx,starty,endx,endy = line.strip().split(None)

        image_path = image_basepath + image_name
        #need image size
        image = cv2.imread(image_path)
        height,width,channels = image.shape

        dict_manifestformat = {}
        dict_manifestformat['source-ref'] = aws_s3url_images + image_name

        dict_imagesize = {}
        dict_imagesize['width'] = width
        dict_imagesize['height'] = height
        dict_imagesize['depth'] = channels
        dict_manifestformat['bounding-box'] = {'image_size': [dict_imagesize]}

        classlabel_id = dict_objnames[label]

        dict_annotations = {}
        dict_annotations['class_id'] = int(classlabel_id)
        dict_annotations['top'] = int(starty)
        dict_annotations['left'] = int(startx)
        dict_annotations['width'] = int(endx) - int(startx)
        dict_annotations['height'] = int(endy) - int(starty)

        if image_name in dict_images:
            dict_image = dict_images[image_name]
            list_annotate = dict_image[label_attribute]['annotations']
            list_annotate.append(dict_annotations)
            cl_object = {}
            cl_object['confidence'] = int(1)
            list_objects = dict_image[label_attribute + '-metadata']['objects']
            list_objects.append(cl_object)
            dict_image[label_attribute + '-metadata']['class-map'][classlabel_id] = label
        else:
            list_annotate = []
            list_annotate.append(dict_annotations)
            dict_manifestformat['bounding-box']['annotations'] = list_annotate

            cl_object = {}
            cl_object['confidence'] = int(1)
            dict_metadata = {}
            list_objects = []
            list_objects.append(cl_object)
            dict_metadata['objects'] = list_objects

            dict_metadata['class-map'] = {}
            dict_metadata['class-map'][classlabel_id] = label

            dict_metadata['type'] = 'groundtruth/object-detection'
            dict_metadata['human-annotated'] = 'yes'
            dict_metadata['creation-date'] = '2018-10-18T22:18:13.527256'
            dict_metadata['job-name'] = 'my job'
            dict_manifestformat['bounding-box-metadata'] = dict_metadata
            dict_images[image_name] = dict_manifestformat


for im in dict_images.values():

    with open("custom_labels.manifest", "a+") as write_file:
        json.dump(im, write_file)
        write_file.write('\n')
        write_file.close()

#s3 = boto3.resource('s3')
#s3.Bucket(aws_s3url_manifest).upload_file("custom_labels.manifest", "custom_labels.manifest")