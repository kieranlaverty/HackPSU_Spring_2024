import tensorflow as tf 
import cv2 as cv
import random
import os
import numpy as np
import keras
from keras import layers


Datadirectory = "train/"
#[angry, disgust, fear, happy, neutral, sad, surprise]
Classes = ["0","1","2","3","4","5","6"]
img_size = 224
training_Data = []

def create_training_Data():
    for category in Classes:
        path = os.path.join(Datadirectory, category)
        class_num = Classes.index(category)
        for img in os.listdir(path):
            try:
                img_array = cv.imread(os.path.join(path, img))
                new_array = cv.resize(img_array, (img_size, img_size))
                training_Data.append([new_array, class_num])
            except Exception as e:
                pass


    
def main():
    
    #gathering and preparing the training data
    create_training_Data()

    #shuffle the data
    random.shuffle(training_Data)

    #create an x and y list
    X = []
    Y = []

    #for each item in the training_data
    for features, label in training_Data:

        #add the feature to X
        np.append(X,features)

        #add the label to Y
        np.append(Y,label)

        #resize the image
        X = np.array(X).reshape(-1, img_size, img_size, 3) 

    #normalize the data
    X = X / 255.0

    #take a model with pretrained weights
    model = keras.applications.MobileNetV2()

    #remaking the base inputs and outputs
    base_input = model.layers[0].input
    base_output = model.layers[-2].output

    #creating the layers of the CNN
    final_output = layers.Dense(128)(base_output) 
    final_output = layers.Activation("relu")(final_output) 
    final_output = layers.Dense(64)(final_output)
    final_output = layers.Activation("relu")(final_output)
    final_output = layers.Dense(7, activation="softmax")(final_output)

    #this will be the model final model
    new_model = keras.Model(input = base_input, outputs = final_output)


    new_model.compile(loss="sparse_categorical_crossentropy", optimizer = "adam", metrics = ["accuracy"])
    
    new_model.fit(X,Y, epochs = 30)

    new_model.save("emotion.h5")

if __name__ == "__main__":
    main()