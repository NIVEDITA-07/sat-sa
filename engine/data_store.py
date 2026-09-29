import pandas as pd
from typing import Dict, Any, List

class DataStore:
    """
    SAT-SA Data Relationship Layer.
    Maintains the in-memory normalized data and provides relational access.
    Raw data remains immutable.
    """
    def __init__(self):
        self._profiles_df = pd.DataFrame()
        self._assets_df = pd.DataFrame()
        self._alerts_df = pd.DataFrame()
        self._cases_df = pd.DataFrame()
        
        # Indexed representations for fast O(1) lookup
        self._profiles_idx = {}
        self._assets_idx = {}
        self._alerts_idx = {}
        self._cases_idx = {}

    def load_cse_profiles(self, df: pd.DataFrame):
        self._profiles_df = df.copy()
        if not df.empty and 'cse_id' in df.columns:
            # Handle potential duplicates by dropping them for the index
            self._profiles_idx = df.drop_duplicates(subset=['cse_id']).set_index('cse_id').to_dict('index')

    def load_assets(self, df: pd.DataFrame):
        self._assets_df = df.copy()
        if not df.empty and 'asset_id' in df.columns:
            self._assets_idx = df.drop_duplicates(subset=['asset_id']).set_index('asset_id').to_dict('index')

    def load_alerts(self, df: pd.DataFrame):
        self._alerts_df = df.copy()
        if not df.empty and 'alert_id' in df.columns:
            self._alerts_idx = df.drop_duplicates(subset=['alert_id']).set_index('alert_id').to_dict('index')

    def load_cases(self, df: pd.DataFrame):
        self._cases_df = df.copy()
        if not df.empty and 'case_id' in df.columns:
            self._cases_idx = df.drop_duplicates(subset=['case_id']).set_index('case_id').to_dict('index')
            
        # Build alert to case index
        self._alert_to_case_idx = {}
        if not df.empty and 'alert_id' in df.columns and 'case_id' in df.columns:
            for _, row in df.iterrows():
                a_id = row.get('alert_id')
                c_id = row.get('case_id')
                if pd.notna(a_id) and pd.notna(c_id):
                    self._alert_to_case_idx[str(a_id)] = str(c_id)

    def validate_relationships(self) -> Dict[str, Any]:
        """
        Validates the relational linkages between entities.
        Returns a dictionary with validation results.
        """
        results = {
            "missing_assets_in_alerts": [],
            "missing_cses_in_assets": [],
            "missing_alerts_in_cases": [],
            "missing_cses_in_alerts": []
        }
        
        if not self._alerts_df.empty and not self._assets_df.empty:
            alert_assets = set(self._alerts_df['asset_id'].dropna())
            known_assets = set(self._assets_df['asset_id'])
            results["missing_assets_in_alerts"] = list(alert_assets - known_assets - {'NOT_AVAILABLE'})

        if not self._assets_df.empty and not self._profiles_df.empty:
            asset_cses = set(self._assets_df['cse_id'].dropna())
            known_cses = set(self._profiles_df['cse_id'])
            results["missing_cses_in_assets"] = list(asset_cses - known_cses - {'NOT_AVAILABLE'})

        if not self._cases_df.empty and not self._alerts_df.empty:
            case_alerts = set(self._cases_df['alert_id'].dropna())
            known_alerts = set(self._alerts_df['alert_id'])
            results["missing_alerts_in_cases"] = list(case_alerts - known_alerts - {'NOT_AVAILABLE'})

        if not self._alerts_df.empty and not self._profiles_df.empty:
            alert_cses = set(self._alerts_df['cse_id'].dropna())
            known_cses = set(self._profiles_df['cse_id'])
            results["missing_cses_in_alerts"] = list(alert_cses - known_cses - {'NOT_AVAILABLE'})

        results["is_valid"] = all(len(v) == 0 for k, v in results.items() if k != "is_valid")
        return results

    def get_cse_data(self, cse_id: str) -> Dict[str, Any]:
        """
        Retrieve CSE profile, along with its assets, alerts, and cases.
        """
        profile = self._profiles_idx.get(cse_id, {})
        
        assets = []
        if not self._assets_df.empty:
            assets = self._assets_df[self._assets_df['cse_id'] == cse_id].to_dict('records')
            
        alerts = []
        if not self._alerts_df.empty:
            alerts = self._alerts_df[self._alerts_df['cse_id'] == cse_id].to_dict('records')
            
        cases = []
        if not self._cases_df.empty:
            cases = self._cases_df[self._cases_df['cse_id'] == cse_id].to_dict('records')
            
        return {
            "profile": profile,
            "assets": assets,
            "alerts": alerts,
            "cases": cases
        }

    def get_alert_evidence(self, alert_id: str) -> Dict[str, Any]:
        """
        Returns the raw/normalized alert data for an evidence lookup.
        """
        return self._alerts_idx.get(alert_id, {})

    def get_case_evidence(self, case_id: str) -> Dict[str, Any]:
        """
        Returns the raw/normalized case data for an evidence lookup.
        """
        return self._cases_idx.get(case_id, {})

    def get_asset_evidence(self, asset_id: str) -> Dict[str, Any]:
        """
        Returns the raw/normalized asset data for an evidence lookup.
        """
        return self._assets_idx.get(asset_id, {})

    def get_case_for_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Returns the case associated with the primary_alert_id, or None.
        """
        if not hasattr(self, '_alert_to_case_idx'):
            return None
        case_id = self._alert_to_case_idx.get(alert_id)
        if case_id:
            return self.get_case_evidence(case_id)
        return None

    @property
    def alerts_df(self): return self._alerts_df
    
    @property
    def assets_df(self): return self._assets_df
    
    @property
    def cases_df(self): return self._cases_df
    
    @property
    def cse_profiles_df(self): return self._profiles_df
