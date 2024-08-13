import os
from dataclasses import dataclass
from typing import List

import requests
from teams.ai.tokenizers import Tokenizer
from teams.ai.data_sources import DataSource
from teams.state.state import TurnContext
from teams.state.memory import Memory

@dataclass
class Result:
    output: str
    length: int
    too_long: bool

class MyDataSource(DataSource):
    """
    A data source that searches through Confluence for a given query.
    """

    def __init__(self, name, api_key=None, base_url=None):
        """
        Creates a new instance of the MyDataSource instance.
        Initializes the data source.
        """
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self._data = []
        
    def name(self):
        return self.name

    async def render_data(self, context: TurnContext, memory: Memory, tokenizer: Tokenizer, maxTokens: int):
        """
        Renders the data source as a string of text.
        The returned output should be a string of text that will be injected into the prompt at render time.
        """
        query = memory.get('temp.input')
        if not query:
            return Result('', 0, False)

        # Fetch data from Confluence
        result = self.search_confluence(query)
        
        return Result(self.formatDocument(result), len(result), False) if result else Result('', 0, False)

    def search_confluence(self, query: str) -> str:
        """
        Search for the query in Confluence.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        params = {
            'cql': f'text ~ "{query}"',
        }
        
        #response = requests.get(f'{self.base_url}/dosearchsite.action?queryString=', headers=headers, params=params)
        response = requests.get(f'{self.base_url}/rest/api/content/search', headers=headers, params=params)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        combined_results = ' '.join([result.get('title', {}) for result in results[:100]])
        
        return combined_results

    def formatDocument(self, result: str) -> str:
        """
        Formats the result string.
        """
        return f"<context>{result}</context>"