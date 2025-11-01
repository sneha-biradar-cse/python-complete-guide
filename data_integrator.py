"""
Data Integration Layer for Agricultural Q&A System
Handles multiple data sources with different formats and structures
"""

import json
import csv
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import os


class DataSource(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self, name: str, source_url: str):
        self.name = name
        self.source_url = source_url
        self.cache_dir = "data_cache"
        self.last_updated = None
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    @abstractmethod
    def fetch_data(self) -> Any:
        """Fetch data from the source"""
        pass
    
    @abstractmethod
    def query(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query the data source with given parameters"""
        pass
    
    @abstractmethod
    def normalize_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize data to a common format"""
        pass
    
    def get_citation(self) -> Dict[str, str]:
        """Return citation information for this data source"""
        return {
            "source_name": self.name,
            "source_url": self.source_url,
            "last_updated": self.last_updated.isoformat() if self.last_updated else "Unknown"
        }


class AgricultureDataSource(DataSource):
    """Data source adapter for Ministry of Agriculture & Farmers Welfare data"""
    
    def __init__(self):
        super().__init__(
            name="Ministry of Agriculture & Farmers Welfare",
            source_url="https://data.gov.in"
        )
        self.data = []
        self.dataset_id = "agriculture_data"
        
    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch agriculture data from data.gov.in or local cache"""
        cache_file = os.path.join(self.cache_dir, f"{self.dataset_id}.json")
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                self.data = json.load(f)
                self.last_updated = datetime.fromtimestamp(os.path.getmtime(cache_file))
                return self.data
        
        # For demo purposes, create sample agriculture data
        # In production, this would fetch from actual data.gov.in API/CSV
        self.data = self._create_sample_agriculture_data()
        
        # Cache the data
        with open(cache_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        self.last_updated = datetime.now()
        return self.data
    
    def _create_sample_agriculture_data(self) -> List[Dict[str, Any]]:
        """Create sample agriculture data for demonstration"""
        return [
            {
                "crop": "Rice",
                "state": "Punjab",
                "year": 2024,
                "production_tonnes": 12500000,
                "area_hectares": 3100000,
                "yield_kg_per_hectare": 4032,
                "msp_rupees_per_quintal": 2183
            },
            {
                "crop": "Wheat",
                "state": "Punjab",
                "year": 2024,
                "production_tonnes": 18000000,
                "area_hectares": 3500000,
                "yield_kg_per_hectare": 5143,
                "msp_rupees_per_quintal": 2275
            },
            {
                "crop": "Rice",
                "state": "West Bengal",
                "year": 2024,
                "production_tonnes": 15600000,
                "area_hectares": 5400000,
                "yield_kg_per_hectare": 2889,
                "msp_rupees_per_quintal": 2183
            },
            {
                "crop": "Cotton",
                "state": "Gujarat",
                "year": 2024,
                "production_tonnes": 8500000,
                "area_hectares": 2600000,
                "yield_kg_per_hectare": 3269,
                "msp_rupees_per_quintal": 7020
            },
            {
                "crop": "Sugarcane",
                "state": "Uttar Pradesh",
                "year": 2024,
                "production_tonnes": 145000000,
                "area_hectares": 2200000,
                "yield_kg_per_hectare": 65909,
                "msp_rupees_per_quintal": 340
            }
        ]
    
    def query(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query agriculture data with filters"""
        if not self.data:
            self.fetch_data()
        
        results = self.data
        
        # Apply filters
        if "crop" in params:
            crop = params["crop"].lower()
            results = [r for r in results if crop in r["crop"].lower()]
        
        if "state" in params:
            state = params["state"].lower()
            results = [r for r in results if state in r["state"].lower()]
        
        if "year" in params:
            results = [r for r in results if r["year"] == params["year"]]
        
        return results
    
    def normalize_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize agriculture data to common format"""
        return raw_data


class IMDDataSource(DataSource):
    """Data source adapter for India Meteorological Department data"""
    
    def __init__(self):
        super().__init__(
            name="India Meteorological Department (IMD)",
            source_url="https://data.gov.in"
        )
        self.data = []
        self.dataset_id = "imd_weather_data"
    
    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch IMD weather data from data.gov.in or local cache"""
        cache_file = os.path.join(self.cache_dir, f"{self.dataset_id}.json")
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                self.data = json.load(f)
                self.last_updated = datetime.fromtimestamp(os.path.getmtime(cache_file))
                return self.data
        
        # For demo purposes, create sample weather data
        # In production, this would fetch from actual IMD API/CSV
        self.data = self._create_sample_weather_data()
        
        # Cache the data
        with open(cache_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        self.last_updated = datetime.now()
        return self.data
    
    def _create_sample_weather_data(self) -> List[Dict[str, Any]]:
        """Create sample weather data for demonstration"""
        return [
            {
                "location": "Punjab",
                "date": "2024-10-01",
                "temperature_celsius": 28.5,
                "rainfall_mm": 45.2,
                "humidity_percent": 72,
                "wind_speed_kmph": 12.3,
                "season": "Monsoon"
            },
            {
                "location": "West Bengal",
                "date": "2024-10-01",
                "temperature_celsius": 30.2,
                "rainfall_mm": 125.8,
                "humidity_percent": 85,
                "wind_speed_kmph": 15.7,
                "season": "Monsoon"
            },
            {
                "location": "Gujarat",
                "date": "2024-10-01",
                "temperature_celsius": 32.8,
                "rainfall_mm": 35.4,
                "humidity_percent": 68,
                "wind_speed_kmph": 18.2,
                "season": "Monsoon"
            },
            {
                "location": "Uttar Pradesh",
                "date": "2024-10-01",
                "temperature_celsius": 29.7,
                "rainfall_mm": 78.3,
                "humidity_percent": 76,
                "wind_speed_kmph": 10.5,
                "season": "Monsoon"
            },
            {
                "location": "Punjab",
                "date": "2024-09-01",
                "temperature_celsius": 31.2,
                "rainfall_mm": 89.5,
                "humidity_percent": 80,
                "wind_speed_kmph": 14.1,
                "season": "Monsoon"
            }
        ]
    
    def query(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query weather data with filters"""
        if not self.data:
            self.fetch_data()
        
        results = self.data
        
        # Apply filters
        if "location" in params:
            location = params["location"].lower()
            results = [r for r in results if location in r["location"].lower()]
        
        if "date" in params:
            results = [r for r in results if r["date"] == params["date"]]
        
        if "season" in params:
            season = params["season"].lower()
            results = [r for r in results if season in r["season"].lower()]
        
        return results
    
    def normalize_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize weather data to common format"""
        return raw_data


class DataIntegrator:
    """Main data integration class that manages multiple data sources"""
    
    def __init__(self):
        self.sources = {
            "agriculture": AgricultureDataSource(),
            "weather": IMDDataSource()
        }
    
    def initialize_sources(self):
        """Initialize all data sources by fetching their data"""
        for source_name, source in self.sources.items():
            try:
                source.fetch_data()
                print(f"✓ Initialized {source.name}")
            except Exception as e:
                print(f"✗ Failed to initialize {source.name}: {str(e)}")
    
    def query_source(self, source_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query a specific data source and return results with citation"""
        if source_name not in self.sources:
            return {"error": f"Unknown data source: {source_name}"}
        
        source = self.sources[source_name]
        results = source.query(params)
        
        return {
            "results": results,
            "citation": source.get_citation(),
            "count": len(results)
        }
    
    def query_all_sources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query all relevant data sources and combine results"""
        combined_results = {}
        
        for source_name, source in self.sources.items():
            try:
                results = source.query(params)
                if results:
                    combined_results[source_name] = {
                        "results": results,
                        "citation": source.get_citation()
                    }
            except Exception as e:
                combined_results[source_name] = {
                    "error": str(e)
                }
        
        return combined_results
