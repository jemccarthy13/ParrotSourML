# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 08:46:39 2023
@author: ayaha

Defines a function to run a single RandomForest prediction with the coded img_size parameter.
"""
import logging
import os
import time

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from sklearn import metrics
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from ParrotSourPreProcessor import IMAGE_DIR, OUT_DIR
from PSLogger import psLog


def randomforest(img_size=30, n_estimators=240, use_pca=False, show_cm=False):
    """
    Run sklearn random forest model training and prediction.

    This function will take an output image, bin the pixels into img_size sized
    bins, and use sklearn's Random Forest to train and predict.

    Parameters
    ----------
    img_size : int (optional)
        The size (width & height) in which to bin the larger image
    n_estimators : int (optional)
        The number of trees in the forest
    use_pca : bool (optional)
        Whether or not to use PCA optimization
    show_cm : bool (optional)
        Whether or not to display the confusion matrix after running algorithm

    Returns
    ----------
    img_size : int 
        The image size used for binning images in this RF run
    elapsed_time : int
        How much time the algorithm took to run for this img_size
    error_rate : int 
        The rate of error in classifying the test data
    """

    start_time = time.time()
    pictures = []

    # read the output image directory to prep the dataset
    filelist = []
    for root, dirs, files in os.walk(IMAGE_DIR, topdown=True):

        for n in files:
            filelist.append(os.path.splitext(n)[0])
    sorted_files = sorted(filelist, key=int)

    # read the images for form the dataset
    for name in sorted_files:
        image = Image.open(os.path.join(root, name)+'.png')
        resized_image = image.resize((img_size, img_size))
        image_array = np.array(resized_image).flatten()
        pictures.append(image_array)

    # create the rf classifier
    baseestimator = RandomForestClassifier(n_estimators=n_estimators)

    # load the answer key and format the dataset
    Y = np.loadtxt(OUT_DIR+"\\Y.txt", dtype=str)
    X = np.asarray(pictures)

    # run optimization if specified
    if (use_pca):
        num_components = len(pictures) if len(pictures) < 7 else 7
        pca = PCA(n_components=num_components)
        X = pca.fit_transform(X)

    # train the model
    x_train, x_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.2, shuffle=False)
    baseestimator.fit(x_train, y_train)

    # predict based on test data
    predicted = baseestimator.predict(x_test)

    # Results:
    elapsed_time = time.time() - start_time

    error_rate = 1 - metrics.accuracy_score(y_test, predicted)

    psLog.debug("Time taken to classify: %s seconds", elapsed_time)
    psLog.debug(f"Classification error: {error_rate}")

    if show_cm:
        disp = metrics.ConfusionMatrixDisplay.from_predictions(
            y_test, predicted)
        disp.figure_.suptitle("Confusion Matrix")
        plt.show()

    return [img_size, elapsed_time, error_rate]