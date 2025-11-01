"""
Response Generator for Agricultural Q&A System
Synthesizes answers from multiple data sources with proper citations
"""

from typing import Dict, List, Any
from query_processor import QueryIntent
from datetime import datetime


class ResponseGenerator:
    """Generates coherent responses from multiple data sources with citations"""
    
    def __init__(self):
        self.response_templates = {
            "crop_production": self._generate_production_response,
            "crop_price": self._generate_price_response,
            "crop_area": self._generate_area_response,
            "weather": self._generate_weather_response,
            "comparison": self._generate_comparison_response,
            "general": self._generate_general_response
        }
    
    def generate_response(
        self,
        query: str,
        query_intent: QueryIntent,
        data_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive response with citations
        
        Args:
            query: Original user query
            query_intent: Processed query intent
            data_results: Results from data sources
            
        Returns:
            Dictionary containing answer, citations, and metadata
        """
        # Get the appropriate response generator
        generator_func = self.response_templates.get(
            query_intent.intent_type,
            self._generate_general_response
        )
        
        # Generate the response
        answer = generator_func(query_intent, data_results)
        
        # Collect all citations
        citations = self._collect_citations(data_results)
        
        # Generate metadata
        metadata = {
            "query": query,
            "intent": query_intent.intent_type,
            "entities": query_intent.entities,
            "confidence": query_intent.confidence,
            "sources_queried": query_intent.data_sources,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "answer": answer,
            "citations": citations,
            "metadata": metadata
        }
    
    def _generate_production_response(
        self,
        query_intent: QueryIntent,
        data_results: Dict[str, Any]
    ) -> str:
        """Generate response for crop production queries"""
        answer_parts = []
        
        # Check agriculture data
        if "agriculture" in data_results and data_results["agriculture"].get("results"):
            results = data_results["agriculture"]["results"]
            
            if len(results) == 0:
                answer_parts.append("No production data found for the specified criteria.")
            else:
                for result in results:
                    crop = result.get("crop", "Unknown crop")
                    state = result.get("state", "Unknown state")
                    year = result.get("year", "Unknown year")
                    production = result.get("production_tonnes", 0)
                    area = result.get("area_hectares", 0)
                    yield_val = result.get("yield_kg_per_hectare", 0)
                    
                    answer_parts.append(
                        f"**{crop} in {state} ({year}):**\n"
                        f"- Production: {production:,.0f} tonnes\n"
                        f"- Cultivation Area: {area:,.0f} hectares\n"
                        f"- Yield: {yield_val:,.0f} kg/hectare"
                    )
                    
                    # Add citation reference
                    answer_parts.append(
                        f"*[Source: Ministry of Agriculture & Farmers Welfare]*"
                    )
        
        # Check if weather data is relevant
        if "weather" in data_results and data_results["weather"].get("results"):
            weather_results = data_results["weather"]["results"]
            if weather_results:
                answer_parts.append("\n**Related Weather Information:**")
                for weather in weather_results[:2]:  # Limit to 2 weather records
                    location = weather.get("location", "Unknown")
                    rainfall = weather.get("rainfall_mm", 0)
                    temp = weather.get("temperature_celsius", 0)
                    
                    answer_parts.append(
                        f"- {location}: {rainfall:.1f}mm rainfall, {temp:.1f}°C temperature"
                    )
                
                answer_parts.append("*[Source: India Meteorological Department]*")
        
        return "\n\n".join(answer_parts) if answer_parts else "No data available for your query."
    
    def _generate_price_response(
        self,
        query_intent: QueryIntent,
        data_results: Dict[str, Any]
    ) -> str:
        """Generate response for crop price queries"""
        answer_parts = []
        
        if "agriculture" in data_results and data_results["agriculture"].get("results"):
            results = data_results["agriculture"]["results"]
            
            if len(results) == 0:
                answer_parts.append("No price data found for the specified criteria.")
            else:
                for result in results:
                    crop = result.get("crop", "Unknown crop")
                    state = result.get("state", "Unknown state")
                    msp = result.get("msp_rupees_per_quintal", 0)
                    year = result.get("year", "Unknown year")
                    
                    answer_parts.append(
                        f"**{crop} MSP in {state} ({year}):**\n"
                        f"- Minimum Support Price: ₹{msp:,.0f} per quintal"
                    )
                    
                    answer_parts.append(
                        f"*[Source: Ministry of Agriculture & Farmers Welfare]*"
                    )
        
        return "\n\n".join(answer_parts) if answer_parts else "No price data available."
    
    def _generate_area_response(
        self,
        query_intent: QueryIntent,
        data_results: Dict[str, Any]
    ) -> str:
        """Generate response for crop area queries"""
        answer_parts = []
        
        if "agriculture" in data_results and data_results["agriculture"].get("results"):
            results = data_results["agriculture"]["results"]
            
            for result in results:
                crop = result.get("crop", "Unknown crop")
                state = result.get("state", "Unknown state")
                area = result.get("area_hectares", 0)
                year = result.get("year", "Unknown year")
                
                answer_parts.append(
                    f"**{crop} cultivation area in {state} ({year}):**\n"
                    f"- Total Area: {area:,.0f} hectares"
                )
                
                answer_parts.append(
                    f"*[Source: Ministry of Agriculture & Farmers Welfare]*"
                )
        
        return "\n\n".join(answer_parts) if answer_parts else "No area data available."
    
    def _generate_weather_response(
        self,
        query_intent: QueryIntent,
        data_results: Dict[str, Any]
    ) -> str:
        """Generate response for weather queries"""
        answer_parts = []
        
        if "weather" in data_results and data_results["weather"].get("results"):
            results = data_results["weather"]["results"]
            
            if len(results) == 0:
                answer_parts.append("No weather data found for the specified criteria.")
            else:
                for result in results:
                    location = result.get("location", "Unknown location")
                    date = result.get("date", "Unknown date")
                    temp = result.get("temperature_celsius", 0)
                    rainfall = result.get("rainfall_mm", 0)
                    humidity = result.get("humidity_percent", 0)
                    wind = result.get("wind_speed_kmph", 0)
                    season = result.get("season", "Unknown")
                    
                    answer_parts.append(
                        f"**Weather in {location} ({date}):**\n"
                        f"- Temperature: {temp:.1f}°C\n"
                        f"- Rainfall: {rainfall:.1f}mm\n"
                        f"- Humidity: {humidity}%\n"
                        f"- Wind Speed: {wind:.1f} km/h\n"
                        f"- Season: {season}"
                    )
                    
                    answer_parts.append(
                        f"*[Source: India Meteorological Department]*"
                    )
        
        return "\n\n".join(answer_parts) if answer_parts else "No weather data available."
    
    def _generate_comparison_response(
        self,
        query_intent: QueryIntent,
        data_results: Dict[str, Any]
    ) -> str:
        """Generate response for comparison queries"""
        answer_parts = []
        
        if "agriculture" in data_results and data_results["agriculture"].get("results"):
            results = data_results["agriculture"]["results"]
            
            if len(results) >= 2:
                answer_parts.append("**Comparison:**\n")
                
                for result in results:
                    crop = result.get("crop", "Unknown")
                    state = result.get("state", "Unknown")
                    production = result.get("production_tonnes", 0)
                    yield_val = result.get("yield_kg_per_hectare", 0)
                    
                    answer_parts.append(
                        f"- **{crop} ({state}):** {production:,.0f} tonnes production, "
                        f"{yield_val:,.0f} kg/ha yield"
                    )
                
                answer_parts.append("\n*[Source: Ministry of Agriculture & Farmers Welfare]*")
            else:
                answer_parts.append("Insufficient data for comparison.")
        
        return "\n\n".join(answer_parts) if answer_parts else "No comparison data available."
    
    def _generate_general_response(
        self,
        query_intent: QueryIntent,
        data_results: Dict[str, Any]
    ) -> str:
        """Generate general response when intent is unclear"""
        answer_parts = []
        
        # Try to show any available data
        for source_name, source_data in data_results.items():
            if source_data.get("results"):
                results = source_data["results"]
                
                if source_name == "agriculture":
                    answer_parts.append("**Agricultural Data:**")
                    for result in results[:3]:  # Limit to 3 results
                        crop = result.get("crop", "Unknown")
                        state = result.get("state", "Unknown")
                        production = result.get("production_tonnes", 0)
                        answer_parts.append(
                            f"- {crop} in {state}: {production:,.0f} tonnes"
                        )
                    answer_parts.append("*[Source: Ministry of Agriculture & Farmers Welfare]*")
                
                elif source_name == "weather":
                    answer_parts.append("\n**Weather Data:**")
                    for result in results[:3]:  # Limit to 3 results
                        location = result.get("location", "Unknown")
                        temp = result.get("temperature_celsius", 0)
                        rainfall = result.get("rainfall_mm", 0)
                        answer_parts.append(
                            f"- {location}: {temp:.1f}°C, {rainfall:.1f}mm rainfall"
                        )
                    answer_parts.append("*[Source: India Meteorological Department]*")
        
        if not answer_parts:
            return "I couldn't find specific data matching your query. Please try rephrasing or being more specific."
        
        return "\n".join(answer_parts)
    
    def _collect_citations(self, data_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Collect all citations from data results"""
        citations = []
        
        for source_name, source_data in data_results.items():
            if "citation" in source_data:
                citation = source_data["citation"]
                citations.append({
                    "source": citation.get("source_name", "Unknown"),
                    "url": citation.get("source_url", ""),
                    "last_updated": citation.get("last_updated", "Unknown")
                })
        
        return citations
    
    def format_response_for_display(self, response: Dict[str, Any]) -> str:
        """Format the complete response for display"""
        output = []
        
        # Add the answer
        output.append("## Answer\n")
        output.append(response["answer"])
        
        # Add citations
        if response["citations"]:
            output.append("\n\n## Sources\n")
            for i, citation in enumerate(response["citations"], 1):
                output.append(
                    f"{i}. **{citation['source']}**\n"
                    f"   - URL: {citation['url']}\n"
                    f"   - Last Updated: {citation['last_updated']}"
                )
        
        # Add metadata (optional, for debugging)
        # output.append(f"\n\n## Query Metadata\n")
        # output.append(f"- Intent: {response['metadata']['intent']}")
        # output.append(f"- Confidence: {response['metadata']['confidence']:.2f}")
        
        return "\n".join(output)
