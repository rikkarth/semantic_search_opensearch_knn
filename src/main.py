from fastapi import FastAPI

from db_provider import opensearch

app = FastAPI()


@app.get("/")
def test_endpoint():
    os_client = opensearch()

    try:
        resp = os_client.indices.create(
            index="test_index_01",
            body={
                "settings": {
                    "index.knn": True,
                    "number_of_shards": 5,
                    "number_of_replicas": 0,
                    "default_pipeline": "nlp-ingest-pipeline",
                },
                "mappings": {
                    "properties": {
                        # The properties of our document
                        "passage_embedding": {
                            "type": "knn_vector",
                            "dimension": 768,
                            "method": {
                                "engine": "lucene",
                                "space_type": "cosinesimil",
                                "name": "hnsw",
                                "parameters": {},
                            },
                        },
                        "passage_text": {"type": "text"},
                        # redundant but may be useful
                        "id": {"type": "text"},
                    }
                },
            },
        )
        print(resp)
    except Exception as e:
        # index may exist for now we just print error and do nothing
        print("Index already exists")

    try:
        print("Searching")
        query = {
            "_source": {"exclude": ["passage_embedding"]},
            "min_score": 0.7,
            "query": {
                "hybrid": {
                    "queries": [
                        {
                            "match": {
                                "passage_text": {
                                    "query": "Dragon Scales, Wyrm Scales, Dragonhide, Dragon Armor, Scaled Dragons"
                                }
                            }
                        },
                        {
                            "neural": {
                                "passage_embedding": {
                                    "query_text": "Dragon Scales, Wyrm Scales, Dragonhide, Dragon Armor, Scaled Dragons",
                                    "model_id": "SKE4F5kBTyoUJ0useXad",
                                    "k": 5,
                                }
                            }
                        },
                    ]
                }
            },
        }
        response = os_client.search(body=query, index="test_index_01", params={"search_pipeline": "nlp-search-pipeline"})

        return response
    except Exception as e:
        print(e)
        return {"error": "db probably down"}
