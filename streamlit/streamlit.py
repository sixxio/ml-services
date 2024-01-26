import streamlit as st
import extra_streamlit_components as stx

import json
import pandas as pd
from joblib import load
from hashlib import sha512
from datetime import datetime
import requests

endpoint = 'fastapi:9999'
cm = stx.CookieManager()
st.session_state.update(cm.get_all())


def predict():
    path = st.session_state.get('data', None)
    match path.name.split('.')[-1]:
        case 'csv':
            data = pd.read_csv(uploaded_file)
        case 'json':
            data = pd.read_json(uploaded_file)

    cols = json.load(open('./top_features.json'))
    data = data[cols].dropna()

    model_name = st.session_state.get('model').split(' ')[0]
    models = get_models()
    model_id = [model['id'] for model in models if model_name==model['name']][0]
    response = requests.post(url=f'http://{endpoint}/predictions/',
                             json={
                                    "input_data":data.to_json(),
                                    "output_data":'{"no":"no"}',
                                    "user_id": st.session_state.get('user_id'),
                                    "model_id": model_id
                                 })
    return pd.read_json(json.loads(response.json()['output_data']))

def get_models():
    return requests.get(f'http://{endpoint}/models/').json()

def create_user():
    requests.post(f'http://{endpoint}/sign-up/',
                    json={"email": st.session_state.get('email_sign_up', None),
                          "name": st.session_state.get('name_sign_up', None),
                          "login": st.session_state.get('login_sign_up', None),
                          "balance": 0,
                          "hash": sha512(st.session_state.get('pw_sign_up', None).encode()).hexdigest()})
        
def auth_user(cm):
    resp = requests.post(f'http://{endpoint}/token',
                            data={'username':st.session_state.get('email_sign_in', None),
                                  'password':sha512(st.session_state.get('pw_sign_in', None).encode()).hexdigest()})
    cm = stx.CookieManager('jwt')
    cm.set('jwt', resp.json()['access_token'], key='jwt1')
    cm.set('user_id', resp.json()['user_id'], key='uid')
    print(resp.json())


def get_balance():
    resp = requests.get(f'http://{endpoint}/users/{st.session_state.get("user_id")}')
    return resp.json()['balance']

def refill():
    requests.post(f'http://{endpoint}/transactions/', 
                  json={"amount": st.session_state.get('amount', 0),
                        "user_id":st.session_state.get('user_id')})
                #     }, 
                #   headers={'Authorization':f'Bearer {cm.get('jwt')}'})

def get_pred_history():
    return requests.get(f'http://{endpoint}/predictions/{st.session_state.get('user_id')}').json()

def get_bill_history():
    return requests.get(f'http://{endpoint}/transactions/{st.session_state.get('user_id')}').json()

if cm.get('jwt') is None:

    l, r = st.tabs(['Authorization', 'Sign up'])
    with l:
        username = st.text_input("Email", key='email_sign_in')
        password = st.text_input("Password", type="password", key='pw_sign_in')
        if st.button("Sign in", use_container_width=True):
            auth_user(cm)
    with r:
        username = st.text_input("Username", key='login_sign_up')
        email = st.text_input('Email', key='email_sign_up')
        name = st.text_input('Name', key='name_sign_up')
        password = st.text_input("Password", type="password", key='pw_sign_up')
        if st.button("Sign up", use_container_width=True):
            create_user() # TBD
else:
    st.title("Predictor")
    st.markdown(f'## Your balance is {get_balance()} tokens')
    uploaded_file = st.file_uploader("Upload a file", key='data')

    models = [f"{i['name']} - {i['cost']} tokens per predict" for i in get_models()]
    selected_model = st.selectbox("Select a model", models, key='model')

    if st.button("Predict") and st.session_state.get('data', None):
        result = f"Predicted result for {selected_model} using uploaded file: {uploaded_file.name}"
        with st.spinner('Prediction in progress..'):
            pred = predict()
        st.dataframe(pred)

        df = pd.DataFrame({"Result": [result]})
        csv = pred.to_csv(index=False)
        st.download_button(
            label="Download result",
            data=csv,
            file_name="result.csv",
            mime="text/csv"
        )

    st.divider()

    st.title('Refill')
    st.number_input('Choose sum', min_value=0, max_value=15000, key='amount')
    if st.button('Refill'):
        refill()
    
    with st.expander('Prediction history'):
        st.dataframe(get_pred_history(), hide_index=True)

    with st.expander('Transaction history'):
        st.dataframe(get_bill_history(), hide_index=True)
