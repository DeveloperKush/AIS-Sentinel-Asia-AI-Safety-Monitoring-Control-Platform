import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional

class RegulatoryMapper:
    """
    Maps threat classifications and risk categories to regional AI policies
    and regulatory requirements in the Global South and international frameworks.
    """
    
    DEFAULT_POLICIES = {
        "Biosecurity": [
            {
                "jurisdiction": "Vietnam",
                "law_name": "Law 134/2025 (AI Law)",
                "article": "Article 12",
                "requirement": "Strict registration and mandatory risk assessment for AI models integrated with biological sequence design tools.",
                "penalty": "Administrative fine up to 500,000,000 VND and immediate suspension of model deployment.",
                "effective_date": "2025-06-01"
            },
            {
                "jurisdiction": "EU",
                "law_name": "EU AI Act",
                "article": "Article 6",
                "requirement": "High-risk classification requiring independent third-party safety audits for dual-use biotechnology AI applications.",
                "penalty": "Administrative fines up to 35,000,000 EUR or 7% of global annual turnover, whichever is higher.",
                "effective_date": "2026-08-01"
            },
            {
                "jurisdiction": "India",
                "law_name": "MeitY AI frameworks",
                "article": "Section 4(c)",
                "requirement": "Mandatory biosecurity alignment check and threat reporting before publishing open-weight biological design models.",
                "penalty": "Revocation of digital commercial authorization and administrative sanctions.",
                "effective_date": "2025-12-01"
            }
        ],
        "AI Safety": [
            {
                "jurisdiction": "Vietnam",
                "law_name": "Decree 142/2026 (Human-in-the-Loop)",
                "article": "Article 8",
                "requirement": "Mandatory human-in-the-loop supervisor override mechanism for all generative foundation models deployed in public services.",
                "penalty": "Fines up to 200,000,000 VND and mandatory public model recall.",
                "effective_date": "2026-01-01"
            },
            {
                "jurisdiction": "Singapore",
                "law_name": "AI Verify Framework",
                "article": "Section 3.2",
                "requirement": "Mandatory verification of model robustness against jailbreak prompts, sycophancy bias, and translation hallucinations.",
                "penalty": "Voluntary framework - loss of compliance certification, standard listing, and reputational damage.",
                "effective_date": "2024-05-01"
            },
            {
                "jurisdiction": "ASEAN",
                "law_name": "ASEAN AI Governance Guide",
                "article": "Section 5 (Voluntary)",
                "requirement": "Implement localized risk monitoring, alignment checks, and translation guardrails to prevent harmful model behaviors in regional languages.",
                "penalty": "Voluntary guidance - no direct legal penalties, serves as regional industry best practice.",
                "effective_date": "2024-02-01"
            },
            {
                "jurisdiction": "EU",
                "law_name": "EU AI Act",
                "article": "Article 52",
                "requirement": "Transparency obligation: ensure users know they are interacting with AI, and disclose safety benchmark performance metrics.",
                "penalty": "Administrative fines up to 15,000,000 EUR or 3% of global annual turnover.",
                "effective_date": "2026-08-01"
            }
        ],
        "Data Privacy": [
            {
                "jurisdiction": "India",
                "law_name": "Digital Personal Data Protection Act (DPDP)",
                "article": "Section 6",
                "requirement": "Obtain explicit consent before utilizing personal data to train large language models or processing individual user interactions.",
                "penalty": "Administrative fine up to 250 Crore INR (2.5 billion INR).",
                "effective_date": "2024-09-01"
            },
            {
                "jurisdiction": "Singapore",
                "law_name": "Personal Data Protection Act (PDPA)",
                "article": "Section 20",
                "requirement": "Implement data protection frameworks and masking to prevent personal data from being stored or exposed in generative AI prompt logs.",
                "penalty": "Financial penalty up to 1,000,000 SGD or 10% of local annual turnover, whichever is higher.",
                "effective_date": "2021-02-01"
            },
            {
                "jurisdiction": "Indonesia",
                "law_name": "Personal Data Protection Law (PDP Law)",
                "article": "Article 28",
                "requirement": "Process personal data lawfully for automated decision making; provide individuals with the right to request human override review.",
                "penalty": "Administrative fine up to 2% of annual revenues and potential criminal penalties up to 6 years imprisonment.",
                "effective_date": "2024-10-17"
            }
        ],
        "Default": [
            {
                "jurisdiction": "EU",
                "law_name": "EU AI Act",
                "article": "Article 9",
                "requirement": "Establish a risk management system to identify, evaluate, and mitigate safety risks throughout the AI system lifecycle.",
                "penalty": "Administrative fines up to 30,000,000 EUR or 6% of global annual turnover.",
                "effective_date": "2026-08-01"
            }
        ]
    }

    def __init__(self, policies_file: str = "config/policies.json") -> None:
        """
        Initializes the RegulatoryMapper and loads the policies file.
        If the file does not exist, it is created and pre-populated with default values.
        """
        self.policies_file = policies_file
        self._ensure_policies_file()
        self.policies = self._load_policies()

    def _ensure_policies_file(self) -> None:
        """Ensures that the policies JSON database exists, creating parent folders if necessary."""
        if not os.path.exists(self.policies_file):
            dir_name = os.path.dirname(self.policies_file)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            self._write_default_policies()

    def _write_default_policies(self) -> None:
        """Writes the default policy database to the policies JSON file."""
        with open(self.policies_file, "w", encoding="utf-8") as f:
            json.dump(self.DEFAULT_POLICIES, f, indent=4)

    def _load_policies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Loads policies from the JSON file."""
        try:
            with open(self.policies_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.DEFAULT_POLICIES

    def _normalize_category(self, risk_category: str) -> str:
        """Normalizes risk categories to group them under matching policy keys."""
        cat_lower = risk_category.lower()
        if any(w in cat_lower for w in ["bio", "gene", "pathogen", "crispr", "dual-use", "weapon", "biosecurity"]):
            return "Biosecurity"
        elif any(w in cat_lower for w in ["privacy", "leak", "personal", "data", "dpdp", "pdpa"]):
            return "Data Privacy"
        elif any(w in cat_lower for w in ["jailbreak", "sycophancy", "hallucination", "adversarial", "safety", "layout", "attack"]):
            return "AI Safety"
        return "Default"

    def map_threat(self, risk_category: str, jurisdiction: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Maps a threat risk category to applicable regulations.
        
        Args:
            risk_category: The risk category classification of the threat.
            jurisdiction: Optional filter for a specific country or region.

        Returns:
            A list of dictionary objects representing relevant regulations.
        """
        category = self._normalize_category(risk_category)
        laws = self.policies.get(category, self.policies.get("Default", []))
        
        if jurisdiction:
            juris_lower = jurisdiction.lower()
            return [l for l in laws if l.get("jurisdiction", "").lower() == juris_lower]
        
        return laws

    def get_all_jurisdictions(self, risk_category: str) -> List[Dict[str, Any]]:
        """
        Returns laws for all jurisdictions mapping to the risk category.

        Args:
            risk_category: The threat's risk category.

        Returns:
            A list of all applicable policy items for that category.
        """
        return self.map_threat(risk_category, jurisdiction=None)

    def compare_jurisdictions(self, risk_category: str) -> pd.DataFrame:
        """
        Creates a comparison table (DataFrame) comparing the policy requirements
        across all jurisdictions for the given risk category.

        Args:
            risk_category: The risk category of the threat.

        Returns:
            A Pandas DataFrame comparing the rules.
        """
        laws = self.get_all_jurisdictions(risk_category)
        df = pd.DataFrame(laws)
        if df.empty:
            return pd.DataFrame(columns=["jurisdiction", "law_name", "article", "requirement", "penalty", "effective_date"])
        
        # Sort and rename columns for readability in comparisons
        df.columns = [c.replace("_", " ").title() for c in df.columns]
        return df
