# flask server code
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from amadeus import Client, ResponseError
import config
import json
app = Flask(__name__)
api = Api(app)

# a class for a particular resource : Default


class Hello(Resource):

    def get(self):

        return jsonify({'message': 'hello Welcome to our Travel Companion'})


class FlightResult(Resource):

    # corresponds to the GET request.
    # this function is called whenever there
    # is a GET request for this resource
    def get(self):

        return jsonify({'message': 'hello world'})

        # Corresponds to POST request
    def post(self):

        data = request.get_json()     # status code
        # Authorize
        # call
        # prepare result
        amadeus_client = config.get_client()
        try:
            '''
            Find best flight offers from Madrid to New York
            '''
            response = amadeus_client.shopping.flight_offers.get(origin='MAD', destination='NYC', departureDate='2020-06-01')
            print(type(response.data))
            return jsonify({'return': response.data})
        # print(response.data)
        except ResponseError as error:
            raise error

# a class for a particular resource : Square


class Square(Resource):

    def get(self, num):

        return jsonify({'square': num**2})

api.add_resource(Hello, '/')
api.add_resource(FlightResult, '/FLightStatus')
api.add_resource(Square, '/square/<int:num>')

if __name__ == '__main__':

    app.run(debug=True)
