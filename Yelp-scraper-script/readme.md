Instructions:
1. Execute yelp-scrape.py
```
python yelp-scrape.py
```
2. The data that goes to DynamoDB is in the `jsons` file, and to batch upload them, just click on `upload.bat` to upload all the json file. (Only works in Windows, essentially it runs `aws dynamodb batch-write-item --request-items file://<filename.json>` for every json file in `jsons`.)
3. The data that goes to the opensearch instance can be found at `opensearch.json`. For Windows, first execute `Remove-item alias:curl`, then `curl -XPOST -u <username>:<password> <opensearch domain endpoint>/_bulk --data-binary '@opensearch.json' -H 'Content-Type: application/json'`