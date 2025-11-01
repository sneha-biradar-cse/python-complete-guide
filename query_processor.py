"""
Query Processor for Agricultural Q&A System
Uses NLP techniques to understand user questions and route to appropriate data sources
"""

import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class QueryIntent:
    """Represents the understood intent of a user query"""
    intent_type: str  # e.g., "crop_production", "weather", "price", "comparison"
    entities: Dict[str, Any]  # Extracted entities like crop names, locations, dates
    data_sources: List[str]  # Which data sources to query
    confidence: float  # Confidence score of the intent classification


class QueryProcessor:
    """Processes natural language queries and extracts structured information"""
    
    def __init__(self):
        # Define keywords for different intent types
        self.intent_keywords = {
            "crop_production": ["production", "yield", "harvest", "grow", "cultivate", "produce"],
            "crop_price": ["price", "msp", "cost", "rate", "value", "minimum support price"],
            "crop_area": ["area", "hectare", "land", "acreage", "cultivation area"],
            "weather": ["weather", "rainfall", "temperature", "rain", "climate", "humidity", "wind"],
            "comparison": ["compare", "difference", "versus", "vs", "better", "higher", "lower"],
            "statistics": ["total", "average", "maximum", "minimum", "sum", "mean"]
        }
        
        # Define entity patterns
        self.crop_names = [
            "rice", "wheat", "cotton", "sugarcane", "maize", "corn", "barley",
            "jowar", "bajra", "ragi", "pulses", "soybean", "groundnut", "mustard",
            "sunflower", "potato", "onion", "tomato", "tea", "coffee", "rubber"
        ]
        
        self.state_names = [
            "punjab", "haryana", "uttar pradesh", "up", "madhya pradesh", "mp",
            "rajasthan", "gujarat", "maharashtra", "karnataka", "tamil nadu",
            "andhra pradesh", "telangana", "west bengal", "bihar", "odisha",
            "assam", "kerala", "jharkhand", "chhattisgarh"
        ]
        
        self.seasons = ["kharif", "rabi", "zaid", "summer", "winter", "monsoon"]
        
        # Year pattern
        self.year_pattern = r'\b(19|20)\d{2}\b'
    
    def process_query(self, query: str) -> QueryIntent:
        """
        Process a natural language query and extract intent and entities
        
        Args:
            query: User's natural language question
            
        Returns:
            QueryIntent object with extracted information
        """
        query_lower = query.lower()
        
        # Extract intent
        intent_type, confidence = self._classify_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Determine which data sources to query
        data_sources = self._determine_data_sources(intent_type, entities)
        
        return QueryIntent(
            intent_type=intent_type,
            entities=entities,
            data_sources=data_sources,
            confidence=confidence
        )
    
    def _classify_intent(self, query: str) -> Tuple[str, float]:
        """Classify the intent of the query"""
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return "general", 0.5
        
        # Get the intent with highest score
        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]
        
        # Calculate confidence (normalized)
        confidence = min(max_score / 3.0, 1.0)
        
        return best_intent, confidence
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query"""
        entities = {}
        
        # Extract crop names
        for crop in self.crop_names:
            if crop in query:
                entities["crop"] = crop.title()
                break
        
        # Extract state names
        for state in self.state_names:
            if state in query:
                # Normalize state names
                state_normalized = state.title()
                if state == "up":
                    state_normalized = "Uttar Pradesh"
                elif state == "mp":
                    state_normalized = "Madhya Pradesh"
                entities["state"] = state_normalized
                break
        
        # Extract year
        year_match = re.search(self.year_pattern, query)
        if year_match:
            entities["year"] = int(year_match.group())
        
        # Extract season
        for season in self.seasons:
            if season in query:
                entities["season"] = season.title()
                break
        
        # Extract location (for weather queries)
        if "location" not in entities and "state" in entities:
            entities["location"] = entities["state"]
        
        return entities
    
    def _determine_data_sources(self, intent_type: str, entities: Dict[str, Any]) -> List[str]:
        """Determine which data sources to query based on intent and entities"""
        sources = []
        
        # Weather-related intents always need weather data
        if intent_type == "weather" or "season" in entities:
            sources.append("weather")
        
        # Crop-related intents need agriculture data
        if intent_type in ["crop_production", "crop_price", "crop_area"] or "crop" in entities:
            sources.append("agriculture")
        
        # Comparison queries might need both sources
        if intent_type == "comparison":
            sources.extend(["agriculture", "weather"])
        
        # If no specific sources identified, query all
        if not sources:
            sources = ["agriculture", "weather"]
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(sources))
    
    def build_query_params(self, query_intent: QueryIntent) -> Dict[str, Dict[str, Any]]:
        """
        Build query parameters for each data source based on extracted intent
        
        Args:
            query_intent: The processed query intent
            
        Returns:
            Dictionary mapping data source names to their query parameters
        """
        params = {}
        
        for source in query_intent.data_sources:
            source_params = {}
            
            if source == "agriculture":
                if "crop" in query_intent.entities:
                    source_params["crop"] = query_intent.entities["crop"]
                if "state" in query_intent.entities:
                    source_params["state"] = query_intent.entities["state"]
                if "year" in query_intent.entities:
                    source_params["year"] = query_intent.entities["year"]
            
            elif source == "weather":
                if "location" in query_intent.entities:
                    source_params["location"] = query_intent.entities["location"]
                elif "state" in query_intent.entities:
                    source_params["location"] = query_intent.entities["state"]
                if "season" in query_intent.entities:
                    source_params["season"] = query_intent.entities["season"]
            
            params[source] = source_params
        
        return params
    
    def generate_query_summary(self, query_intent: QueryIntent) -> str:
        """Generate a human-readable summary of the understood query"""
        summary_parts = []
        
        summary_parts.append(f"Intent: {query_intent.intent_type.replace('_', ' ').title()}")
        
        if query_intent.entities:
            entity_strs = [f"{k}: {v}" for k, v in query_intent.entities.items()]
            summary_parts.append(f"Entities: {', '.join(entity_strs)}")
        
        summary_parts.append(f"Data Sources: {', '.join(query_intent.data_sources)}")
        summary_parts.append(f"Confidence: {query_intent.confidence:.2f}")
        
        return " | ".join(summary_parts)


def test_query_processor():
    """Test the query processor with sample queries"""
    processor = QueryProcessor()
    
    test_queries = [
        "What is the rice production in Punjab?",
        "Show me wheat prices in 2024",
        "What is the weather like in Gujarat?",
        "Compare rice and wheat production",
        "What is the rainfall in West Bengal during monsoon?"
    ]
    
    print("Testing Query Processor\n" + "="*50)
    for query in test_queries:
        print(f"\nQuery: {query}")
        intent = processor.process_query(query)
        print(processor.generate_query_summary(intent))
        params = processor.build_query_params(intent)
        print(f"Query Params: {params}")


if __name__ == "__main__":
    test_query_processor()
