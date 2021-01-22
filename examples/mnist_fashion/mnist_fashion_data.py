import torch
import torchvision

import numpy as np
import matplotlib.pyplot as plt
import random

import ml_tools as ml

#--------------------------------------------
# Access and define the FashionMNIST dataset
#--------------------------------------------

def load_FashionMNIST_data(verbose=1):
    '''
    Define the dataset we are going to use, included data transformers.
    Download the data if we haven't already.
    '''
    if verbose > 0:
        print('Loading FashionMNIST dataset...')
    train_dataset = torchvision.datasets.FashionMNIST(
        root='.',
        train=True,
        transform=torchvision.transforms.ToTensor(), # normalizes values to [0,1], as well as type/shape conversion
        download=True
    )
    test_dataset = torchvision.datasets.FashionMNIST(
        root='.',
        train=False,
        transform=torchvision.transforms.ToTensor(), # normalizes values to [0,1], as well as type/shape conversion
        download=True
    )
    # Define the mapping of target labels (0-9) onto more descriptive strings for MNIST Fashion
    label_dict = {0: 'T-shirt/top', 1: 'Trouser', 2: 'Pullover', 3: 'Dress', 4: 'Coat',
                  5: 'Sandal', 6: 'Shirt', 7: 'Sneaker', 8: 'Bag', 9: 'Ankle boot'}
    # Give use back some information about the dataset we've just loaded
    if verbose > 1:
        print('  Training data shape: {}'.format(train_dataset.data.shape))
        print('  Test data shape: {}'.format(test_dataset.data.shape))
        print('  Data min,max values: {},{}'.format(train_dataset.data.min(), train_dataset.data.max()))
        label_str = ', '.join(['{}:{}'.format(k,v) for k,v in label_dict.items()])
        print('  Data labels ({} categories): {}'.format(len(label_dict), label_str))
    return train_dataset, test_dataset, label_dict


#-------------------------------------------------------
# Define the data loaders we will use to train a model
#------------------------------------------------------

def get_dataloaders(train_dataset, test_dataset, batch_size=256):
    '''
    Create our data loaders.  Use batches for batch gradient descent so we aren't 
    trying to load all training images into memory at the same time!
    '''
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                               batch_size=batch_size,
                                               shuffle=True)
    test_loader = torch.utils.data.DataLoader(dataset=test_dataset,
                                              batch_size=batch_size,
                                              shuffle=False)
    return train_loader, test_loader
    

#--------------------------------------------
# Make a plot of some example training data
#--------------------------------------------

def display_example_data(train_dataset, label_dict, 
                         filename=None):
    '''
    Plot one example from each of the training data categories.
    Use this to confirm label assignments and to see what we are up against!
    '''
    fig = plt.figure(figsize=(16,8))
    axs = fig.subplots(2,5)
    for i,l in enumerate(list(label_dict.keys())):
        ind = list(train_dataset.targets).index(l)  # just get the first example for each label
        im = train_dataset.data[ind]
        # Show an example image
        axs[i//5,i%5].imshow(im.reshape([28,28]),cmap='gray')
        axs[i//5,i%5].set_title('Label={}: {}'.format(l,label_dict[l]))
    if filename:
        plt.savefig(filename)
    else:
        plt.show()
    return


#-------------------------------------------------
# Make a plot of examples with their predictions
#-------------------------------------------------

def display_pred_examples(example_indices, test_dataset, 
                          test_targets, test_predictions,
                          label_dict, 
                          filename=None):
    '''
    Given a set of indices for the objects we want to see examples of 
    (e.g., "correct" predictions or "wrong" predictions), plot a 
    set of images for inspection.
    '''
    fig = plt.figure(figsize=(15,15))
    axs = fig.subplots(4,4)
    for i in range(16):
        idx = random.sample(list(example_indices), 1)[0]
        im = test_dataset.data[idx]
        axs[i//4,i%4].imshow(im.reshape([28,28]),cmap='gray')
        axs[i//4,i%4].set_title('True={}   Pred={}'.format(label_dict[test_targets[idx]],
                                                           label_dict[test_predictions[idx]]),fontsize='small')
    if filename:
        plt.savefig(filename)
    else:
        plt.show()
    return

