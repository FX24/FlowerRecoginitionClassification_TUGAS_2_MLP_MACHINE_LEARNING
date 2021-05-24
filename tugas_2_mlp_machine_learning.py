# -*- coding: utf-8 -*-
"""Tugas 2 MLP - Machine Learning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bTLVeNI93mDsJzfL5qGY9EnE6H7ajK-Z
"""

import pandas as pd
import os
import random
import matplotlib.pyplot as plt
import numpy as np
import cv2
from sklearn import utils
from google.colab.patches import cv2_imshow

"""##Download Dataset From Kaggle"""

#Mount your GDrive

from google.colab import drive
drive.mount('/content/drive')

from google.colab import files
files.upload()

#Upload kaggle.json (Kaggle API Token)
#You can download it by create new API Token from your kaggle account

#Make sure kaggle.json file is present
!ls -lha kaggle.json

#Install kaggle API client
!pip install -q kaggle

#Download and unzip the dataset
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 /root/.kaggle/kaggle.json
!kaggle datasets download alxmamaev/flowers-recognition
!unzip flowers-recognition.zip

"""##1. Tentukan arsitektur MLP

###Ketentuan

* 1 hidden layer
* Jumlah neuron di input layer = jumlah keseluruhan pixel dalam image (320x240)

ARSITEKTUR :


*   Input layer dengan jumlah neuron 320 * 240 = 76800
*   Hidden layer dengan jumlah neuron = 160
* Output layer dengan jumlah neuron 3 ['sunflower', 'daisy', 'dandelion']

##2. Definisikan arsitektur yang digunakan
"""

input_unit = 76800
hidden_unit = 160
output_unit = 3

"""##3. Definisikan fungis Load dataset , Visualisasi Data, dan Split data"""

directory = r'/content/flowers/'
classes=['sunflower','daisy','dandelion']
def load_split_ds() :

  X_train=[]
  y_train=[]
  X_test=[]
  y_test=[]

  for i,class_name in enumerate(classes):
      path=os.path.join(directory,class_name)
      files=[filename for filename in os.listdir(path) if filename.endswith(".jpg")]
      random.shuffle(files)
      X_train+=files[:80]
      y_train+=([i]*80)
      X_test+=(files[80:100])
      y_test+=([i]*20)
  X_train,y_train=utils.shuffle(X_train,y_train)
  X_test,y_test=utils.shuffle(X_test,y_test)

  return X_train, y_train, X_test, y_test

X_train, y_train, X_test, y_test = load_split_ds()

for i in range (5) :
    image=cv2.imread(os.path.join(os.path.join(directory,classes[y_train[i]]),X_train[i]))
    image=cv2.resize(image,(240,320))/255.0

"""##4. Definisikan Greyscaling Image"""

def grayscale(X,y):
    #print(os.path.join(directory,classes[y]))
    image=cv2.imread(os.path.join(os.path.join(directory,classes[y]),X),cv2.IMREAD_GRAYSCALE)
    image=cv2.resize(image,(240,320))
    return image

cv2_imshow(grayscale(X_train[0],y_train[0]))

"""##5. Definisikan Fungsi Sigmoid"""

def sigmoid(x):
    # sigmoid function
    g = 1 / (1 + np.exp(-x))
    return g

"""##6. Definisikan Backpropagation - Inisialisasi bobot and bias

"""

def initialization(input_unit,hidden_unit,output_unit):
    W1=np.random.randn(hidden_unit, input_unit)*0.01
    b1 = np.zeros((hidden_unit, 1))
    W2 = np.random.randn(output_unit, hidden_unit)*0.01
    b2 = np.zeros((output_unit, 1))
    parameter = {"W1": W1, "b1": b1, "W2": W2, "b2": b2}
    return parameter

#Inisialisasi paramater yang telah kita tentukan
parameter=initialization(input_unit,hidden_unit,output_unit)

"""##7. Definisikan Backpropagation - menghitung error

"""

def error(A2,Y):
    """Cross entropy"""
    m=240
    cost=-np.sum(np.multiply(np.log(A2),Y)+np.multiply((1-Y),np.log(1-A2)))/m
    cost=float(np.squeeze(cost))
    return cost

