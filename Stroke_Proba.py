import streamlit as st
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor 
from catboost import CatBoostClassifier, CatBoostRegressor 
import joblib
import pandas as pd
import numpy as np
import urllib.request
import boto3
from botocore.config import Config
from botocore import UNSIGNED
import io

st.set_page_config(
    page_title="Stroke Risk Assessment", page_icon="🧠", 
    menu_items={
        'Get Help': 'https://www.kaggle.com/code/frankmollard/machine-learning-process-idea-2-app',
        'About': 'Developed by Frank Mollard'
    }
)

tab1, tab2 = st.tabs(["Stroke Risk", "Advanced Information"])

tab1.header('Stroke Risk Assessment')
tab1.text(
    body ="""
    This application is designed to assess the risk of stroke 
    using machine learning algorithms. If a stroke is suspected, 
    a doctor must always be consulted. This is a medical emergency.  
    """,
    help="""
    This application is based on scientific evidence, but does not 
    include all risk factors. Therefore, this app should only be 
    used as a first but not only assessment.
    """
)

tab2.title('Contribution by Model')
tab2.text(
    """
    At this point, you can check the risk contributions in
    percentage points for the individual models.
    """
)

URL="https://strokemodels.s3.eu-central-1.amazonaws.com"

data_load_state1 = tab1.text('Loading models...')
data_load_state2 = tab2.text('Loading models...')

#Load Sklearn models
@st.cache_resource()
def loadAllModels(url):
    models=[]
    for c in ["svm1", "svm2", "logit1", "logit2", "nbc1", "nbc2", "rf1", "rf2", "errGBR"]:
        models.append(
            joblib.load(
                urllib.request.urlopen(url + "/" + "{}.pkl".format(c))
                )
            )

        
    return models[0], models[1], models[2], models[3], models[4], models[5], models[6], models[7], models[8]

svm1, svm2, logit1, logit2, nbc1, nbc2, rf1, rf2, errGBR = loadAllModels(URL)

#Load CatBoost
@st.cache_resource()
def loadCatBoost(_CB = CatBoostClassifier(), C=["cb1", "cb2"]):
    
    s3 = boto3.resource(
        service_name='s3',
        region_name='eu-central-1',
        config=Config(signature_version=UNSIGNED)
    )
    bucket = s3.Bucket('strokemodels')

    models=[]

    for c in C:
        
        obj = bucket.Object("%s" % (c))
        file_stream = io.BytesIO()
        obj.download_fileobj(file_stream)# downoad to memory
        
        models.append(_CB.load_model(blob=file_stream.getvalue()))
        
    return models
    
catClassifier = loadCatBoost()
cb1, cb2 = catClassifier[0], catClassifier[0]

catRegressor = loadCatBoost(_CB = CatBoostRegressor(), C=["errCBR"])
errCBR = catRegressor[0]

# Notify the reader that the data was successfully loaded.
data_load_state1.text("AI-Models Loaded")
data_load_state2.text("AI-Models Loaded")
###############SIDEBAR START################

st.sidebar.title("Patient Data")

work_type = st.sidebar.selectbox(
    'Work Type', ["Child", "Government", "Never worked", "Private", "Self-employed"]
    )    
if work_type == "Child":
    work_type_children = 1
    work_type_Self_employed	= 0
    work_type_Private = 0
    work_type_Never_worked = 0
    workType = "children"
elif work_type == "Never worked":
    work_type_children = 0
    work_type_Self_employed	= 0
    work_type_Private = 0
    work_type_Never_worked = 1
    workType = "Never_worked"
elif work_type == "Private":
    work_type_children = 0
    work_type_Self_employed	= 0
    work_type_Private = 1
    work_type_Never_worked = 0
    workType = "Private"
elif work_type == "Self-employed":
    work_type_children = 0
    work_type_Self_employed	= 1
    work_type_Private = 0
    work_type_Never_worked = 0
    workType = "Self-employed"
else:
    work_type_children = 0
    work_type_Self_employed	= 0
    work_type_Private = 0
    work_type_Never_worked = 0
    workType = "Govt_job"

