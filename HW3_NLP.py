from collections import Counter
import os 
import pandas as pd
import random
import re
import shutil
from textblob import TextBlob
import zipfile


cwd = os.getcwd() # get working directory, this also happens to be where I've stored the folder with the text files 
#cwd = os.chdir() # or change to the working directory in which the script and data folder is located.
data_folder = "Characters" # Name of folder in which the text files (data) is located in
character_path = os.path.join(cwd, data_folder) #path to all character raw data


# extract all overwrites files with the same name, Macs also create a hidden folder within zip folders,
# which gets extracted if you try to singularly extract files from Zipfiles infolist() with extract()
# to avoid the extra files and from being overwritten, I extracted the text from the zip files to randome folders, all of which will 
# be located in a a temp folder, which I will just later go through to extract all the texts and then delete
#by having each set of text files from each zip folder in a separate folder, files with the same name will not be overwrittena and deleted.
temp_folder = os.path.join(character_path, "temp_to_delete") # the temporary folder where we will be handling the data
os.mkdir(temp_folder) # to make temp folder directory

for zips in os.listdir(character_path): #go through zip file in the folder
    zips_path = os.path.join(character_path, zips) # get the absolute path to the zip folders
    random_folder = os.path.join(temp_folder, "{}".format(random.randint(1,10000))) # path to random folder in which the text from one zip file will be located
    os.mkdir(random_folder) # creates the random folder
    if zipfile.is_zipfile(zips_path): # check to see if it is a zip file
        with zipfile.ZipFile(zips_path) as zipped: 
            zipped.extractall(random_folder) # extract all text files from zipped folders and place it in the random folder created above
        os.remove(zips_path) # to remove the zipped folders,

data_links_txt = [] # initialize list to store paths for text files
data_links_csv = [] #Initialize list to store paths for csv files

#walk through subdirectories of given folder and store path to respective list if text or csv
for root, dirs, files in os.walk(character_path): 
    for file in files: 
        if file.endswith(".txt"):
             data_links_txt.append(os.path.join(root, file))
        if file.endswith(".csv"):
            data_links_csv.append(os.path.join(root,file))

# MacOs recognizes the MACOSX hidden folder, and that is a path we do not need
female_data = pd.DataFrame(columns=["Description","Sentiment"]) # initialize dataframe to store all female descriptions
male_data = pd.DataFrame(columns=["Description","Sentiment"]) # initialize dataframe to store all male descriptions

for x in data_links_txt:
    if re.search(r"MACOSX", x): # skip over paths referring to the hidden folder
        continue
    if re.search(r"she|(\bher)|(\bfemale)", x, re.IGNORECASE):
        with open(x, "rt") as female_texts: # open text files to read
            for female_txt in female_texts: # go through each line of the particular text file and add it to the female_data dataframe
                female_data = female_data.append({"Description": female_txt}, ignore_index = True)
    if re.search(r"(\bhe)[^r]|(\bhis)|(\bmale)", x, re.IGNORECASE): # to find all male files with a word boundary and non inclusion of r to prevent files with her to be chosen
        with open(x, "rt") as male_texts: # open text files to read
            for male_txt in male_texts: # go through each line of the particular text file and add it to the female_data dataframe
                male_data = male_data.append({"Description": male_txt}, ignore_index = True)
    
# repeat the steps above for files stored as csvs instead od txt  
for y in data_links_csv:
    if re.search(r"MACOSX", y):
        continue
    if re.search(r"she|(\bher)|(\bfemale)", y, re.IGNORECASE):
        with open(y, "rt") as female_excel:
            for female_csv in female_excel:
                female_data = female_data.append({"Description": female_csv}, ignore_index = True)
    if re.search(r"(\bhe)[^r]|(\bhis)|(\bmale)", y, re.IGNORECASE):
        with open(y, "rt") as male_excel:
            for male_csv in male_excel:
                male_data = male_data.append({"Description": male_csv}, ignore_index = True)


###############################
# Clean the data 
#Started with the males first, because some of the descriptions still had the female desc in the same sentence
female_addins = [] # this is where the female characters from the male data set will be stored
for i in range(len(male_data["Description"])):
    male_data["Description"][i] = re.sub(r"\d\W?","", male_data["Description"][i]) # gets rid of all the numbers preceding the sentences 
    male_data["Description"][i] = re.sub(r"\\", "", male_data["Description"][i]) # getting rid of some punctuation
    male_data["Description"][i] = re.sub(r"-", " ", male_data["Description"][i])
    male_data["Description"][i] = re.sub(r"\"", "", male_data["Description"][i])
    male_data["Description"][i] = re.sub(r"^\s", "", male_data["Description"][i]) # to get rid of white space in the beginning of the sentence
    male_data["Description"][i] = re.sub(r"<", "", male_data["Description"][i])
    if re.search(r" (?=She's)", male_data["Description"][i]): #using positive lookahead to split sentences with both male and female characters
        male_data["Description"][i], female_addition = re.split(r" (?=She's)", male_data["Description"][i])
        female_addins.append(female_addition) # storing the characters in the list initialized above
    if re.search(r"^[^He's]", male_data["Description"][i]): # Look for sentences that do not start with He's
        male_data["Description"][i] = re.sub("(^[^He's])", r"He's \1", male_data["Description"][i]) # add He's to the beginning of the sentence
    if len(male_data["Description"][i]) < 20: # to get rid of lines that aren't proper character descriptions
        male_data = male_data.drop([i], axis = 0)

