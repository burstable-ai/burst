import torch
import numpy as np
from datetime import datetime
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import itertools

#--------------------------------------------
# Training loop --- all NN are the same!
#--------------------------------------------

def train(train_loader, model, optimizer, criterion, 
          n_epochs=10, test_loader=None, device=None, 
          reshape_inp=None, reshape_targ=None,
          verbose=1, print_every=1):
    '''
    Train a Neural Net model (all data are the same!)
    '''
    
    if device is not None: model = model.to(device)

    t0 = datetime.now()
    if verbose: print('Training NN through {} epochs.  Start time: {}'.format(n_epochs, t0))
    train_losses, test_losses = [], []

    for e in range(n_epochs):
        t0 = datetime.now()
        train_loss = []

        for inputs, targets in train_loader:
            # move data to GPU (in batches!) and reshape
            if device is not None: inputs, targets = inputs.to(device), targets.to(device)
            if reshape_inp is not None:
                inputs = reshape_inp(inputs)
            if reshape_targ is not None:
                targets = reshape_targ(targets)

            # zero the parameter gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            train_loss.append(loss.item())  # store losses

            # Backward pass and optimize
            loss.backward()
            optimizer.step()

        # Average loss for this epoch
        train_losses.append(np.mean(train_loss))

        # Get test losses for tracking
        if test_loader is not None:
            test_loss = []
            for test_inp, test_targ in test_loader:
                if device is not None: test_inp, test_targ = test_inp.to(device), test_targ.to(device)
                if reshape_inp is not None:
                    test_inp = reshape_inp(test_inp)
                if reshape_targ is not None:
                    test_targ = reshape_targ(test_targ)
                test_out = model(test_inp)
                test_loss.append(criterion(test_out, test_targ).item())
            test_losses.append(np.mean(test_loss))

        if verbose and e % print_every == 0: 
            string = ' Iteration {:3d}, avg train_loss = {:2.3f}, '.format(e, np.mean(train_loss))
            if test_loader is not None:
                string += 'avg test_loss = {:2.3f},'.format(np.mean(test_loss))
            string += '1 epoch duration: {}'.format(datetime.now()-t0)
            print(string)
    if verbose: print(' Done training.')        

    return train_losses, test_losses
    
#--------------------------------------------
# Plot losses to an output file
#--------------------------------------------
    
def plot_losses(train_losses, test_losses, filename=None):
    fig = plt.figure(figsize=(7,7))    
    plt.plot(train_losses, label='train')
    plt.plot(test_losses, label='test')
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    if filename:
        plt.savefig(filename)
    else:
        plt.show()
    return
    
#--------------------------------------------
# Predict --- all NN are the same!
#--------------------------------------------

def predict(loader, model, 
            binaryclass=False, multiclass=False, 
            device=None,
            reshape_inp=None, reshape_targ=None):

    '''
    Iterate through the specified dataloader, apply the model, 
    and return the full set of predictions and targets
    '''
    
    if device is None: model.to(device)

    all_targets, all_predictions = [], []
    
    for inputs, targets in loader:
        if device is not None: inputs, targets = inputs.to(device), targets.to(device)
        if reshape_inp is not None:
            inputs = reshape_inp(inputs)
        if reshape_targ is not None:
            targets = reshape_targ(targets)
        outputs = model(inputs)
        if multiclass:
            max_values, predictions = torch.max(outputs, 1)
            max_values = max_values.cpu().detach().numpy()
            predictions = predictions.cpu().detach().numpy()
        elif binaryclass:
            predictions = outputs.detach().numpy().flatten() > 0
        else:
            predictions = outputs.detach().numpy().flatten()
        all_targets.extend(targets.cpu().numpy())
        all_predictions.extend(predictions)
        
    return all_predictions, all_targets

#--------------------------------------------
# Model accuracy
#--------------------------------------------

def get_accuracy(train_predictions, train_targets,
                 test_predictions, test_targets, verbose=1):
    '''
    * Compute and display model accuracies.
    '''
    train_acc = np.sum(np.array(train_predictions)==np.array(train_targets)) / len(train_targets)
    test_acc = np.sum(np.array(test_predictions)==np.array(test_targets)) / len(test_targets)
    if verbose: 
        print('---------------------------------------')
        print('Training set accuracy: {:5.4f}'.format(train_acc))
        print('    Test set accuracy: {:5.4f}'.format(test_acc))   
    return

