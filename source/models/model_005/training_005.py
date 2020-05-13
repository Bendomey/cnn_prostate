import keras
from sklearn.model_selection import train_test_split
import numpy as np

import sys
sys.path.append('../../')

# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("Loading training and testing data from disk...")

# Loading in the data
X = np.load("../../../data/X.npy")
y = np.load("../../../data/Y.npy")

#------------------------------------------------------------------------------------------------#

# Splitting the data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1/7)

print("Loading model from disk...")

# Loading the model
json_file = open("../../../data/models/model_005/model_005_init.json", "r")
loaded_json_file = json_file.read()
json_file.close()

with keras.utils.CustomObjectScope({'GlorotUniform': keras.initializers.glorot_uniform()}):
    model = keras.models.model_from_json(loaded_json_file)


model.load_weights("../../../data/models/model_005/model_005_init.h5")

print("Training...")

# Configure the training details, e.g. what optimiser to use
model.compile(loss = keras.losses.categorical_crossentropy,optimizer = keras.optimizers.Adadelta(),metrics = ['accuracy'])

non_cancer = np.count_nonzero(y_test[:, 0] == 1)
samples = y_test.shape[0]

epoch_num = 100

history = model.fit(X_train, y_train,class_weight = { 1: non_cancer / samples, 0: (samples - non_cancer) / samples },batch_size = 52,epochs = epoch_num)

print("Saving the model 005...")

# Serialise model to JSON
model_json = model.to_json()
with open("../../../data/models/model_005/model_005_trained.json", "w") as json_file:
    json_file.write(model_json)

# Serialise weights to HDF5
model.save_weights("../../../data/models/model_005/model_005_trained.h5")


# Evaluate the performance
performance = model.evaluate(X_test, y_test)
print(
'''
On Test Data:
Loss -> %.3f
Accuracy -> %.3f
'''
% tuple(performance))

y_pred = model.predict(X_test)
print("Prediction:\n", y_pred)
print("\nGround Truth:\nHas {}/{} FALSE labels\n".
    format(np.count_nonzero(y_test[:, 0] == 1), y_test.shape[0]),
    y_test)
metrics.confusion_matrix(y_pred, y_test) # Producing a confusion matrix
metrics.ROC(y_pred, y_test, 5)
metrics.plot_training(history, epoch_num, 5)