"""##8. Definisikan Backpropagation - Feedforward

"""

def feedforward(X,parameter):
    X = X.reshape(input_unit,1)
    Z1 = np.dot(parameter['W1'], X) + parameter['b1']
    A1 = sigmoid(Z1)
    Z2 = np.dot(parameter['W2'], A1) + parameter['b2']
    A2 = sigmoid(Z2)
    return A2, A1

#testing
A2,A1 =feedforward(grayscale(X_train[0],y_train[0]).flatten(),parameter)
error(A2,y_train[0])
print(A2.shape)

"""##9. Definisikan Backpropagation - Backward (update bobot)"""

def update_weight(X, Y, parameter, lrate) :
  output_y, hidden_y = feedforward(X.flatten(),parameter)

  #reshape variable yang diperlukan (Perkalian terbalik)
  output_y = output_y.reshape(1, len(output_y))
  hidden_y = hidden_y.reshape(len(hidden_y), 1)
  X_transpose = X.reshape(len(X), 1)

  #update theta between HIDDEN-OUTPUT layer
  dv_hidden_output = (output_y - Y) * output_y * (1 - output_y)
  dt_hidden_output = np.dot(hidden_y, dv_hidden_output)

  oldparameter = parameter
  parameter['W2'] -= (lrate * dt_hidden_output.T)
  parameter['b2'] -= (lrate * dv_hidden_output[0].reshape(output_unit,1))

  #update theta between INPUT-HIDDEN layer
  dEtotal_hidden_output = np.dot(dv_hidden_output, oldparameter['W2'])
  dv_input_hidden = dEtotal_hidden_output*hidden_y.T * (1 - hidden_y.T)
  dt_input_hidden = np.dot(X_transpose,dv_input_hidden)

  parameter['W1'] -= lrate * dt_input_hidden.T
  parameter['b1'] -= lrate * dt_input_hidden[0].reshape(hidden_unit,1)

#Testing
X = grayscale(X_train[0],y_train[0]).flatten()
update_weight(X, y_train[0], parameter, 0.01)

"""##10. Definisikan Backpropagation - prediksi """

def predict(X,parameter):
  output, _ = feedforward(X, parameter)
  return np.argmax(output)

"""##11. Definisikan Backpropagation - akurasi """



def acuracy(parameter):
  count = 0
  for i in range (len(X_test)) :
    img = grayscale(X_test[i], y_test[i])
    if np.argmax(y_test[0]) == predict (img, parameter):
      count += 1
  
  return count/len(X_test)

#BUAT AKURASI SAMA PREDICT
#PARAMETERNYA DIBAWAH
#parameter=initialization(input_unit,hidden_unit,output_unit)

"""##12. Definisikan fungsi training (80% data) dan testing (20% data)"""

def train(parameter, epoch, lrate):
  print("Training model; epoch =", epoch, "; learning_rate =", lrate)
  errors = []
  accuracies = []
  for current_epoch in range(epoch):
    print("EPOCH", current_epoch)
    cur_error = 0
    for i in range(len(X_test)):
      img = grayscale(X_test[i], y_test[i]).flatten()
      output_1,output_2 = feedforward(img, parameter)
      cur_error += error(y_test[i], output_1)
      update_weight(img, y_test[i], parameter, lrate)
    errors.append((cur_error)/len(X_test))
    accuracies.append(acuracy(parameter))
  return errors, accuracies

"""##13. Visualisasikan error dan akurasi 

"""

def visualize(errors, accuracies):
  plt.plot(errors, 'r-')
  plt.plot(accuracies, 'b-')
  plt.show()

# percobaan epoch=50 dan learning rate=0,1
errors_0_1, accuracies_0_1 = train(parameter, 50, 0.1)
visualize(errors_0_1, accuracies_0_1)
 
# percobaan epoch=50 dan learning rate=0,8
errors_0_8, accuracies_0_8 = train(parameter, 50, 0.8)
visualize(errors_0_8, accuracies_0_8)

