from typing import List

from elasticsearch import Elasticsearch
from llama_index.schema import TextNode
from llama_index import QueryBundle
from llama_index.schema import NodeWithScore
from llama_index.retrievers import BaseRetriever

from preprocess.get_text_id_mapping import text_node_id_mapping


class CustomBM25Retriever(BaseRetriever):
    """Custom retriever for elasticsearch with bm25"""
    def __init__(self, top_k) -> None:
        """Init params."""
        super().__init__()
        self.es_client = Elasticsearch("http://localhost:9200")
        self.top_k = top_k

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        result = []
        # 查询数据(全文搜索)
        dsl = {
            'query': {
                'match': {
                    'content': query_bundle.query_str
                }
            },
            "size": self.top_k
        }
        search_result = self.es_client.search(index='docs_qa', body=dsl)
        if search_result['hits']['hits']:
            for record in search_result['hits']['hits']:
                text = record['_source']['content']
                node_with_score = NodeWithScore(node=TextNode(text=text, id_=text_node_id_mapping[text]),
                                                score=record['_score'])
                result.append(node_with_score)

        return result


if __name__ == '__main__':
    from pprint import pprint
    custom_bm25_retriever = CustomBM25Retriever(top_k=3)
    query = "叙利亚队"
    t_result = custom_bm25_retriever.retrieve(str_or_query_bundle=query)
    pprint(t_result)
