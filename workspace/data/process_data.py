'''
This ETL Pipeline is handling two datasets
1- messages.csv  contains the messages
2- categories.csv contains the categories for each message
First: will load the datasets into dataframe and drop unuseful columns and merge them
Second: will clean the dataframe by fix catefories and drop duplicates
Third: will save the new data into SQL database
'''

# import packages
import os
import sys
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    """ Load disaster messages and categories into dataframe.

    Args:
        messages_filepath: String. This is a csv file and contains disaster messages.
        categories_filepath: String. This is a csv file and contains disaster categories for each messages.

    Returns:
       pandas.DataFrame
    """
    # read in file
    if os.path.exists(messages_filepath):
        messages = pd.read_csv(messages_filepath)
    else:
        messages = pd.read_csv(messages_filepath + '.gz', compression='gzip')

    # load categories dataset
    if os.path.exists(categories_filepath):
        categories = pd.read_csv(categories_filepath)
    else:
        categories = pd.read_csv(categories_filepath + '.gz', compression='gzip')

    # merge datasets
    df = pd.merge(messages, categories, on='id', how='outer')

    return df

    

def clean_data(df):
    """Clean data.

    Args:
        df: pandas.DataFrame. it contains disaster messages and categories.

    Return:
        pandad.DataFrame
    """
    
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';', expand=True)

    # select the first row of the categories dataframe
    row = categories[0:1]

    # use this row to extract a list of new column names for categories.
    # one way is to apply a lambda function that takes everything
    # up to the second to last character of each string with slicing
    category_colnames = [(v.split('-'))[0] for v in row.values[0]]

    # rename the columns of `categories`
    categories.columns = category_colnames

    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]

        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    # Convert all value into binary (0 or 1)
    categories = (categories > 0).astype(int)

    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)

    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)

    # drop duplicates
    df.drop_duplicates(inplace=True)

    return df


def save_data(df, database_filename, table_name='CleanedDataTable'):
    """Save data into database.

    Args:
        df: pandas.DataFrame. It contains disaster messages and categories that are cleaned.
        database_filename: String. Dataframe is saved into this database file.
        table_name: String. Dataframe is saved into this table on database.
    """
    # load to database
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql(table_name, engine, index=False, if_exists='replace', chunksize=600)  



'''
def build_model():
    # text processing and model pipeline


    # define parameters for GridSearchCV


    # create gridsearch object and return as final model pipeline


    return model_pipeline


def train(X, y, model):
    # train test split


    # fit model


    # output model test results


    return model


def export_model(model):
    # Export model as a pickle file



def run_pipeline(data_file):
    X, y = load_data(data_file)  # run ETL pipeline
    model = build_model()  # build model pipeline
    model = train(X, y, model)  # train model pipeline
    export_model(model)  # save model



if __name__ == '__main__':
    data_file = sys.argv[1]  # get filename of dataset
    run_pipeline(data_file)  # run data pipeline
'''    

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()