import io
import json
import os

from flask import Flask, render_template, request

app = Flask(__name__)

common = {
    'first_name': 'Vitalii',
    'last_name': 'Shmatolokha',
}

if __name__ == "__main__":
    print("running py app")
    app.run(host="127.0.0.1", port=5000, debug=True)