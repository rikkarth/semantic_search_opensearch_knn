print("Hello from asset-fetch!")
    
os_client = opensearch()

os_client.indices.create(index="test_index_01", body={
    "settings": {
        "index.knn": True,
        "number_of_shards": 5,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "values": {
                "type": "knn_vector",
                "dimension": 256
            }
        }
    }
})