# Species Identification from Birdsong

In this repository we provide our code for data preprocessing, data augmentation, network training and network testing.

## How we got the data

To download the data, save the files “all_samples.csv” and “fetch_and_convert_data.R” to a directory on your machine. You will need R installed and an R editor, we recommend RStudio. You will also need 3 packages: warbleR (https://www.rdocumentation.org/packages/warbleR/versions/1.1.23), tuneR (https://www.rdocumentation.org/packages/tuneR/versions/1.3.3/topics/tuneR), and dplyR (https://www.rdocumentation.org/packages/dplyr/versions/0.7.8)

You will need to edit the R script to set the current working directory to the directory containing the script and CSV (line 79 of the script). Then run the R script. The download may take several hours or more, and take up several dozen GB, as there are over 8,000 MP3 files to download and convert to WAV. 

After downloading, you will need to use “Create_MFCC_Feature_Vectors.ipynb” to convert the WAV files to feature vectors, then combine them into tensors. Open the notebook and edit the “DATA_DIR” line to point to the directory the WAV files are saved in. Then run the Python script. This may take several hours.
