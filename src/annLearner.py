################################################################################################

# Artificial Neural Network
# Created on 31st October

################################################################################################

import numpy as np
import os, csv
import math
import random
import itertools
import collections
import pickle
from sklearn import datasets
import BatchReader

################################################################################################

# Gobal Variables

LOW = -0.01
HIGH = 0.01
ERROR_LIMIT=0.004
BATCH_SIZE = 7

# Setting seed for random for consistent results
#random.seed(12345)

################################################################################################

# Classes

'''
    Neural Network class
    Parameters - 
    n_inputs = Number of network input signals
    n_outputs = Number of desired outputs from the network
    n_hidden_nodes = Number of nodes in each hidden layer
    n_hidden_layers = Number of hidden layers in the network
'''

class ArtificialNeuralNetwork():


    def __init__(self, n_inputs, n_outputs, n_hidden_nodes, n_hidden_layers):
        self.nIn = n_inputs                
        self.nOut = n_outputs              
        self.nHiddenNodes = n_hidden_nodes              
        self.nHiddenLayers = n_hidden_layers
        print self.nIn, self.nOut, self.nHiddenNodes, self.nHiddenLayers

        # Setting weights of different nodes to random values
        # n is number of weights required (+1 for bais terms)
        n = ( (self.nIn+1)*self.nHiddenNodes )+ ( ((self.nHiddenNodes+1)*self.nHiddenNodes)*(self.nHiddenLayers-1) ) + (self.nHiddenNodes+1)*self.nOut
        self.weight = []
        self.weightUpdate( [random.uniform(LOW, HIGH) for i in xrange(n)] )


    
    def weightUpdate(self, weightList):
        '''
        weightUpdate : 
        Parameter: weightList takes list of weights to update model weights for all nodes
        Creates a list of weight arrays for each layer. 
        Using this kind of structure of optimized forward and back pass implementation
        '''
        self.weight = []
        firstLayer = weightList[:((self.nIn+1)*self.nHiddenNodes)]
        #print firstLayer
        weightList = weightList[((self.nIn+1)*self.nHiddenNodes): ]
        self.weight.append( np.array(firstLayer).reshape((self.nIn+1), self.nHiddenNodes) )

        for i in range(1, self.nHiddenLayers):
            hiddenLayer = weightList[:((self.nHiddenNodes+1)*self.nHiddenNodes)]
            self.weight.append( np.array(hiddenLayer).reshape( (self.nHiddenNodes+1), self.nHiddenNodes) )
            weightList = weightList[((self.nHiddenNodes+1)*self.nHiddenNodes):]

        outputLayer = weightList
        self.weight.append( np.array(outputLayer).reshape((self.nHiddenNodes+1), self.nOut) )

        for layer, w in enumerate(self.weight):
            print 'layer: ', layer, 'w.shape: ', w.shape, 'np.max(w.T):', np.max(w.T)


    def biasTerm(self, input):
            # Add bias term of 1 at start of each data row
            n,m = input.shape
            return np.hstack(( np.ones(shape=[n,1]), input ))


    def sigmoid_function(self, x, derivative=False):
        # the activation function
        try:
            signal = 1/(1+math.e**(-x))
            
        except OverflowError:
            signal = float("inf")

        if derivative:
            # Return the partial derivation of the activation function
            return np.multiply(signal, 1-signal)
        else:
            # Return the activation signal
            return signal



    def backPropagation(self, trainX, trainY , alpha=0.3, momentum_factor=0.9  ):
        
        assert len(trainX[0]) == self.nIn, "ERROR: input size varies from the defined input setting"
        
        #trainX = np.array( trainX )
        #trainY = np.array( trainY )
        
        mse = float("inf")
        momentum = collections.defaultdict(int)
        #print "Calculating weights inside backPropagation method"
        i = 0
        # Gradient descent till we get error below ERROR_LIMIT
        while i<50000 and mse > ERROR_LIMIT:
            #print i

            index = np.random.randint(0, len(trainX), BATCH_SIZE)
            training_data = np.array([trainX[k] for k in index]).astype(np.float32)
            training_targets = np.array([trainY[k] for k in index]).astype(np.float32)
            '''
            training_targets = np.zeros(shape=(BATCH_SIZE, self.nOut)).astype(np.float32)
            for l, k in enumerate(index): training_targets[l,trainY[k]] = 1
            #print training_targets
            '''

            out = self.forwardPass(training_data)
            #print "Back in backPropagation method"
            #print 'out[-1][:,:-1].shape:', out[-1][:,:-1].shape, 'training_targets.shape:', training_targets.shape       
            error = training_targets - out[-1][:,1:] # output from last layer - also excluding first column (the bias term)
            #print "i: ", i, "error shape = ", error.shape, 'error:', error
            mse = np.mean( np.power(error,2) )
            delta = error

            # Iterate backwards on layer to update weights for each neuron
            for j in xrange((self.nHiddenLayers), -1, -1):
                #print 'j:', j
                w = self.weight[j]
                inp = out[j]
                print 'j:', j, "inp.T shape = ", inp.T.shape, "delta.shape =", delta.shape
                #print inp.T

                dW = alpha * np.dot(inp.T, delta) + momentum_factor * momentum[j]
                '''
                if j != self.nHiddenLayers:
                    dW = alpha * np.dot(inp.T, delta[:,1:]) + momentum_factor * momentum[j]
                else:
                    dW = alpha * np.dot(inp.T, delta) + momentum_factor * momentum[j]
                '''
                #print 'dW.shape:', dW.shape
                
                # Update the weights
                '''
                if j != self.nHiddenLayers:
                    print "self.weight[j].shape: ",self.weight[j].shape, 'dW.T[1:,:].shape: ', dW.T[1:,:].shape
                    self.weight[j] += dW.T[1:,:]

                else:
                    print "self.weight[j].shape: ",self.weight[j].shape, 'dW.T.shape: ', dW.T.shape
                    self.weight[j] += dW.T
                '''
                print "self.weight[j].shape: ",self.weight[j].shape, 'dW.T.shape: ', dW.T.shape
                self.weight[j] += dW
                #print dW.T

                # Calculate previous layer's delta for next calculation
                if j!= 0:
                    print "delta.shape:", delta.shape, "w.T.shape: ", w.T.shape
                    sig = np.dot( delta, w[1:,:].T )
                    delta = np.multiply( sig , self.sigmoid_function(inp[:,1:], derivative=True) )
                    print 'delta.shape: ', delta.shape
                
                # Store the momentum
                momentum[j] = dW
                 
            i += 1
            if i%1000==0:
                print "MSE: %g, iterations: %d" % (mse, i)
        
        print "Converged to error bound (%.4g) with MSE = %.4g." % ( ERROR_LIMIT, mse )
        print "Training ran for %d iterations." % i



    def forwardPass(self, inp_vec):
        # each entry of output list has 1 appended as bias term at 0th index
        #print "In Forward Pass"
        output = [ self.biasTerm(inp_vec) ]
        for w in self.weight:
            # Looping over network layers to calculate output
            #print "output[-1].shape: ",output[-1].shape, 'w.T.shape: ',w.T.shape 
            # print w[:,1:].T.shape
            o = np.dot( output[-1], w ) # adding bias term for each layer
            o = self.sigmoid_function(o)
            output.append( self.biasTerm(o) )
        #print len(output), output[0].shape
        #print 
        #for term in output: print term.shape
        return output


    def forwardPass1(self, inp_vec):
        # each entry of output list has 1 appended as bias term at 0th index
        #print "In Forward Pass"
        print "Start"
        output = [ self.biasTerm(inp_vec) ]
        for w in self.weight:
            # Looping over network layers to calculate output
            print "output[-1].shape: ",output[-1].shape, 'w.T.shape: ',w.T.shape 
            print 'output[-1]:', output[-1]
            print 'np.max(w.T):', np.max(w.T)
            o = np.dot( output[-1], w.T ) # adding bias term for each layer
            print 'o.shape:' , o.shape
            o = self.sigmoid_function(o)
            print 'o:',o 
            output.append( self.biasTerm(o) )
        #print len(output), output[0].shape
        
        #for term in output: print term
        print "Done"
        return output

    def dumpToFile(self):
        print "Dumping parameters to ../data/ann_parameters.pkl"
        dir = os.getcwd()
        path = os.path.join(dir,"..//data")
        os.chdir(path)

        with open( "ann_parameters.pkl" , 'wb') as file:
            dict = {
                "nIn" : self.nIn,
                "nOut" : self.nOut,
                "nHiddenNodes" : self.nHiddenNodes,
                "nHiddenLayers" : self.nHiddenLayers,
                "weight" : self.weight
            }
            pickle.dump(dict, file, 2 )
        os.chdir(dir)


    def loadFromMemory(self):
        dir = os.getcwd()
        path = os.path.join(dir,"..//data")
        os.chdir(path)

        if os.path.isfile("ann_parameters.pkl") :
            print "Reading parameters from ../data/ann_parameters.pkl"
            with open(ann_parameters.pkl , 'rb') as file:
                d = pickle.load(file)
                self.nIn = d["nIn"]            
                self.nOut = d["nOut"]           
                self.nHiddenNodes = d["nHiddenNodes"]           
                self.nHiddenLayers = d["nHiddenLayers"]     
                self.weight = d["weight"]
        os.chdir(dir)