#-------------------------------------------------
# Indices of "correct" and "wrong" predictions
#-------------------------------------------------

def get_correct_wrong(test_predictions, test_targets,
                      verbose=1):
    '''
    * Get the indices into the test dataset for all the images with 
           correct predictions, and with wrong predictions.
    '''
    wrong = np.where(np.array(test_targets) != np.array(test_predictions))[0]
    correct = np.where(np.array(test_targets) == np.array(test_predictions))[0]
    if verbose:
        print('------------- Test Set: ---------------')
        print('# Correct predictions: {}'.format(len(correct)))
        print('  # Wrong predictions: {}'.format(len(wrong)))
        print('---------------------------------------')
    return correct, wrong


#--------------------------------------------
# Confusion matrix
#--------------------------------------------

def plot_confusion_matrix(targets, predictions, 
                          labels=None, normalize=False, log_color=True,
                          title='Confusion matrix', cmap=plt.cm.Blues,
                          filename=None):
    '''
    Make a nice color-scale plot of the confusion matrix,
    using the targets and predictions.
    '''
    fig = plt.figure(figsize=(7,7))
    plt.rcParams.update({'font.size': 14})
    cm = confusion_matrix(targets, predictions)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:,np.newaxis]        

    if log_color:
        plt.imshow(np.log10(np.clip(cm,1,cm.max())),   # floor at 1 so log is defined
                   interpolation='nearest', cmap=cmap) 
    else:
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    cbar = plt.colorbar()
    if log_color: cbar.set_label('log N')
    if labels:
        tick_marks = list(labels.keys())
        rotation = 90 if max([len(v) for v in labels.values()]) > 2 else 0
        plt.xticks(tick_marks, list(labels.values()), rotation=rotation, ha='center')
        plt.yticks(tick_marks, list(labels.values()))
                   
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i,j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j,i, format(cm[i,j], fmt),
                 horizontalalignment='center',
                 color='white' if cm[i,j] > thresh else 'black')
    plt.tight_layout()
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    if filename:
        plt.savefig(filename)
    else:
        plt.show()
    return

#--------------------------------------------
# Precision / Recall / F1
#--------------------------------------------

def precision_recall(targets, predictions, normalize=False):
    '''
    Display the precision and recall data for binary outcome predictions
    '''
    tarr = np.array(targets,dtype=int)
    parr = np.array(predictions,dtype=int)
    true_pos = np.where(tarr*parr)[0]
    false_pos = np.where((1-tarr)*parr)[0]
    false_neg = np.where(tarr*(1-parr))[0]
    true_neg = np.where((1-tarr)*(1-parr))[0]

    n_tp = len(true_pos) 
    n_fp = len(false_pos) 
    n_fn = len(false_neg) 
    n_tn = len(true_neg)         

    f_tp = n_tp / len(targets)
    f_fp = n_fp / len(targets)
    f_fn = n_fn / len(targets)
    f_tn = n_tn / len(targets)
    
#     print(' True positives: {}'.format(n_tp))
#     print('False positives: {}'.format(n_fp))
#     print('False negatives: {}'.format(n_fn))
#     print(' True negatives: {}'.format(n_tn))

    if not normalize:
        print()
        print('          |        Truth    ')
        print('          |     Yes       No')
        print('--------------------------------')
        print('Pred: Yes |     {}      {}'.format(n_tp,n_fp))
        print('Pred:  No |     {}      {}'.format(n_fn,n_tn))
        print()

    if normalize:
        print()
        print('          |        Truth    ')
        print('          |     Yes       No')
        print('--------------------------------')
        print('Pred: Yes |     {:4.2f}      {:4.2f}'.format(f_tp,f_fp))
        print('Pred:  No |     {:4.2f}      {:4.2f}'.format(f_fn,f_tn))
        print()

    precision = n_tp / (n_tp + n_fp)
    recall = n_tp / (n_tp + n_fn)
    f1 = 2 * (precision * recall) / (precision + recall)    
    print('     Precision: {:4.2f}  (Purity)'.format(precision))
    print('        Recall: {:4.2f}  (Completeness)'.format(recall))
    print('            F1: {:4.2f}'.format(f1))
        
    return