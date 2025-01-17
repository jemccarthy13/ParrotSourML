# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 08:46:39 2023
@author: ayaha

Runs multi-threaded RandomForest predictions to optimize the img_size parameter.
"""
import logging
import multiprocessing as mp
import time

import joblib
from tqdm import tqdm

import PSRandomForest as psrf
from PSLogger import psLog

psLog.setLevel(logging.INFO)

if __name__ == '__main__':
    # required conditional to avoid recursive multithreading

    psLog.info("Finding optimized parameters...")
    psLog.info("---------------")

    starttime = time.time()

    # initialize a thread pool equal to the number of cores available on
    # this machine
    pool = mp.Pool(mp.cpu_count(), maxtasksperchild=3)

    # Start with a error rate of 100%; if a RF instance beats this
    # they become the new best. If an img_size of -1 is the best result,
    # something went wrong
    least_error = 100
    best_img_size = -1

    # Create threads for different img_size values
    # for x in range (10,50) will go through img_size values between 10 and 49
    # and find the best number within that range
    results = [pool.apply_async(psrf.randomforest, args=([False, x]))
               for x in range(10, 25)]

    # Also try 14,15,16,19 as these have historically been the lowest error rates
    results.extend([pool.apply_async(
        psrf.randomforest, args=([False, x])) for x in [14, 15, 16, 19]])

    pool.close()

    # get the results after each thread has finished executing
    output = []
    for job in tqdm(results):
        output.append(job.get())

    # find the best img_size (lowest error rate)
    for x in output:
        if (x[2] < least_error):
            least_error = x[2]
            best_img_size = x[0]
            forest = x[3]

        # only in logLevel DEBUG, print all results
        psLog.debug("-----------")
        psLog.debug("Img size: %s", str(x[0]))
        psLog.debug("Error: %s", str(x[2]))
        psLog.debug("")
        psLog.debug("Img size: %s", str(x[1]))

    psLog.debug("Saving best forest model...")
    joblib.dump((forest, best_img_size), 'PSRandomForestSaved.jbl')
    psLog.debug("Model saved.")
    psLog.info("------------------------------")

    total_time = time.time() - starttime

    # Results:
    psLog.info("Best error rate: %s", least_error)
    psLog.info("Best img size: %s", best_img_size)
    psLog.info("Total time: %s", total_time)
