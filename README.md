# FE595_HW3_NLP
NLP on TheyFightCrime Characters

# <strong> Overview </strong>

This repository will process scraped data from the theyfightcrime.org website. It will give you a cleaned data set (one for Male and Female Characters), a textfile for top 10 and bottom 10 characters based on polarity, and a textfile of just the top 10 most common descriptors (adjectives) used to make the characters. 

# <strong> Reading In  and Cleaning Data </strong> 
Start or change into the directory where the script is located and the folder where the zip files of the data are stored. 

The script reads in the zip files and stores the unzipped content in a temporary folder. The data is read in separately if it's a text file or a csv. Regular expressions are used to clean the data. The clean data is then saved in two csv in the original folder where the raw data was stored - one csv for Male Characters and the other for Female Characters. All the zip files, and the temporary folder where the process happens is deleted. 

# <strong> Sentiment and Tagging </strong> 
Each line from the datasets are read in separately, and the polarity score for each sentence is found using TextBlob and stored. The tokens in the sentence are also tagged and the ones that are adjectives are stored separately to process as descriptors. From the scores collected the top ten characters with the highest polarity (most positive) and the bottom 10 characters with the lowest (most negative) polarity are saved in a textfile. The 10 descriptors with the highest frequency within both data sets are also saves in a textfile. 