for addin in female_addins: # adding the female characters from above to the female dataset
    female_data = female_data.append({"Description": addin}, ignore_index = True)

for i in range(len(female_data["Description"])):
    female_data["Description"][i] = re.sub(r"\d\W?","", female_data["Description"][i]) # gets rid of all the numbers preceding the sentences
    female_data["Description"][i] = re.sub(r"\\", "", female_data["Description"][i]) # getting rid of some punct
    female_data["Description"][i] = re.sub(r"-", " ", female_data["Description"][i]) # getting rid of some punctuations
    female_data["Description"][i] = re.sub(r"\"", "", female_data["Description"][i]) # to get rid of misc. quotes in the sentence
    female_data["Description"][i] = re.sub(r"^\s", "", female_data["Description"][i]) # to get rid of white space
    female_data["Description"][i] = re.sub(r"<", "", female_data["Description"][i])
    if re.search(r"^[^She's]", female_data["Description"][i]): #Look for sentences that don't start with She's and add it to the beginning of the sentence
        female_data["Description"][i] = re.sub("(^[^She's])", r"She's \1", female_data["Description"][i])
    if len(female_data["Description"][i]) < 20: # getting rid of rows that aren't sentences, or the ones with "They Fight Crime"
        female_data = female_data.drop([i], axis = 0)

#Resetting the index of the data frame since some rows are now missing because of the deletions
female_data = female_data.reset_index(drop=True) 
male_data = male_data.reset_index(drop=True)

#############################
# Sentiment Analysis and Descriptors

descriptors = []  # initialize a list where the adjectives will be stored


for i in range(len(female_data["Description"])): # this will go through each line one by one
    text = TextBlob(female_data["Description"][i]) # create a base class for the string 
    female_data["Sentiment"][i] = text.sentiment.polarity # get the polarity of the sentence
    part_of_speech = text.pos_tags # get the parts of speech for each token
    for adj in part_of_speech:
        if re.search(r"JJ", adj[1]): #find any JJ (adjective tag JJ, JJR, JJS)
            descriptors.append(adj[0]) # add the adjective to the list

# the same for the male _ data list
for i in range(len(male_data["Description"])):
    text = TextBlob(male_data["Description"][i])
    male_data["Sentiment"][i] = text.sentiment.polarity
    part_of_speech = text.pos_tags
    for adj in part_of_speech:
        if re.search(r"JJ", adj[1]): #find any JJ (adjective tag JJ, JJR, JJS)
            descriptors.append(adj[0]) # add the adjective to the list

#Sorting 
female_data = female_data.sort_values("Sentiment", ascending = False) # sort the data based on descending polarity score
male_data = male_data.sort_values("Sentiment", ascending = False)

#reset the index which changed because of the sort 
female_data = female_data.reset_index(drop=True)
male_data = male_data.reset_index(drop=True)

#Save the clean data sets
female_data.to_csv(os.path.join(character_path,"female_data.csv"))  
male_data.to_csv(os.path.join(character_path,"male_data.csv"))  

#Remove the temporary folder in which we were working in earlier
shutil.rmtree(temp_folder)

######################
# Top / Bottom 10 Characters 

top_bottom_characters = open("top_bottom_characters.txt","w+") # Create a text file to store the new characters
top_bottom_characters.write("TOP 10 CHARACTERS \n \n")

#from the sorted clean data set create the top 10 best they fight crime characters 
for i in range(0,10):
    female = female_data["Description"][i]
    male = male_data["Description"][i]
    top_bottom_characters.write("{}) {} {} They fight crime! \n".format(i+1, male, female))

top_bottom_characters.write("\n BOTTOM 10 CHARACTERS \n \n")

#from the sorted clean data set create the top 10 worst they fight crime characters 

for i in range(1,11):
    female = female_data.iloc[-i,0]
    male = male_data.iloc[-i,0]
    top_bottom_characters.write("{}) {} {} They fight crime! \n".format(i, male, female))

top_bottom_characters.close()
###########################
# Top 10 Descriptors 

descriptors_frequency = Counter(descriptors) # count the amount of times each adjective occurred within the data sets
descriptors_frequency = pd.DataFrame.from_dict(descriptors_frequency, orient='index').reset_index() # store the information in a dataframe
descriptors_frequency = descriptors_frequency.rename(columns={"index":"Descriptors", 0:"Frequency"})
descriptors_frequency = descriptors_frequency.sort_values("Frequency", ascending = False).reset_index(drop = True) # sort the information in descending order

top_descriptors = open("top_descriptors.txt","w+") # create a textfile to store the top ten frequent descriptors
top_descriptors.write("TOP 10 DESCRIPTORS USED \n \n")

for i in range(0,10):
    top_descriptors.write("{}) Descriptor: {} ----- Frequency: {} \n".format(i+1, descriptors_frequency["Descriptors"][i], descriptors_frequency["Frequency"][i])) 

top_descriptors.close()

