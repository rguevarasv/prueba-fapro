import unittest

import requests
from flask import json

from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.url = 'http://127.0.0.1:5000/uf'
        self.app = app.test_client()

    def test_uf(self):
        data = {'dia': 1, 'mes': 1, 'anio': "2022"}
        response = requests.get(self.url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        expected_response = {"valor": "31.001,72"}
        self.assertEqual(json.loads(response.text), expected_response)


if __name__ == '__main__':
    unittest.main()
