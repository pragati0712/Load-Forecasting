# -*- coding: utf-8 -*-
"""Untitled

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TacAQgiQ4fEZGQ2sI8dCaioWa6MA2xF4
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x

import tensorflow as tf

tf.__version__

ls

cd drive

cd My Drive

! mkdir LoadForecast

cd ..

cd Electricity-Demand-Prediction-through-Neural-Network

cd Data

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow.python.framework import ops
import math



X_train1 = np.loadtxt('X_train1.txt', dtype=float)
X_train2 = np.loadtxt('X_train2.txt', dtype=float)
X_val1 = np.loadtxt('X_val1.txt', dtype=float)
X_val2 = np.loadtxt('X_val2.txt', dtype=float)
X_test1 = np.loadtxt('X_test1.txt', dtype=float)
X_test2 = np.loadtxt('X_test2.txt', dtype=float)
y_train = np.loadtxt("y_train.txt", dtype=float)
y_val = np.loadtxt("y_val.txt", dtype=float)
y_test = np.loadtxt("y_test.txt", dtype=float)

# Converting W to kW

y_train/=1000
y_test/=1000
y_val/=1000

X_train1.T.shape, y_train[np.newaxis].shape

X_train = np.concatenate((X_train1, X_train2), axis=1)
X_val = np.concatenate((X_val1, X_val2), axis=1)

X_train = X_train.T
X_val = X_val.T

y_train=y_train[np.newaxis]
y_val=y_val[np.newaxis]

X_train.shape, X_val.shape, y_train.shape, y_val.shape

def create_placeholders(n_x, n_y):
    X = tf.placeholder(shape=[n_x, None], dtype=tf.float32)
    Y = tf.placeholder(shape=[n_y, None], dtype=tf.float32)
    return X, Y

X, Y = create_placeholders(12288, 6)
print ("X = " + str(X))
print ("Y = " + str(Y))

def initialize_parameters(n_x, n_y, layers=4, layers_dim=[512, 512, 512, 1]):
    
    tf.set_random_seed(1)
    parameters={}
    for l in range(layers):
        if l == 0:
            parameters["W"+str(l+1)] = tf.get_variable("W"+str(l+1), [layers_dim[l], n_x], initializer=tf.contrib.layers.xavier_initializer(seed = 1))
            parameters["b"+str(l+1)] = tf.get_variable("b"+str(l+1), [layers_dim[l], 1], initializer=tf.zeros_initializer())
        else:
            parameters["W"+str(l+1)] = tf.get_variable("W"+str(l+1), [layers_dim[l], layers_dim[l-1]], initializer=tf.contrib.layers.xavier_initializer(seed = 1))
            parameters["b"+str(l+1)] = tf.get_variable("b"+str(l+1), [layers_dim[l], 1], initializer=tf.zeros_initializer())
    
    return parameters

tf.reset_default_graph()
with tf.Session() as sess:
    parameters = initialize_parameters(12288, 6)
    print("W1 = " + str(parameters["W1"]))
    print("b1 = " + str(parameters["b1"]))
    print("W2 = " + str(parameters["W2"]))
    print("b2 = " + str(parameters["b2"]))
    print("W3 = " + str(parameters["W3"]))
    print("b3 = " + str(parameters["b3"]))
    print("W4 = " + str(parameters["W4"]))
    print("b4 = " + str(parameters["b4"]))

def forward_propagation(X, parameters, activation_types=["relu","relu","relu","relu"]):
    mul = {}
    L = int(len(parameters)/2)
    for l in range(L):
        if l == 0:
            mul["Z"+str(l+1)] = parameters["W"+str(l+1)] @ X + parameters["b"+str(l+1)]
        else:
            mul["Z"+str(l+1)] = parameters["W"+str(l+1)] @ mul["A"+str(l)] + parameters["b"+str(l+1)]
        if activation_types[l] == "relu":
            mul["A"+str(l+1)] = tf.nn.relu(mul["Z"+str(l+1)])
        elif activation_types[l] == "sigmoid":
            mul["A"+str(l+1)] = tf.nn.sigmoid(mul["Z"+str(l+1)])
        else:
            mul["A"+str(l+1)] = mul["Z"+str(l+1)]
        
    return mul["A"+str(int(len(parameters)/2))]

def compute_cost(AL, Y, cost_type="mse"):
#     m = Y.shape[0]
    cost = tf.reduce_mean((AL-Y)**2)
    return cost

def random_minibatches(X, Y, mini_batch_size=64, seed=1):
    np.random.seed(seed)            # To make your "random" minibatches the same as ours
    m = X.shape[1]                  # number of training examples
    mini_batches = []
        
    # Step 1: Shuffle (X, Y)
    permutation = list(np.random.permutation(m))
    shuffled_X = X[:, permutation]
    shuffled_Y = Y[:, permutation].reshape((1,m))

    # Step 2: Partition (shuffled_X, shuffled_Y). Minus the end case.
    num_complete_minibatches = math.floor(m/mini_batch_size) # number of mini batches of size mini_batch_size in your partitionning
    for k in range(0, num_complete_minibatches):
        ### START CODE HERE ### (approx. 2 lines)
        mini_batch_X = shuffled_X[:, k*mini_batch_size: (k+1)*mini_batch_size]
        mini_batch_Y = shuffled_Y[:, k*mini_batch_size: (k+1)*mini_batch_size]
        ### END CODE HERE ###
        mini_batch = (mini_batch_X, mini_batch_Y)
        mini_batches.append(mini_batch)
    
    # Handling the end case (last mini-batch < mini_batch_size)
    if m % mini_batch_size != 0:
        mini_batch_X = shuffled_X[:, num_complete_minibatches:]
        mini_batch_Y = shuffled_Y[:, num_complete_minibatches:]
        mini_batch = (mini_batch_X, mini_batch_Y)
        mini_batches.append(mini_batch)
    
    return mini_batches

def model(X_train, Y_train, X_test, Y_test, learning_rate=0.001, num_epochs=200, print_cost=True, mini_batch_size=64):
    ops.reset_default_graph()
#     tf.set_random_seed(1)
    (n_x, m) = X_train.shape
    n_y = Y_train.shape[0]
    costs=[]
    
    X, Y = create_placeholders(n_x, n_y)
    
    parameters = initialize_parameters(n_x, n_y)
    
    AL = forward_propagation(X, parameters)
    
    cost = compute_cost(AL, Y)
    
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
    
    init = tf.global_variables_initializer()
    
    with tf.Session() as sess:
        sess.run(init)
        for epoch in range(num_epochs):
            epoch_cost = 0.
            num_minibatches = m/mini_batch_size
            minibatches = random_minibatches(X_train, Y_train)
            for minibatch in minibatches:
                minibatch_X, minibatch_Y = minibatch
                _, minibatch_cost = sess.run((optimizer, cost), feed_dict={X:minibatch_X, Y:minibatch_Y})
                epoch_cost += minibatch_cost/num_minibatches
                
            if print_cost == True:
                if epoch%50==0:
                    costs.append(epoch_cost)
                    if epoch%50==0:
                        print("Cost after epoch %i: %f" % (epoch, epoch_cost))
                        
        parameters = sess.run(parameters)
        accuracy = tf.reduce_mean(1-AL/Y)

        print("Train accuracy: ", accuracy.eval({X: X_train, Y: Y_train}))
        print("Test accuracy: ", accuracy.eval({X: X_test, Y: Y_test}))
    
    return parameters

parameters = model(X_train, y_train, X_val, y_val)

X_test = np.concatenate((X_test1, X_test2), axis=1)
X_test = X_test.T
y_test=y_test.reshape(1, -1)

with tf.Session() as sess:
    X, Y = create_placeholders(200, 1)
    AL = forward_propagation(X, parameters)
#     print(tf.Variable(AL, validate_shape=False).eval())
#     pred = tf.reduce_uniform(AL)
#     print(pred)
    pred = (AL.eval({X: X_test}))
    accuracy = tf.reduce_mean(tf.abs(1-AL/Y))
    mse_test = tf.reduce_mean((AL-Y)**2).eval({X: X_test, Y: y_test})
    mse_train = tf.reduce_mean((AL-Y)**2).eval({X: X_train, Y: y_train})
    mse_val = tf.reduce_mean((AL-Y)**2).eval({X: X_val, Y: y_val})
    print("Train accuracy: ", (1-accuracy.eval({X: X_train, Y: y_train}))*100,"%")
    print("Validation accuracy: ", (1-accuracy.eval({X: X_val, Y: y_val}))*100,"%")
    print("Test accuracy: ", (1-accuracy.eval({X: X_test, Y: y_test}))*100,"%")

print('Train MSE:', mse_train)
print('Val MSE:', mse_val)
print('Test MSE:', mse_test)

def plot(x,y,x_label=None,y_label=None, title=None, style1=None, color1=None, label1=None, y2=None, label2=None, \
           style2=None, color2=None):
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plot1 = plt.scatter(x, y, color=color1)
    plot2, = plt.plot([(y_test).min(), (y_test).max()], [(y_test).min(), (y_test).max()], 'k--', lw=4)
    plt.legend([plot1], [label1, label2])
    plt.show()
    
plot(y_test, pred, 'Actual Load (kWh)', 'Predicted Load (kWh)',  'Simple Neural Network', \
       style1='.', color1='blue', label1='Predicted', y2=y_test, label2='Actual', \
       style2='--', color2='black')

