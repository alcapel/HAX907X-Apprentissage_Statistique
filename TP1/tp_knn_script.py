"""Created some day.

@authors:  salmon, gramfort, vernade
"""

#%%
from functools import partial  # useful for weighted distances
import numpy as np
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn import metrics
from scipy import stats  # to use scipy.stats.mode
from sklearn import neighbors
from sklearn import datasets

from tp_knn_source import (rand_gauss, rand_bi_gauss, rand_tri_gauss,
                           rand_checkers, rand_clown, plot_2d, ErrorCurve,
                           frontiere, LOOCurve)


import seaborn as sns
from matplotlib import rc

plt.close('all')
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Computer Modern Roman']})
params = {'axes.labelsize': 12,
          'font.size': 16,
          'legend.fontsize': 16,
          'text.usetex': False,
          'figure.figsize': (8, 6)}
plt.rcParams.update(params)

sns.set_context("poster")
sns.set_palette("colorblind")
sns.set_style("white")

#%%
############################################################################
#     Data Generation: example
############################################################################

# Q1
np.random.seed(42)  # fix seed globally

n = 100
mu = [1., 1.]
sigma = [1., 1.]
rand_gauss(n, mu, sigma)

n1 = 20
n2 = 20
mu1 = [1., 1.]
mu2 = [-1., -1.]
sigma1 = [0.9, 0.9]
sigma2 = [0.9, 0.9]
X1, y1 = rand_bi_gauss(n1, n2, mu1, mu2, sigma1, sigma2)

n1 = 50
n2 = 50
n3 = 50
mu1 = [1., 1.]
mu2 = [-1., -1.]
mu3 = [1., -1.]
sigma1 = [0.9, 0.9]
sigma2 = [0.9, 0.9]
sigma3 = [0.9, 0.9]
X2, y2 = rand_tri_gauss(n1, n2, n3, mu1, mu2, mu3, sigma1, sigma2, sigma3)

n1 = 50
n2 = 50
sigma1 = 0.01
sigma2 = 0.1
X3, y3 = rand_clown(n1, n2, sigma1, sigma2)

n1 = 150
n2 = 150
sigma = 0.1
X4, y4 = rand_checkers(n1, n2, sigma)

#%%
############################################################################
#     Displaying labeled data
############################################################################

plt.show()
plt.close("all")
plt.ion()
plt.figure(figsize=(15, 5))
plt.subplot(141)
plt.title('Bi-gauss data set')
plot_2d(X1, y1)

plt.subplot(142)
plt.title('Tri-gauss data set')
plot_2d(X2, y2)

plt.subplot(143)
plt.title('Clown data set')
plot_2d(X3, y3)

plt.subplot(144)
plt.title('Checkers data set')
plot_2d(X4, y4)

plt.savefig("./plot/visu_data.png")
#%%
############################################################################
#     K-NN
############################################################################

# Q2 : Write your own implementation


class KNNClassifier(BaseEstimator, ClassifierMixin):
    """Home made KNN Classifier class."""

    def __init__(self, n_neighbors=1):
        self.n_neighbors = n_neighbors

    def fit(self, X, y):
        self.X_ = X
        self.y_ = y
        return self

    def predict(self, X):
        n_samples, n_features = X.shape
        # TODO: Compute all pairwise distances between X and self.X_ using e.g. metrics.pairwise.pairwise_distances
        dist = np.sum((X[:,np.newaxis,:]-self.X_[np.newaxis,:,:])**2, axis=-1)
        # Get indices to sort them
        idx_sort = np.argsort(dist, axis=1)
        # Get indices of neighbors
        idx_neighbors = idx_sort[:,:self.n_neighbors]
        # Get labels of neighbors
        y_neighbors = self.y_[idx_neighbors]
        # Find the predicted labels y for each entry in X
        # You can use the scipy.stats.mode function
        mode, _ = stats.mode(y_neighbors, axis=1)
        # the following might be needed for dimensionality
        y_pred = np.asarray(mode.ravel(), dtype=np.intp)
        return y_pred

# TODO : compare your implementation with scikit-learn

# Focus on dataset 2 for instance
X_train = X2[::2]
Y_train = y2[::2].astype(int)
X_test = X2[1::2]
Y_test = y2[1::2].astype(int)

#%% TODO: use KNeighborsClassifier vs. KNNClassifier
# KNNClassifier
model = KNNClassifier(n_neighbors=10)
model.fit(X_train, Y_train)
Y_pred = model.predict(X_test)
acc_model = metrics.accuracy_score(Y_test, Y_pred)

# KneighborsClassifier
knn = neighbors.KNeighborsClassifier(n_neighbors=10)
knn.fit(X_train, Y_train)
Y_pred2 = knn.predict(X_test)
acc_knn = metrics.accuracy_score(Y_test, Y_pred2)

print("Accuracy KNN : ", acc_knn, " et  Accuracy model : ", acc_model)
#%%
# Q3 : test now all datasets
# From now on use the Scikit-Learn implementation

n_neighbors = 5  # the k in k-NN
knn = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors)

# for data in [data1, data2, data3, data4]:
for X, y in [(X1, y1), (X2, y2), (X3, y3), (X4, y4)]:
    knn.fit(X, y)
    plt.figure()
    plot_2d(X, y)
    n_labels = np.unique(y).shape[0]
    frontiere(knn, X, y, w=None, step=50, alpha_choice=1,
              n_labels=n_labels, n_neighbors=n_neighbors)
    plt.draw()


