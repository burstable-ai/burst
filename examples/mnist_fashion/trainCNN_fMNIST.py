import torch
import torch.nn as nn
import argparse
import os

import mnist_fashion_data as mdata
import ml_tools as ml

OUTPUT_DIR = 'output/'
filename_root = 'CNN_'

#--------------------------------------------
# Define the Convolutional Neural Net
#--------------------------------------------

# Define model using custom module
class CNN(nn.Module):
    def __init__(self, K):
        super(CNN, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=2),
            nn.ReLU()            
        )
        self.dense_layers = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(128 * 2 * 2, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, K)
        )
    def forward(self,X):
        out = self.conv_layers(X)
        out = out.view(out.size(0), -1)
        out = self.dense_layers(out)
        return out

    
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
    mdata.display_example_data(train_dataset, label_dict, filename=OUTPUT_DIR+filename_root+'training_example_images.png')

    # Construct the model
    model = CNN(len(label_dict))

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
                                         verbose=bool(args.verbose), print_every=1)
    
    # Plot loss per epoch to output directory
    ml.plot_losses(train_losses, test_losses, filename=OUTPUT_DIR+filename_root+'model_losses.png')

    # Get model predictions
    train_predictions, train_targets = ml.predict(train_loader, model, device=device, 
                                                  multiclass=True)
    test_predictions, test_targets = ml.predict(test_loader, model, device=device, 
                                                multiclass=True)
    
    # Get overall accuracy
    ml.get_accuracy(train_predictions, train_targets, test_predictions, test_targets, verbose=args.verbose)

    # Plot examples of images we got wrong
    correct, wrong = ml.get_correct_wrong(test_predictions, test_targets, verbose=args.verbose)
    mdata.display_pred_examples(wrong, 
                                test_dataset, test_targets, test_predictions,
                                label_dict,
                                filename=OUTPUT_DIR+filename_root+'wrong_examples.png')
    
    # Make the confusion_matrix
    ml.plot_confusion_matrix(test_targets, test_predictions, labels=label_dict, log_color=True, 
                             filename=OUTPUT_DIR+filename_root+'confusion_matrix.png')
    
    
if __name__ == '__main__':
    main()
