"""
OpenAPI Tools - FDA API and ClinicalTrials.gov integration
"""

import logging
import os
from typing import Dict, Any, List
import requests

logger = logging.getLogger(__name__)


class FDAApiTool:
    """Tool for querying FDA API for drug approvals and regulatory data."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("tools", {}).get("openapi", {}).get("fda", {}).get("base_url", "https://api.fda.gov")
        self.api_key = os.getenv("FDA_API_KEY", "")  # Optional
    
    def search_drug_approvals(
        self,
        company: str = None,
        date_range: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search FDA drug approvals.
        
        Args:
            company: Company name to filter
            date_range: Date range (e.g., "[20230101+TO+20231231]")
            limit: Max results
            
        Returns:
            List of drug approvals
        """
        try:
            url = f"{self.base_url}/drug/drugsfda.json"
            
            # Build search query
            search_terms = []
            if company:
                search_terms.append(f'openfda.manufacturer_name:"{company}"')
            if date_range:
                search_terms.append(f"approval_date:{date_range}")
            
            params = {
                "limit": limit
            }
            
            if search_terms:
                params["search"] = "+AND+".join(search_terms)
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            logger.info(f"FDA API returned {len(results)} drug approvals")
            return results
            
        except Exception as e:
            logger.error(f"FDA API error: {e}")
            return []
    
    def as_tool(self):
        """Convert to OpenAPI tool format."""
        # Simplified - in production, use full OpenAPI spec
        from google.genai import types
        
        return types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="search_fda_drug_approvals",
                    description="Search FDA drug approval database",
                    parameters={
                        "type": "object",
                        "properties": {
                            "company": {"type": "string", "description": "Company name"},
                            "limit": {"type": "integer", "description": "Max results"}
                        }
                    }
                )
            ]
        )


class ClinicalTrialsTool:
    """Tool for querying ClinicalTrials.gov database."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("tools", {}).get("openapi", {}).get("clinicaltrials", {}).get("base_url", "https://clinicaltrials.gov/api/v2")
    
    def search_trials(
        self,
        condition: str = None,
        sponsor: str = None,
        status: str = None,
        page_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search clinical trials.
        
        Args:
            condition: Disease or condition
            sponsor: Sponsor/company name
            status: Trial status (e.g., "Recruiting", "Completed")
            page_size: Results per page
            
        Returns:
            List of clinical trials
        """
        try:
            url = f"{self.base_url}/studies"
            
            # Build query
            query_parts = []
            if condition:
                query_parts.append(f"AREA[Condition]{condition}")
            if sponsor:
                query_parts.append(f"AREA[Sponsor]{sponsor}")
            if status:
                query_parts.append(f"AREA[OverallStatus]{status}")
            
            params = {
                "query.cond": condition or "",
                "query.spons": sponsor or "",
                "pageSize": page_size
            }
            
            # Remove empty params
            params = {k: v for k, v in params.items() if v}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            studies = data.get("studies", [])
            
            logger.info(f"ClinicalTrials.gov returned {len(studies)} trials")
            return studies
            
        except Exception as e:
            logger.error(f"ClinicalTrials.gov API error: {e}")
            return []
    
    def as_tool(self):
        """Convert to OpenAPI tool format."""
        from google.genai import types
        
        return types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="search_clinical_trials",
                    description="Search clinical trials database",
                    parameters={
                        "type": "object",
                        "properties": {
                            "condition": {"type": "string", "description": "Disease/condition"},
                            "sponsor": {"type": "string", "description": "Sponsor company"},
                            "status": {"type": "string", "description": "Trial status"}
                        }
                    }
                )
            ]
        )
