import streamlit as st
import pandas as pd
import json
from datetime import datetime


st.set_page_config(page_title="Base Dictionary Update", page_icon='random', 
                layout="wide",
                initial_sidebar_state="expanded")


# load the json file
@st.cache(allow_output_mutation=True)
def load_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data



st.title("Base Dictionary Update Tool")
st.write('This page is for associate consultants to update the base dictionary.')

with st.expander('Click here to view the instructions for updating base dictionary'):
    st.markdown("""
    #### Instructions
    1. Visit the responses for the [update form](https://docs.google.com/spreadsheets/d/1yewrCftjO5iJzg5ib7wTrII80ayT4zHxek_D9D4KIEw/edit?usp=sharing)
    2. Download the responses as **CSV** file.
    3. Upload the CSV file to this page and download the updated dictionary (a JSON file)
    4. Visit the [Github](https://github.com/kylieeeeee/LIS-Translation.git) for the LIS translation tool.
    5. Go to the *data* file and rename the old base dictionary **LIS DB.json** to **LIS DB_replaced at [today's date].json**
    6. Upload the new dictionary to the *data* file and rename it to **LIS DB.json**
    """)

st.header('Upload new tests that need to be added to the base dictionary')
uploaded_file = st.file_uploader("Select the file with the new LIS test dictionary:", type=['csv'])
st.info('Please only upload **CSV** file.')
st.markdown('---')

if uploaded_file is not None:
    # read csv
    new_tests = pd.read_csv(uploaded_file)
    with st.expander('Click here to view the file you uploaded'):
        st.write('There are ' + str(len(new_tests)) + ' new tests in this file.')
        st.dataframe(new_tests)

    new_tests.rename(columns={"Customer's LIS test name": 'LISName',
                            "Material for the LIS test": 'Material',
                            "Corresponding Roche assay names": 'AssayName'}, inplace = True)

    # Load the base dictionary      
    base_dict = load_json('data/LIS DB.json')

    # create a new dicitonary for the new tests
    new_dict = {}
    for i in range(len(new_tests)):
        test = new_tests.iloc[i]
        LISName = test['LISName']
        Material = test['Material']
        Assay = test['AssayName']

        new_dict[LISName] = {'Include': 1, 'Material': Material, 'AssayName': Assay}

    # update the new tests to base dictionary
    for key, value in new_dict.items():
        # if the new test is already in the base dicitonary, update the old one
        if key in base_dict.keys():
            base_dict[key] = value
        
        # the test is not in the dictionary, add the test to base
        else:
            base_dict[key] = value


    # download the updated base dictionary
    today = datetime.today().strftime("%Y%m%d")
    new_file_name = 'LIS DB_update at ' + today +'.json'
    json_dict = json.dumps(base_dict)

    st.download_button(
        label = '📥 Download the updated base dictionary (JSON file)',
        file_name = new_file_name,
        data = json_dict
    )