if work_type == "Child":
    minAge = 0
    maxAge = 16
    defAge = 10
else:
    minAge = 17
    maxAge = 100
    defAge = 40

age = st.sidebar.slider('Age', minAge, maxAge, defAge)  
adjst = 10000/(age*10+1) if work_type != "Child" else 75
bmi = st.sidebar.slider('BMI', 5, 45, 20) 
agl = st.sidebar.slider('Average Glucose Level', 50, 400, 100) 

smoking = st.sidebar.selectbox(
    'Smoking Status', ["Never Smoked", "Formerly Smoked", "Smokes", "Unknown"]
    )
if smoking == "Never Smoked":   
    smoking_status_formerly_smoked = 0
    smoking_status_smokes = 0
    smoking_status_never_smoked = 1
    smoking_status = "never smoked"
elif smoking == "Formerly Smoked":
    smoking_status_formerly_smoked = 1
    smoking_status_smokes = 0
    smoking_status_never_smoked = 0
    smoking_status = "formerly smoked"
elif smoking == "Smokes":
    smoking_status_formerly_smoked = 0
    smoking_status_smokes = 1
    smoking_status_never_smoked = 0
    smoking_status = "smokes"
else:
    smoking_status_formerly_smoked = 0
    smoking_status_smokes = 0
    smoking_status_never_smoked = 0   
    smoking_status = "Unknown"
    
heart = st.sidebar.selectbox(
    'Heart Disease', ["No", "Yes"]
    )    
if heart == "Yes":
    heart_disease = 1
else:
    heart_disease = 0
    
gender = st.sidebar.selectbox(
    'Gender', ["Male", "Female"]
    )    
if gender == "Male":
    gender_Male = 1
else:
    gender_Male = 0
    
married = st.sidebar.selectbox(
    'Ever Married', ["Yes", "No"]
    )    
if married == "Yes":
    ever_married_Yes = 1
else:
    ever_married_Yes = 0
    
residence_type = st.sidebar.selectbox(
    'Residence Type', ["Urban", "Rural"]
    )    
if residence_type == "Urban":
    Residence_type_Urban = 1
else:
    Residence_type_Urban = 0
    
hyTen = st.sidebar.selectbox(
    'Hypertension', ["No", "Yes"]
    )    
if hyTen == "Yes":
    hypertension = 1
else:
    hypertension = 0

st.sidebar.text(" ")
###############SIDEBAR END##################
    
data_load_state1.text("Predicting...")
data_load_state2.text("Predicting...")

data = pd.DataFrame(
    data=[
        [age], [hypertension], [heart_disease], [agl], [bmi], 
        [gender_Male], [work_type_Never_worked], [work_type_Private], 
        [work_type_Self_employed], [work_type_children], [ever_married_Yes], 
        [Residence_type_Urban], [smoking_status_formerly_smoked], 
        [smoking_status_never_smoked], [smoking_status_smokes]
        ], 
    index=['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi',
       'gender_Male', 'work_type_Never_worked', 'work_type_Private',
       'work_type_Self-employed', 'work_type_children', 'ever_married_Yes',
       'Residence_type_Urban', 'smoking_status_formerly smoked',
       'smoking_status_never smoked', 'smoking_status_smokes']
    ).T

dataC = pd.DataFrame(
    data=[
        [age], [hypertension], [heart_disease], [workType], 
        [agl], [bmi], [smoking_status],
        [gender_Male], [ever_married_Yes], [Residence_type_Urban]
        ], 
    index=['age', 'hypertension', 'heart_disease', 'work_type',
       'avg_glucose_level', 'bmi', 'smoking_status',
       'gender_Male', 'ever_married_Yes', 'Residence_type_Urban']
    ).T

#Define list of Continous Features
contVars = ["age", "avg_glucose_level", "bmi"]