#%%
# Q4: Display the result when varying the value of K

plt.figure(figsize=(12, 8))
plt.subplot(3, 5, 3)
plot_2d(X_train, Y_train)
plt.xlabel('Samples')
ax = plt.gca()
ax.get_yaxis().set_ticks([])
ax.get_xaxis().set_ticks([])

for n_neighbors in range(1, 11):
    # TODO : fit the knn
    knn = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, Y_train)
    plt.subplot(3, 5, 5 + n_neighbors)
    plt.xlabel('KNN with k=%d' % n_neighbors)

    n_labels = np.unique(y).shape[0]
    frontiere(knn, X, y, w=None, step=50, alpha_choice=1,
              n_labels=n_labels, colorbar=False, samples=False,
              n_neighbors=n_neighbors)

plt.draw()  # update plot
plt.tight_layout()
plt.savefig("./plot/visu_diffk.png")

#%%
plt.figure(figsize=(12, 8))
plt.title('KNN with extrem values of k')
ax = plt.gca()
ax.get_yaxis().set_ticks([])
ax.get_xaxis().set_ticks([])
j=1
for n_neighbors in [1,len(X_train)]:
    knn = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, Y_train)
    plt.subplot(1, 2,j)
    plt.xlabel('KNN with k=%d' % n_neighbors)

    n_labels = np.unique(y).shape[0]
    frontiere(knn, X, y, w=None, step=50, alpha_choice=1,
              n_labels=n_labels, colorbar=False, samples=False,
              n_neighbors=n_neighbors)
    j+=1

plt.draw()  # update plot
plt.tight_layout()

#%%
# Q5 : Scores on train data
knn = neighbors.KNeighborsClassifier(n_neighbors=1)
knn.fit(X_train, Y_train)
Y_app = knn.predict(X_train)
print(metrics.accuracy_score(Y_train, Y_app))

Y_pred = knn.predict(X_test)
print(metrics.accuracy_score(Y_test, Y_pred))

#%%
# Q6 : Scores on left out data

n1 = n2 = 250
sigma = 0.1
data4, rep4 = rand_checkers(2 * n1, 2 * n2, sigma)

X_train = data4[::2]
Y_train = rep4[::2].astype(int)
X_test = data4[1::2]
Y_test = rep4[1::2].astype(int)

error = ErrorCurve(k_range=list(range(1,50)))

error.fit_curve(X_train, Y_train, X_test, Y_test)
print(np.argmin(error.errors))
error.plot()
plt.savefig("./plot/visu_error.png")
#%%
############################################################################
#     Digits data
############################################################################

# Q8 : test k-NN on digits dataset

# The digits dataset
digits = datasets.load_digits()

print(type(digits))
# A Bunch is a subclass of 'dict' (dictionary)
# help(dict)
# see also "http://docs.python.org/3/library/stdtypes.html#mapping-types-dict"


# plot some images to observe the data
plt.figure()
for index, (img, label) in enumerate(list(zip(digits.images, digits.target))[10:20]):
    plt.subplot(2, 5, index + 1)
    plt.axis('off')
    plt.imshow(img, cmap=plt.cm.gray_r, interpolation='None')
    plt.title('%i' % label)
plt.draw()

# Check that the dataset is balanced
plt.figure()
plt.hist(digits.target, density=True)
plt.title("Labels frequency over the whole dataset")
plt.ylabel("Frequency")
plt.draw()

#%%
n_samples = len(digits.data)

X_digits_train = digits.data[:n_samples // 2]
Y_digits_train = digits.target[:n_samples // 2]
X_digits_test = digits.data[n_samples // 2:]
Y_digits_test = digits.target[n_samples // 2:]

# Check that the test dataset is balanced
plt.figure()
plt.hist(Y_digits_test, density=True)
plt.title("Labels frequency on the test dataset")

score = np.zeros(10)
for k in range(1,50,5):
    knn = neighbors.KNeighborsClassifier(n_neighbors= k)
    knn.fit(X_digits_train, Y_digits_train)

    score[k//5] = knn.score(X_digits_test, Y_digits_test)
    Y_digits_pred = knn.predict(X_digits_test)
plt.figure()
plt.plot(list(range(1,50,5)), score)
plt.title("Précision sur les données de test")                                                              
plt.savefig("./plot/visu_accdigits.png")
#%%
# Q9 : Compute confusion matrix: use sklearn.metrics.confusion_matrix
knn = neighbors.KNeighborsClassifier(n_neighbors=3)
knn.fit(X_digits_train, Y_digits_train)
Y_digits_pred = knn.predict(X_digits_test)

# TODO : compute and show confusion matrix
mc = metrics.confusion_matrix(Y_digits_test, Y_digits_pred)
disp = metrics.ConfusionMatrixDisplay(mc)

disp.plot()
plt.show()
plt.savefig("./plot/visu_confmat.png")
#%%
# Q10 : Estimate k with cross-validation for instance

# Have a look at the class  'LOOCurve', defined in the source file.
plt.figure()
loo_curv = LOOCurve(k_range=list(range(1, 50, 1)))

loo_curv.fit_curve(digits.data, digits.target)
loo_curv.plot()
