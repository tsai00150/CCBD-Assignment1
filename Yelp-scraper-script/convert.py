import json
from datetime import datetime

def convert(dict_list, cuisine, offset):
    for round in [0,25]:    
        put_requests = []
        for d in dict_list[round:round+25]:
            item = {}
            item["id"] = {"S": d.get('id')}
            item["name"] = {"S": d.get('name')}

            coord = d.get('coordinates')
            if coord:
                item["coordinates"] = {"M": {
                    "latitude": {"N": str(coord["latitude"])},
                    "longitude": {"N": str(coord['longitude'])}
                    }}
            else:
                item["coordinates"] = {"M": None}

            item["review_count"] = {"N": str(d.get('review_count'))}
            item["rating"] = {"N": str(d.get('rating'))}
            item["zip_code"] = {"N": d.get('location', {}).get('zip_code')}

            address = d.get('location', {}).get('display_address')
            L = []
            for e in address:
                L.append({"S": e})
            item["address"] = {"L": L}

            now = datetime.now()
            item["insertedAtTimestamp"] = {"S": str(now)}

            put_requests.append({"PutRequest":{"Item": item}})

            opensearch = open('opensearch.json', 'r')
            cur_id = len(opensearch.readlines())//2

            with open("opensearch.json", "a") as outfile:
                outfile.write(json.dumps({"index": {"_index": "restaurants", \
                    "_id": cur_id+1, "_type" : "Restaurant"}})+'\n')
                outfile.write(json.dumps({"RestaurantID": d.get('id'), "Cuisine": cuisine})+'\n')

        main_dict = {'yelp-restaurants': put_requests}

        app_json = json.dumps(main_dict, indent=2)
        with open("jsons/"+ cuisine.replace(" ", "")+str(offset)+str(round)+".json", "w") as outfile:
            outfile.write(app_json)