#Define Ensemble Function
@st.cache_data
def predict(df, dfc, cv: list, weights: list):
        
    psvm1 = svm1.predict_proba(df[cv])[0][1]
    psvm2 = svm2.predict_proba(df[cv])[0][1]

    pnbc1 = nbc1.predict_proba(df[cv])[0][1]
    pnbc2 = nbc2.predict_proba(df[cv])[0][1]

    prf1 = rf1.predict_proba(
        df[[i for i in df.columns if i not in ['work_type_Never_worked']]]
        )[0][1]
    prf2 = rf2.predict_proba(
        df[[i for i in df.columns if i not in ['work_type_Never_worked']]]
        )[0][1]

    plogit1 = logit1.predict_proba(df)[0][1]
    plogit2 = logit2.predict_proba(df)[0][1]
    
    pcb1 = cb1.predict(dfc, prediction_type='Probability')[:, 1]
    pcb2 = cb2.predict(dfc, prediction_type='Probability')[:, 1]

    p = (psvm1 * weights[0] + prf1 * weights[2] + plogit1 * weights[4] + pcb1[0] * weights[6] + pnbc1 * weights[8]) / 2 + \
        (psvm2 * weights[1] + prf2 * weights[3] + plogit2 * weights[5] + pcb2[0] * weights[7] + pnbc2 * weights[9]) / 2

    return p

#Predictions of two Fold Ensembles
pred = predict(data, dataC, contVars, weights=[0.59, 0.11, 0.02, 0.08, 0.13, 0.50, 0.07, 0.26, 0.19, 0.05])

#Error Prediction 
@st.cache_data
def errPred(df):
    er = errCBR.predict(df)[0]
    return er

uncertainty = np.where(errPred(dataC) < 0, 0, errPred(dataC))

#Contributions to the Prediction by Model
@st.cache_data()
def contributions(preds: list):
    c = pd.DataFrame(
        data=preds,
        index=["Support Vector Machines", "Random Forest", "Logit", "CatBoost", "Naive Bayes Classifier"],
        columns=["Fold 1 in p.p.", "Fold 2 in p.p."]
    )
    return c

data_load_state1.text("Prediction done")

#########Save User-data by caching############
@st.cache_resource()
def userData():
    return []

@st.cache_data()
def delta(l, p):
    if len(l) == 0:
        l.extend([0, round(p*100, 1)])
        d = 0
    else:
        l.pop(0)
        l.append(round(p*100, 1))
        d = l[1] - l[0]
    return d

#Session States######################
if 'old' not in st.session_state:
    st.session_state.old = pred
    old = pred
    st.session_state.adjstOld = adjst
    adjstOld = adjst
else:
    old = st.session_state.old
    st.session_state.old = pred
    adjstOld = st.session_state.adjstOld
    st.session_state.adjstOld = adjst

#Adjustment#########################

#The model is a good predictor, but not necessarily a good model for risk  assessment. 
#To obtain a good model for risk assessment, we use a linear transformation to obtain results that are comparable to recent studies.
#cf: https://pdfs.semanticscholar.org/4808/e782ebbda2893b0ca7af81c16c18bb522dff.pdf?_gl=1*nsrffc*_ga*MTI4NTIxMzUxMC4xNjQxMDM4NTE5*_ga_H7P4ZT52H5*MTY3NjgxNTY4My4xLjAuMTY3NjgxNTY4NC4wLjAuMA..
#google image search for "risk of stroke"


#Show metrics#######################
tab1.metric(
    label="Risk of Stroke", 
    value=str(round(pred*100/adjst, 3)) + " %", 
    #delta=str(round(delta(userData(), pred)/adjst, 2)) + " percentage points", 
    delta=str(round(pred*100/adjst-old*100/adjstOld, 4)) + " percentage points", 
    help="""
    This is the indication for the risk of stroke, given the patient data.
    The change in percentage points compared to your previous indication is displayed smaller below.
    """,
    delta_color ="inverse"
)

tab1.text("Confidence in the risk assessment:\n" + \
          str(round((1-uncertainty)*100,1)) + " %."
)

#######Additional Information##################

