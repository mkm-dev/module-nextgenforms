import streamlit as st
from PIL import Image
import json
from clarifai.client.model import Model
from clarifai.client.input import Inputs

"""
## Create a form with AI
"""

st.session_state.example_schema = {
    "title": "Form Example Title",
    "description": "Example Form",
    "fields": [
        {"type": "text", "label": "Name"},
        {"type": "email", "label": "E-Mail"},
        {"type": "textarea", "label": "Message"},
    ]
}

st.session_state.text_inputs = [
    "Please create a contact form having name, email, and message fields.",
    "I am an event manager. I would like to create a signup form for an event. The form should ask for details like name, email, job role, and company name."

]

if 'stage' not in st.session_state:
    st.session_state.stage = 0


def set_state(i):
    st.session_state.stage = i


def get_schema_from_image(image_file):
    file_bytes = image_file.getvalue()

    prompt = """You are going to help me create a form. For this task you will be given an image of a form. Your task is to identify all the fields the form should have as show in the image, along with their type such as text, email, text area, number and so on. Once you have found all the fields and figured out their types, you have to respond the data in JSON format as is shown in the next example.
    Example Response Format:
    {
        "title": "Form title",
        "description": "A description about what form is for",
        "fields": [
            { "label": "Field 1 Name", "type": "text" },
            { "label": "Field 2 Name", "type": "number" }
        ]
    }

    You should only respond in JSON format. If the given image is not about a form then respond with an invalid data message.
    """

    gpt_4_vision = Model(
        "https://clarifai.com/openai/chat-completion/models/openai-gpt-4-vision")
    inference_params = dict(temperature=0.2, max_tokens=500)
    model_prediction = gpt_4_vision.predict(inputs=[Inputs.get_multimodal_input(
        input_id="", image_bytes=file_bytes, raw_text=prompt)], inference_params=inference_params)

    raw_text = model_prediction.outputs[0].data.text.raw

    clean_text = raw_text.replace("```", "")
    clean_text = clean_text.replace("json", "", 1)
    # print(clean_text)

    schema = clean_text
    return schema


def get_schema_from_text(text):
    prompt = """You are going to help me create a form. For this task you will be given a description about the form and its fields. Your task is to identify all the fields the form should have based on the given description along with their type such as text, email, text area, number and so on. Once you have found all the fields and figured out their types, you have to respond the data in JSON format as is shown in the next example.
    Example Response Format:
    {
        "title": "Form title",
        "description": "A description about what form is for",
        "fields": [
            { "label": "Field 1 Name", "type": "text" },
            { "label": "Field 2 Name", "type": "number" }
        ]
    }

    You should only respond in JSON format. If the given data is not about a form then respond with an invalid data message.
    Description:

    """

    prompt = prompt + text
    gpt_4_turbo = Model(
        "https://clarifai.com/openai/chat-completion/models/gpt-4-turbo")
    inference_params = dict(temperature=0.2, max_tokens=100)

    # Model Predict
    model_prediction = gpt_4_turbo.predict_by_bytes(
        prompt.encode(), input_type="text")

    raw_text = model_prediction.outputs[0].data.text.raw

    clean_text = raw_text.replace("```", "")
    clean_text = clean_text.replace("json", "", 1)

    schema = clean_text
    return schema


def render_form(schema, off=True):
    st.write(schema["title"])
    st.write(schema["description"])

    for idx, i in enumerate(schema["fields"]):
        if i["type"] == "text" or i["type"] == "email":
            st.text_input(
                label=i["label"], disabled=off)
        if i["type"] == "number":
            st.number_input(
                label=i["label"], disabled=off)
        if i["type"] == "textarea":
            st.text_area(label=i["label"], disabled=off)


def render_form_live(schema, off=False):
    st.write(schema["title"])
    st.write(schema["description"])

    for idx, i in enumerate(schema["fields"]):
        if i["type"] == "text" or i["type"] == "email":
            st.text_input(
                label=i["label"], disabled=off, key=f"f_{idx}")
        if i["type"] == "number":
            st.number_input(
                label=i["label"], disabled=off, key=f"f_{idx}")
        if i["type"] == "textarea":
            st.text_area(label=i["label"], disabled=off, key=f"f_{idx}")


if st.session_state.stage == 0:

    with st.expander("Upload an image"):

        image_file = st.file_uploader(
            "Upload Form Image", type=["png", "jpg", "jpeg"])

        if image_file is not None:
            st.image(Image.open(image_file), width=300)

            """
            Now let's use AI to understand the image and create an actual form that you can work with.
            """
            with st.spinner("Working..."):
                result = get_schema_from_image(image_file)
            schema = json.loads(result)

            st.session_state.schema = schema
            st.button("Continue", key="btn-image",
                      on_click=set_state, args=[1])

    with st.expander("Describe your form in words"):
        section = st.empty()
        with section.container():
            with st.form("text form", clear_on_submit=True):
                query = st.text_area(
                    "Tell us about the form your want to create", max_chars=256, key="text-input")
                submit = st.form_submit_button("Submit")

        if submit:
            section.empty()
            with st.spinner("Working..."):
                result = get_schema_from_text(query)
            schema = json.loads(result)
            st.session_state.schema = schema

            st.button("Continue", key="btn-text", on_click=set_state, args=[1])

        st.divider()
        st.write("Or Copy from one the example below.")
        for ti in st.session_state.text_inputs:
            st.code(ti, language="markdown")


if st.session_state.stage == 1:
    # Form Builder from schema
    if "Invalid" in st.session_state.schema["title"]:
        st.warning(
            """
            Sorry! We couldn't build a form based on your input. Please make sure that you upload an image with a form or enter details such as what fields it should have while describing your form. This app can only handle form related inputs.
            """
        )
        st.button("Try Again", on_click=set_state, args=[0])
    else:
        """
        Here is a preview of a form built based on your input. If you want to fill out this form then click on the fill form button below the form preview.
        """
        with st.form("form1"):
            render_form(st.session_state.schema)
            submit = st.form_submit_button("Submit", disabled=True)

        st.button("Try Again", on_click=set_state, args=[0])
        st.button("Fill Form", type="primary", on_click=set_state, args=[2])

if st.session_state.stage == 2:
    """
    ### Fill out the Form
    """
    form = st.form("form2", clear_on_submit=True)
    with form.container():
        render_form_live(st.session_state.schema, off=False)
        submit = st.form_submit_button("Submit")

    if submit:
        st.info("Thank you for your response.")
        st.info("Your response")

        form_data = {}
        for i in range(len(st.session_state.schema["fields"])):
            key = f"f_{i}"
            label = st.session_state.schema["fields"][i]["label"]
            form_data[label] = st.session_state.get(key)
        st.table(form_data)

        st.button("Start Over", type="primary",
                  on_click=set_state, args=[0])