if __name__=='__main__':

    #####################
    # Autoencoder
    #####################
    X = np.array([ [1,0,0,0,0,0,0,0], [0,1,0,0,0,0,0,0], [0,0,1,0,0,0,0,0], [0,0,0,1,0,0,0,0], [0,0,0,0,1,0,0,0], [0,0,0,0,0,1,0,0], [0,0,0,0,0,0,1,0], [0,0,0,0,0,0,0,1] ]).astype(np.float32)
    Y=X
    trainX = X[:-2,:]
    trainY = Y[:-2,:]

    testX = X[-2:,:]
    testY = Y[-2:,:]

    '''
    ######################
    # Boolean OR function
    ######################
    X = [[0,0, 0],[0,0, 1],[0,1, 0],[0,1, 1],[1,0, 0],[1,0, 1],[1,1, 0]]
    Y = [[0],[1],[1],[1],[1],[1],[1]]
    
    ######################
    # IRIS datasets
    ######################
    iris = datasets.load_digits()
    X = iris.data
    Y = iris.target
    n_inputs = X.shape[1]
    n_outputs = len(Y)
    print X
    print Y
    
    #####################
    # Actual Image data 
    #####################
    br = BatchReader.inputs()
    
    X, Y = br.getNPArray(2)
    trainX = X[1000:,:]
    trainY = Y[1000:,:]

    testX = X[1000:1008,:]
    testY = Y[1000:1008,:]
    '''
    print X.shape, Y.shape
    n_inputs = X.shape[1]
    
    n_outputs = Y.shape[1]
    n_hiddens = 3
    n_hidden_layers = 1

    # initialize the neural network
    network = ArtificialNeuralNetwork(n_inputs, n_outputs, n_hiddens, n_hidden_layers)

    # start training on test set one
    network.backPropagation(trainX, trainY, alpha=0.04, momentum_factor=0.9  )

    # save the trained network
    network.dumpToFile()
    '''
    # load a stored network configuration
    # network.loadFromMemory()
   # print [1,1,1], network.forwardPass(np.array([[1,1,1]]))[-1][:,1:]
    # print out the result

    '''

    predict = network.forwardPass(testX)[-1][0,1:]
    print np.argmax(predict), np.argmax(testY[0,:])


    predict = network.forwardPass(testX)[-1][1,1:]
    print np.argmax(predict), np.argmax(testY[1,:])

    count=0
    for i in range(testY.shape[0]):
        print np.argmax(predict[i]), predict[i], testY[i]
        if(np.argmax(testY[i]) != np.argmax(predict[i])): count += 1
    print "Testing error: ", count