@st.cache_data()
def assesBMI(BMI, AGE):
    if BMI > 45 and AGE > 75:
        inf = """
        Note: Information is unreliable.
        BMI > 45 and age > 75.
        """
    elif BMI <= 10:
        inf = "BMI level:\nBMI too low"
    elif BMI < 18.5 and BMI > 10:
        inf = "BMI level:\nShortweight"
    elif BMI >= 18.5 and BMI < 25:
        inf = "BMI level:\nNormal Weight"
    elif BMI >= 25 and BMI < 30:
        inf = "BMI level:\nOverweight"
    elif BMI >= 30 and BMI < 35:
        inf = "BMI level:\nModerate Obesity"
    elif BMI >= 35 and BMI < 40:
        inf = "BMI level:\nStrong Obesity"
    elif BMI >= 40:
        inf = "BMI level:\nExtreme Obesity"
    return inf

tab1.text(assesBMI(bmi, age))
        
#####Data Visualization#########
viz = dataC.copy()
viz.rename(
    columns={
        "age": "Age",
        "bmi": "BMI",
        "avg_glucose_level": "Average Glucose Level",
        "smoking_status": "Smoking Status",
        "heart_disease": "Heart Disease",
        "gender_Male": "Gender",
        "work_type": "Work Type",
        "ever_married_Yes": "Ever Married",
        "Residence_type_Urban": "Residence Type",
        "hypertension": "Hypertension",    
    }, 
    index={0: 'Data entered'}, 
    inplace=True
)
viz["Hypertension"] = hyTen
viz["Heart Disease"] = heart
viz["Ever Married"] = married
viz["Work Type"] = work_type
viz["Smoking Status"] = smoking
viz["Residence Type"] = residence_type
viz["Gender"] = gender

#viz = viz.iloc[:, [1,8,7,9,3,0,5,4,6,2]]

tab1.table(data=viz.T)

#############tab 2 table######################
pred_svm_1 = predict(data, dataC, contVars, weights=[0.59, 0, 0, 0, 0, 0, 0, 0, 0, 0]) * 100/adjst
pred_svm_2 = predict(data, dataC, contVars, weights=[0, 0.11, 0, 0, 0, 0, 0, 0, 0, 0]) * 100/adjst
pred_rf_1 = predict(data, dataC, contVars, weights=[0, 0, 0.02, 0, 0, 0, 0, 0, 0, 0]) * 100/adjst
pred_rf_2 = predict(data, dataC, contVars, weights=[0, 0, 0, 0.08, 0, 0, 0, 0, 0, 0]) * 100/adjst
pred_logit_1 = predict(data, dataC, contVars, weights=[0, 0, 0, 0, 0.13, 0, 0, 0, 0, 0]) * 100/adjst
pred_logit_2 = predict(data, dataC, contVars, weights=[0, 0, 0, 0, 0, 0.50, 0, 0, 0, 0]) * 100/adjst
pred_cb_1 = predict(data, dataC, contVars, weights=[0, 0, 0, 0, 0, 0, 0.07, 0, 0, 0]) * 100/adjst
pred_cb_2 = predict(data, dataC, contVars, weights=[0, 0, 0, 0, 0, 0, 0, 0.26, 0, 0]) * 100/adjst
pred_nbc_1 = predict(data, dataC, contVars, weights=[0, 0, 0, 0, 0, 0, 0, 0, 0.19, 0]) * 100/adjst
pred_nbc_2 = predict(data, dataC, contVars, weights=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0.05]) * 100/adjst

def formater(styler):
    styler.format("{:.4f}")
    styler.background_gradient(cmap="Greens")
    return styler

cont = contributions(
    [
    [pred_svm_1, pred_svm_2],
    [pred_rf_1, pred_rf_2],                
    [pred_logit_1, pred_logit_2],               
    [pred_cb_1, pred_cb_2],                
    [pred_nbc_1, pred_nbc_2],   
    ]
)

tab2.dataframe(
    cont.style.pipe(formater)
)

data_load_state2.text("Prediction done")

tab2.metric(
    label="Risk of Stroke", 
    value=str(round(pred*100/adjst, 3)) + " %", 
    help="""
    This is the indication for the risk of stroke, given the patient data.
    """
)
                             
