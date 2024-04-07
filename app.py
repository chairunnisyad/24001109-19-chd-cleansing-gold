from flask import Flask, jsonify, request
import re
import pandas as pd
import sqlite3
from flasgger import Swagger, LazyJSONEncoder, swag_from

app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info={
        "title": "API Documentation for Data Processing and Modelling",
        "version": "1.0.0",
        "description": "Dokumentasi API untuk Data Processing and Modelling"
    },
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "docs",
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

connection = sqlite3.connect('/Users/admin/Documents/Binar_challenge/database.db', check_same_thread=False)
connection.execute('''CREATE TABLE IF NOT EXISTS output_text (table_1 varchar(255), table_2 varchar(255));''')

kamus_abusive = pd.read_csv('abusive.csv', encoding='latin-1')
kamusalay = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
kamusalay_dict = kamusalay.rename(columns={0: 'alay', 1: 'normal'})


def lowercase(text):
    return text.lower()


@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route("/", methods=['GET'])
def hello_world():
    json_response = {
        "status_code": 200,
        "description": "Hello, Yess berhasil!",
        "data": "Hello dunia!"
    }
    response_data = jsonify(json_response)
    return response_data


def remove_nonaplhanumeric(text):
    cleaned_text = re.sub('[^0-9a-zA-Z]+', ' ', text)
    return cleaned_text


def remove_unicode(text):
    text = re.sub(r'\bx[a-fA-F0-9]{2}\b', '', text)
    text = re.sub(r'\bx([a-fA-F0-9]{2})', '', text)
    return text


def remove_unnecessary_char(text):
    text = re.sub('\n', ' ', str(text))
    text = re.sub('\t', ' ', str(text))
    text = re.sub('rt', ' ', str(text))
    text = re.sub('user', ' ', str(text))
    text = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))', ' ', text)
    text = re.sub('   +', ' ', str(text))
    text = text.strip()
    text = re.sub(r'\d+', '', str(text))
    return text


# Membuat kamus alay dari data yang didapat
kamusalay = dict(zip(kamusalay_dict['alay'], kamusalay_dict['normal']))


def normalize_alay(text):
    return ' '.join([kamusalay[word] if word in kamusalay else word for word in text.split()])


def preprocess(text):
    text = lowercase(text)
    text = remove_unnecessary_char(text)
    text = remove_unicode(text)
    text = remove_nonaplhanumeric(text)
    text = normalize_alay(text)
    return text

@swag_from("docs/text_cleansing.yml", methods=['POST'])
@app.route('/text_cleansing', methods=['POST'])
def text_cleansing():
    text = request.form.get("text")
    cleaned_text = preprocess(text)

    # Insert output text into the database
    connection.execute("INSERT INTO output_text (table_1) VALUES ('" + cleaned_text + "')")

    # Prepare JSON response
    json_response = {
        "status_code": 200,
        "description": "Teks yang sudah dibersihkan!",
        "data": cleaned_text,
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text_processing', methods=['POST'])
def text_processing():
    # Upload File
    file = request.files.getlist('file')[0]

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file, encoding="latin-1")
    print(file)
    print(df.head())


    # Convert a column named 'Tweet' from a Pandas DataFrame into a Python list.
    texts = df['Tweet'].to_list()

    # Looping List
    new_text = []
    for text_input in texts:
        cleaned_text = preprocess(text_input)

        # Insert output text into the database
        connection.execute("INSERT INTO output_text (table_2) VALUES ('" + cleaned_text + "')")
        connection.commit()

        new_text.append(cleaned_text)

    json_response = {
        "status_code": 200,
        "description": "Teks yang sudah dibersihkan!",
        "data": new_text,
    }

    return jsonify(json_response)


if __name__ == '__main__':
    app.run()
