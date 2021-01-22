import torch
import torch.nn as nn
import argparse
import os

import mnist_fashion_data as mdata
import ml_tools as ml

OUTPUT_DIR = 'output/'

#--------------------------------------------
# Define the LSTM neural net
#--------------------------------------------

class LSTM(nn.Module):
    '''
    Use recurrent neural net with long/short-term memory (LSTM) 
    '''
    def __init__(self, n_inputs, n_hidden, n_outputs, n_rnnlayers=1):
        super(LSTM, self).__init__()
        self.D = n_inputs
        self.M = n_hidden
        self.K = n_outputs
        self.L = n_rnnlayers
        self.lstm = nn.LSTM(
            input_size=self.D,
            hidden_size=self.M,
            num_layers=self.L,
            batch_first=True)
        self.fc = nn.Linear(self.M, self.K)
    
    def forward(self,X):
        # initial hidden states: 
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        h0 = torch.zeros(self.L, X.size(0), self.M).to(device)
        c0 = torch.zeros(self.L, X.size(0), self.M).to(device)
        h_NxTxM, (h_LxNxM, c_LxNxM) = self.lstm(X, (h0, c0))
        out = self.fc(h_NxTxM[:,-1,:])
        return out

    
#----------------------------------------------------------
# Utility function to reshape FashionMNIST image data 
#    to format needed for LSTM
#----------------------------------------------------------

def reshape_func(input):
    input = input.view(input.size(0), input.size(2), input.size(3))
    return input    
    
    
#----------------------------------------------------------
# Train the model and see how we do!
#----------------------------------------------------------

def main():
    
    # Get command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', type=int, default=1, help='Specify level of verbosity: 0=none, 1=default, 2=extra-verbose')
    parser.add_argument('--nepochs', type=int, default=2, help='Specify the number of training epochs')
    args = parser.parse_args()
    
    # Check for output directory to store plots
    if not os.path.isdir(OUTPUT_DIR):
        os.system('mkdir '+OUTPUT_DIR)
    
    # Load train/test dataset
    train_dataset, test_dataset, label_dict = mdata.load_FashionMNIST_data(verbose=args.verbose)
    # Plot one example image from each category 
    mdata.display_example_data(train_dataset, label_dict, filename=OUTPUT_DIR+'training_example_images.png')

    # Construct the model
    model = LSTM(n_inputs=28, n_hidden=128, n_outputs=10, n_rnnlayers=2)

    # Check to see if GPU is available and move model to GPU if it is
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if args.verbose:
        print('GPU is available?: {}'.format(torch.cuda.is_available()))
        print('Using device: {}'.format(device))
    model.to(device)    

    # Define our loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())    

    # Use batch gradient descent; we don't want to load the whole dataset into memory all at once!
    batch_size = 256
    train_loader, test_loader = mdata.get_dataloaders(train_dataset, test_dataset, batch_size=batch_size)

    # Execute the training loop
    train_losses, test_losses = ml.train(train_loader, model, optimizer, criterion,
                                         device=device,
                                         n_epochs=args.nepochs, test_loader=test_loader, 
                                         reshape_inp=reshape_func,
                                         verbose=bool(args.verbose), print_every=1)
    
    # Plot loss per epoch to output directory
    ml.plot_losses(train_losses, test_losses, filename=OUTPUT_DIR+'model_losses.png')

    # Get model predictions
    train_predictions, train_targets = ml.predict(train_loader, model, device=device, 
                                                  reshape_inp=reshape_func,
                                                  multiclass=True)
    test_predictions, test_targets = ml.predict(test_loader, model, device=device, 
                                                reshape_inp=reshape_func,
                                                multiclass=True)
    
    # Get overall accuracy
    ml.get_accuracy(train_predictions, train_targets, test_predictions, test_targets, verbose=args.verbose)

    # Plot examples of images we got wrong
    correct, wrong = ml.get_correct_wrong(test_predictions, test_targets, verbose=args.verbose)
    mdata.display_pred_examples(wrong, 
                                test_dataset, test_targets, test_predictions,
                                label_dict,
                                filename=OUTPUT_DIR+'wrong_examples.png')
    
    # Make the confusion_matrix
    ml.plot_confusion_matrix(test_targets, test_predictions, labels=label_dict, log_color=True, 
                             filename=OUTPUT_DIR+'confusion_matrix.png')
    
    
if __name__ == '__main__':
    main()
