import streamlit as st
import pandas as pd
import json
from datetime import datetime


st.set_page_config(page_title="Base Dictionary Update", page_icon='random', 
                layout="wide",
                initial_sidebar_state="expanded")


# load the json file
@st.cache_data
def load_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data



st.title("Base Dictionary Update Tool")
st.write('This page is for associate consultants to update the base dictionary.')

with st.expander('Click here to view the instructions for updating base dictionary'):
    st.markdown("""
    #### Instructions
    ** Note: Please do not change the column names of the response sheet for the update request form.**
    1. Visit the responses for the [update form](https://docs.google.com/spreadsheets/d/1yewrCftjO5iJzg5ib7wTrII80ayT4zHxek_D9D4KIEw/edit?usp=sharing)
    2. Download the responses as **CSV** file.
    3. Upload the CSV file to this page and download the updated dictionary (a JSON file)
    4. Visit the [Github for translation tool](https://github.com/Rocheeeeee/LIS_translation_tool.git) for the LIS translation tool.
    5. Go to the *data* file upload the new dictionary.
    7. Visit the [Github for dictionary update](https://github.com/Rocheeeeee/LIS-dictionary-update) and upload the new **base_dict.json**
    """)


with st.sidebar:
    function_radio = st.radio(
        "Select the function",
        ("Update several translation in the base dictionary", "Update the whole base dictionary")
    )

if function_radio == 'Update several translation in the base dictionary':
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

        try:
            new_tests.rename(columns={"Customer's LIS test name": 'LISName',
                                    "Material for the LIS test": 'Material',
                                    "Corresponding Roche assay names": 'AssayName'}, inplace = True)

            # Load the base dictionary      
            base_dict = load_json('base_dict.json')
            new_base = base_dict.copy()

            # create a new dicitonary for the new tests
            new_dict = {}
            for i in range(len(new_tests)):
                test = new_tests.iloc[i]
                LISName = test['LISName'].upper()
                Material = test['Material']
                Assay = test['AssayName'] # string

                # Turn the string of assays into a list of assays
                Assay = Assay.split(',')

                new_dict[LISName] = {'Include': 1, 'Material': Material, 'Assay Name': Assay}

            # update the new tests to base dictionary
            new_base.update(new_dict)

            json_dict = json.dumps(base_dict)

            st.download_button(
                label = '📥 Download the updated base dictionary (JSON file)',
                file_name = 'base_dict.json',
                data = json_dict)
        except KeyError:
            st.error("The column names for the csv you uploaded should be Customer's LIS test name, Material for the LIS test, Corresponding Roche assay names")

else:
    # upload the excel file for the whole dicitonary
    st.subheader('Select the **EXCEL** file for the base dictionary')
    uploaded_dict = st.file_uploader("Base dictionary", type=['xlsx'])
    st.markdown('The column names for the excel file should be **LIS Test Name**, **Include**, **Material**, and **Assay Name**')

    if uploaded_dict is not None:
        own_dict = pd.ExcelFile(uploaded_dict)
        all_dict_sheets = ['(Not Selected Yet)'] + own_dict.sheet_names

        ## User select the sheet name that needs translation
        selected_dict_sheet = st.selectbox('Select the sheet name:', all_dict_sheets)

        ## to read just one sheet to dataframe and display the sheet:
        if selected_dict_sheet != '(Not Selected Yet)':
                own_dict_sheet = pd.read_excel(own_dict, sheet_name = selected_dict_sheet)
                st.session_state.own_dict_sheet = own_dict_sheet
                with st.expander("Click here to check the dictionary you uploaded"):
                    st.write("Number of observations: " + str(len(own_dict_sheet)))
                    st.write(own_dict_sheet)
                    st.caption("<NA> means there is no value in the cell")

                # If the button is clicked, app will save the dictionary
                if st.button('📤 Upload Dictionary'):
                    newBaseDict = {}
                    for i in range(len(own_dict_sheet)):
                        row = own_dict_sheet.iloc[i]
                        test_name = row['LIS Test Name'].upper()
                        include = int(row['Include'])
                        material = row['Material']
                        assay = row['Assay Name'] # a long string of tests

                        # assay name of 'NA' only may be read in as NaN in python. add a space after it to avoid
                        if assay == 'NA':
                            assay = 'NA '

                        # if NA is one of the assays, need to add a space behind it so it will not be considered missing value when it parse the string to list by ,
                        assay = assay.replace("NA,", "NA ,")

                        # for the test without assay, fill na with a space
                        if assay is None:
                            assay = [' ']

                        # split the assay into a list of tests
                        assay = assay.split(',') # a list

                        newBaseDict[test_name] = {'Include': include, 'Material': material, 'Assay Name': assay}

                    # st.write(newBaseDict)
                    json_dict = json.dumps(newBaseDict)

                    st.download_button(
                        label = '📥 Download the updated base dictionary (JSON file)',
                        file_name = 'base_dict.json',
                        data = json_dict
                        )

