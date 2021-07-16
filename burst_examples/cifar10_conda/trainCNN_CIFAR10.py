import torch
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary

import argparse
import subprocess, os, sys

import cifar_data_tools as dt
import ml_tools as ml

OUTPUT_DIR = 'output/'
LOGFILE = OUTPUT_DIR + 'model_log.txt'

#--------------------------------------------
# Define the Convolutional Neural Net
#--------------------------------------------

class CNN(nn.Module):
    def __init__(self, K):
        super(CNN, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.MaxPool2d(2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.MaxPool2d(2)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.MaxPool2d(2)
        )
        self.fc1 = nn.Linear(128 * 4 * 4, 1024)
        self.fc2 = nn.Linear(1024, K)
    def forward(self,x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x.view(x.size(0),-1)
        x = F.dropout(x, p=0.5)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, p=0.2)
        x = self.fc2(x)
        return x
    def summarize(self):
        # Print summary of model
        summary(self, (3, 32, 32))
        return
    
#----------------------------------------------------------
# Train the model and see how we do!
#----------------------------------------------------------

def main():
    
    # Get command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', type=int, default=1, 
                        help='Specify level of verbosity: 0=none, 1=default, 2=extra-verbose')
    parser.add_argument('--nepochs', type=int, default=2, 
                        help='Specify the number of training epochs')
    args = parser.parse_args()
    
    # Check for output directory to store plots
    if not os.path.isdir(OUTPUT_DIR):
        os.system('mkdir '+OUTPUT_DIR)

    # Set up logging
    if args.verbose:
        tee = subprocess.Popen(["tee", LOGFILE], stdin=subprocess.PIPE)
        os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
        os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

    
    # Load train/test dataset
    train_dataset, test_dataset, label_dict = dt.load_CIFAR10_data(verbose=args.verbose)
    # Plot one example image from each category 
    dt.display_example_data(train_dataset, label_dict, 
                            filename=OUTPUT_DIR+'training_example_images.png')

    # Construct the model
    model = CNN(len(label_dict))

    # Check to see if GPU is available and move model to GPU if it is
    device = torch.device("cuda:0") if torch.cuda.is_available() else "cpu"
    if args.verbose:
        print('GPU is available?: {}'.format(torch.cuda.is_available()))
        print('Using device: {}'.format(device))
    model.to(device)    

    # Define our loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())    

    # Use batch gradient descent; we don't want to load the whole dataset into memory all at once!
    batch_size = 128
    train_loader, test_loader = dt.get_dataloaders(train_dataset, test_dataset, 
                                                   batch_size=batch_size)

    # Execute the training loop
    train_losses, test_losses = ml.train(train_loader, model, optimizer, criterion,
                                         device=device,
                                         n_epochs=args.nepochs, test_loader=test_loader, 
                                         verbose=bool(args.verbose), print_every=1)
    
    # Plot loss per epoch to output directory
    ml.plot_losses(train_losses, test_losses, filename=OUTPUT_DIR+'model_losses.png')

    # Get model predictions
    train_predictions, train_targets = ml.predict(train_loader, model, device=device, 
                                                  multiclass=True)
    test_predictions, test_targets = ml.predict(test_loader, model, device=device, 
                                                multiclass=True)
    
    # Get overall accuracy
    ml.get_accuracy(train_predictions, train_targets, 
                    test_predictions, test_targets, 
                    verbose=args.verbose)

    # Plot examples of images we got wrong
    correct, wrong = ml.get_correct_wrong(test_predictions, test_targets, verbose=args.verbose)
    dt.display_pred_examples(wrong, test_dataset, test_targets, test_predictions,
                             label_dict, filename=OUTPUT_DIR+'wrong_examples.png')
    
    # Make the confusion_matrix
    ml.plot_confusion_matrix(test_targets, test_predictions, labels=label_dict, log_color=True, 
                             filename=OUTPUT_DIR+'confusion_matrix.png')
    
    # Plot model summary info
    model.summarize()
    
    # Flush logging
    if args.verbose:
        print("\nstdout flushed", flush=True)
        print("stderr flushed", file=sys.stderr, flush=True)    
    
    
if __name__ == '__main__':
    main()
