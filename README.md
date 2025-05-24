## Abstruct

We propose DailyQA, an automatically updated dynamic dataset that updates questions weekly and contains answers to questions on any given date.
DailyQA utilizes daily updates from Wikipedia revision logs to implement a fully automated pipeline of data filtering, query generation synthesis, quality checking, answer extraction, and query classification. 
The benchmark requires large language models (LLMs) to process and answer questions involving fast-changing factual data and covering multiple domains. 
We evaluate several open-source and closed-source LLMs using different RAG pipelines with web search augmentation. 
We compare the ability of different models to process time-sensitive web information and find that rerank of web retrieval results is critical.
Our results indicate that LLMs still face significant challenges in handling frequently updated information, suggesting that DailyQA benchmarking provides valuable insights into the direction of progress for LLMs and RAG systems.

## Data Introduction

* data.query: The generated queries and the metadata of the wiki infoboxs. 

    * "query": The generated query.

    * "classify": The domain of the query.

* data.qa: The queries and answers for specific dates.

* scripts.get_answer.sh: The script for obtaining the answers for the specified dates. You can modify "search_dates" to specify the dates.


