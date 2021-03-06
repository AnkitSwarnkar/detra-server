# flask server code
from flask import Flask, jsonify, request, render_template
from flask_restful import Resource, Api
from amadeus import Client, ResponseError
import config
import math
import json
app = Flask(__name__, template_folder='templates', static_folder="static", static_url_path='')
api = Api(app)


@app.route('/group-chat')
def hello():
    data = {'app_id': "1d595486132b4f129d960346a5dfefb2",
            'channel': "test",
            'token':"0061d595486132b4f129d960346a5dfefb2IACrK2g+caVtV5Sm9Lz7Y6pUmhu5YpKJTewx/vT9r2CJBgx+f9gAAAAAEADB6e0i4dhJXgEAAQDg2Ele"}
    return render_template('indexdummy.html', data=data)


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
            return jsonify({'return': response.data})
        # print(response.data)
        except ResponseError as error:
            raise error

# a class for a particular resource : Square

class Square(Resource):

    def get(self, num):

        return jsonify({'square': num**2})


# a class for a particular resource : flightsearch
class FlightSearch(Resource):

    # corresponds to the GET request.
    # this function is called whenever there
    # is a GET request for this resource
    def get(self):

        return jsonify({'message': 'hello world'})

    def get_final_dest(self, flight_segments):
        self.flight_segments = flight_segments
        final_dest = ""
        # overwrite final_dest, till we arrived at last segment (Hacky :)
        for segment in flight_segments:
            final_dest = segment["flightSegment"]["arrival"]["iataCode"]
        return final_dest

    def create_combinations_of_top_x_dictionaries(self, trips_outbound_data,trips_inbound_data, x):
        self.trips_outbound_data = trips_outbound_data
        self.trips_inbound_data = trips_inbound_data
        self.x = x

        roundtrip_combinations = []
        for outbound_idx in range(0, x):
            for inbound_idx in range(0,x):
                roundtrip_dict = {}
                roundtrip_dict.update(trips_outbound_data[outbound_idx])
                roundtrip_dict.update(trips_inbound_data[inbound_idx])
                roundtrip_combinations.append(roundtrip_dict)
        return roundtrip_combinations

        # Corresponds to POST request
    def post(self):
        # constant variables
        num_of_return_flights = 30

        data_from_frontend = request.get_json()     # status code
        data_from_frontend_dict = dict(data_from_frontend)
        print(data_from_frontend_dict)
        # Authorize
        # call
        # prepare result
        amadeus_client = config.get_client()

        # request data from amadeus
        try:
            '''
            Find best flight offers for outbound flight
            '''
            response_outbound = amadeus_client.shopping.flight_offers.get(origin=data_from_frontend_dict['origin'],
                                                                 destination=data_from_frontend_dict['destination'],
                                                                 departureDate=data_from_frontend_dict['fromDate'])
            '''
            Find best flight offers for inbound flight
            '''
            response_inbound = amadeus_client.shopping.flight_offers.get(origin=data_from_frontend_dict['destination'],
                                                                        destination=data_from_frontend_dict['origin'],
                                                                        departureDate=data_from_frontend_dict['toDate'])
        except ResponseError as error:
            print("Amadeus Error")
            raise error

        # preprocess and filter data
        # data_outbound = response_outbound.data
        trips_outbound_data = []
        trips_inbound_data = []
        # extract data for sending to frontend
        # flights data outbound
        for flight in response_outbound.data:
            trip_outbound_data = {}
            trip_outbound_data["departureOrigin"] = flight["offerItems"][0]["services"][0]["segments"][0]["flightSegment"]["departure"]["iataCode"]
            trip_outbound_data["departureDestination"] = self.get_final_dest(flight["offerItems"][0]["services"][0]["segments"])
            trip_outbound_data["departureBoardingDateTime"] = flight["offerItems"][0]["services"][0]["segments"][0]["flightSegment"]["departure"]["at"]
            trip_outbound_data["departurePrice"] = str(round(float(flight["offerItems"][0]["price"]["total"]) + float(flight["offerItems"][0]["price"]["totalTaxes"]),2))
            trips_outbound_data.append(trip_outbound_data)
            # print(trips_outbound_data)
        # flights data inbound
        for flight in response_inbound.data:
            trip_inbound_data = {}
            trip_inbound_data["returnOrigin"] = flight["offerItems"][0]["services"][0]["segments"][0]["flightSegment"]["departure"]["iataCode"]
            trip_inbound_data["returnDestination"] = self.get_final_dest(flight["offerItems"][0]["services"][0]["segments"])
            trip_inbound_data["returnBoardingDateTime"] = flight["offerItems"][0]["services"][0]["segments"][0]["flightSegment"]["departure"]["at"]
            trip_inbound_data["returnPrice"] = str(round(float(flight["offerItems"][0]["price"]["total"]) + float(flight["offerItems"][0]["price"]["totalTaxes"]),2))
            trips_inbound_data.append(trip_inbound_data)
        # combine in and outbound flights
        # sort outbount & inbound lists
        trips_outbound_data.sort(key=lambda k: float(k['departurePrice']))
        trips_inbound_data.sort(key=lambda k: float(k['returnPrice']))
        # create all combinations of top X in- and outbound flights
        roundtrip_combinations = self.create_combinations_of_top_x_dictionaries(trips_outbound_data, trips_inbound_data, math.ceil(math.sqrt(num_of_return_flights)))
        # sort combinations
        roundtrip_combinations.sort(key=lambda k: float(k['departurePrice']) + float(k['returnPrice']))
        # return best(first) Y combinations
        #  limit output roundtrips
        roundtrip_combinations_limited = []
        for x in range(0, num_of_return_flights-1):
            roundtrip_combinations_limited.append(roundtrip_combinations[x])
        # print
        # for round_trip in roundtrip_combinations_limited:
        #     print(round_trip)
            # print(float(round_trip["departurePrice"]) + float(round_trip["returnPrice"]))

        # send data to frontend
        return roundtrip_combinations_limited


api.add_resource(FlightSearch, '/tripanion/flightsearch')
api.add_resource(FlightResult, '/FlightStatus')
api.add_resource(Square, '/square/<int:num>')

if __name__ == '__main__':

    app.run(debug=True)
