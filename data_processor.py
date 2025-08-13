"""
Data processing wrapper for the S&P 500 Analysis UI
"""

import pandas as pd
import numpy as np
import requests
import io
from typing import Dict, List, Tuple, Optional, Any
import streamlit as st
from sp500_convergence import SP500Analyzer, download_slickcharts_data, load_local_csv
from config import ANALYSIS_CONFIG, MESSAGES


class DataProcessor:
    """Wrapper class for data processing and analysis operations."""
    
    def __init__(self):
        self.data = None
        self.analyzer = None
        self.analysis_results = {}
    
    @st.cache_data
    def download_slickcharts_data(_self) -> pd.DataFrame:
        """Download data from SlickCharts with caching."""
        try:
            with st.spinner(MESSAGES['downloading_data']):
                data = download_slickcharts_data()
                return data
        except Exception as e:
            st.error(f"下载数据失败: {str(e)}")
            return None
    
    def load_csv_data(self, uploaded_file) -> pd.DataFrame:
        """Load and parse CSV data from uploaded file."""
        try:
            with st.spinner(MESSAGES['processing_data']):
                # Save uploaded file temporarily
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                try:
                    # Use the existing load_local_csv function
                    data = load_local_csv(tmp_path)
                    return data
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

        except Exception as e:
            st.error(f"解析CSV文件失败: {str(e)}")
            return None
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate the loaded data."""
        if data is None or data.empty:
            st.error(MESSAGES['error_no_data'])
            return False
        
        if len(data) < ANALYSIS_CONFIG['min_years_for_analysis']:
            st.error(MESSAGES['error_insufficient_data'])
            return False
        
        # Check for required columns
        if 'year' not in data.columns or 'return' not in data.columns:
            st.error("数据必须包含'year'和'return'列")
            return False
        
        return True
    
    def set_data(self, data: pd.DataFrame) -> bool:
        """Set the data and create analyzer."""
        if not self.validate_data(data):
            return False
        
        self.data = data
        self.analyzer = SP500Analyzer(data)
        st.success(MESSAGES['data_loaded'])
        return True

    def get_data_hash(self) -> str:
        """Generate a hash of the current data for cache invalidation."""
        if self.data is None:
            return "no_data"

        # Create a hash based on data content
        import hashlib
        data_str = f"{len(self.data)}_{self.data['year'].min()}_{self.data['year'].max()}_{self.data['return'].sum():.6f}"
        return hashlib.md5(data_str.encode()).hexdigest()[:8]

    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the loaded data."""
        if self.data is None:
            return {}
        
        return {
            'total_years': len(self.data),
            'start_year': int(self.data['year'].min()),
            'end_year': int(self.data['year'].max()),
            'mean_return': float(self.data['return'].mean()),
            'std_return': float(self.data['return'].std()),
            'min_return': float(self.data['return'].min()),
            'max_return': float(self.data['return'].max()),
            'positive_years': int((self.data['return'] > 0).sum()),
            'negative_years': int((self.data['return'] < 0).sum())
        }
    
    @st.cache_data
    def compute_rolling_analysis(_self, start_years: List[int], windows: List[int], data_hash: str = None) -> Dict[str, Any]:
        """Compute rolling CAGR analysis for all combinations."""
        if _self.analyzer is None:
            return {}
        
        results = {}
        
        with st.spinner(MESSAGES['processing_data']):
            for start_year in start_years:
                results[start_year] = {}
                
                for window in windows:
                    cagrs = _self.analyzer.compute_rolling_cagr(window, start_year)
                    if cagrs:
                        cagr_values = [cagr for _, cagr in cagrs]
                        end_years = [end_year for end_year, _ in cagrs]
                        
                        results[start_year][window] = {
                            'cagrs': cagr_values,
                            'end_years': end_years,
                            'best_cagr': max(cagr_values),
                            'worst_cagr': min(cagr_values),
                            'avg_cagr': np.mean(cagr_values),
                            'std_cagr': np.std(cagr_values),
                            'count': len(cagr_values)
                        }
                    else:
                        results[start_year][window] = None
        
        return results
    
    @st.cache_data
    def compute_no_loss_analysis(_self, start_years: List[int], data_hash: str = None) -> Dict[str, Any]:
        """Compute no-loss horizon analysis."""
        if _self.analyzer is None:
            return {}
        
        results = {}
        
        with st.spinner("计算无损失持有期..."):
            for start_year in start_years:
                result = _self.analyzer.find_min_no_loss_horizon(start_year)
                results[start_year] = result
        
        return results
    
    @st.cache_data
    def compute_convergence_analysis(_self, start_years: List[int], thresholds: List[float], data_hash: str = None) -> Dict[str, Any]:
        """Compute convergence analysis."""
        if _self.analyzer is None:
            return {}
        
        results = {}
        
        with st.spinner("计算收敛性分析..."):
            for start_year in start_years:
                results[start_year] = {}
                for threshold in thresholds:
                    result = _self.analyzer.find_min_spread_horizon(start_year, threshold)
                    results[start_year][threshold] = result
        
        return results
    
    def create_rolling_cagr_dataframe(self, rolling_results: Dict[str, Any], start_year: int) -> pd.DataFrame:
        """Create a DataFrame for rolling CAGR results."""
        if start_year not in rolling_results:
            return pd.DataFrame()
        
        data_rows = []
        year_data = rolling_results[start_year]
        
        # Get all end years from the first available window
        end_years = None
        for window in sorted(year_data.keys()):
            if year_data[window] is not None:
                end_years = year_data[window]['end_years']
                break
        
        if end_years is None:
            return pd.DataFrame()
        
        # Create rows for each end year
        for i, end_year in enumerate(end_years):
            row = {'EndYear': end_year}
            for window in sorted(year_data.keys()):
                if year_data[window] is not None and i < len(year_data[window]['cagrs']):
                    row[f'{window}y'] = year_data[window]['cagrs'][i]
                else:
                    row[f'{window}y'] = None
            data_rows.append(row)
        
        return pd.DataFrame(data_rows)
    
    def create_summary_dataframe(self, rolling_results: Dict[str, Any], start_year: int) -> pd.DataFrame:
        """Create a summary DataFrame for window statistics (enhanced)."""
        if start_year not in rolling_results:
            return pd.DataFrame()

        year_data = rolling_results[start_year]
        summary_rows = []

        for window in sorted(year_data.keys()):
            if year_data[window] is not None:
                data = year_data[window]

                # Find best and worst windows
                best_idx = np.argmax(data['cagrs'])
                worst_idx = np.argmin(data['cagrs'])

                # Additional metrics
                cagrs = np.array(data['cagrs']) if data['cagrs'] else np.array([])
                if cagrs.size > 0:
                    p10 = float(np.percentile(cagrs, 10))
                    p50 = float(np.percentile(cagrs, 50))
                    p90 = float(np.percentile(cagrs, 90))
                else:
                    p10 = p50 = p90 = None
                avg = data['avg_cagr']
                std = data['std_cagr']
                stability_index = (avg / std) if (isinstance(avg, (int,float)) and isinstance(std,(int,float)) and std not in (0.0, 0)) else None
                variation_coeff = (std / abs(avg)) if (isinstance(avg, (int,float)) and avg not in (0.0,)) else None

                summary_rows.append({
                    'window_size': window,
                    'best_window': f"{start_year}-{data['end_years'][best_idx]}",
                    'best_cagr': data['best_cagr'],
                    'worst_window': f"{start_year}-{data['end_years'][worst_idx]}",
                    'worst_cagr': data['worst_cagr'],
                    'avg_cagr': data['avg_cagr'],
                    'std_cagr': data['std_cagr'],
                    'p10_cagr': p10,
                    'median_cagr': p50,
                    'p90_cagr': p90,
                    'stability_index': stability_index,
                    'variation_coeff': variation_coeff,
                    'count': data['count']
                })

        return pd.DataFrame(summary_rows)
    
    def export_results_to_csv(self, results: Dict[str, Any], filename: str) -> bytes:
        """Export results to CSV format."""
        if isinstance(results, pd.DataFrame):
            return results.to_csv(index=False).encode('utf-8')
        else:
            # Convert dict to DataFrame if needed
            df = pd.DataFrame(results)
            return df.to_csv(index=False).encode('utf-8')
