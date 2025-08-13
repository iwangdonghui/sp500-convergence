"""
Data processing wrapper for the S&P 500 Analysis UI
"""

import pandas as pd
import numpy as np
import requests
import io
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import streamlit as st
from sp500_convergence import SP500Analyzer, download_slickcharts_data, load_local_csv
from config import ANALYSIS_CONFIG, MESSAGES
from report_generator import generate_comprehensive_report, ChartExporter
from multi_asset_engine import MultiAssetAnalyzer, ASSET_UNIVERSE
from gips_compliance import (
    GIPSCalculator, PerformanceAttributionAnalyzer, BenchmarkStandardizer,
    ReturnCalculationMethod, ComplianceLevel, CashFlow, PortfolioValuation,
    GIPSCalculationResult
)


class DataProcessor:
    """Wrapper class for data processing and analysis operations."""

    def __init__(self):
        self.data = None
        self.analyzer = None
        self.analysis_results = {}

        # Multi-asset analysis support
        self.multi_asset_analyzer = MultiAssetAnalyzer()
        self.selected_assets = []
        self._initialize_asset_universe()

        # GIPS compliance components
        self.gips_calculator = GIPSCalculator()
        self.attribution_analyzer = PerformanceAttributionAnalyzer()
        self.benchmark_standardizer = BenchmarkStandardizer()
    
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

    @st.cache_data
    def compute_risk_metrics_analysis(_self, start_years: List[int], windows: List[int], data_hash: str = None) -> Dict[str, Any]:
        """Compute risk metrics analysis with caching."""
        if _self.analyzer is None:
            return {}

        try:
            results = {}

            with st.spinner("正在计算风险指标..."):
                # Compute overall risk metrics for each start year
                for start_year in start_years:
                    year_results = {
                        'overall': _self.analyzer.compute_risk_metrics(start_year),
                        'rolling': {}
                    }

                    # Compute rolling risk metrics for each window size
                    for window in windows:
                        rolling_metrics = _self.analyzer.compute_rolling_risk_metrics(start_year, window)
                        year_results['rolling'][window] = rolling_metrics

                    results[start_year] = year_results

            return results
        except Exception as e:
            st.error(f"风险指标分析失败: {str(e)}")
            return {}

    def generate_professional_report(self, report_type: str = 'pdf') -> bytes:
        """Generate professional PDF or Excel report."""
        if not hasattr(self, 'analyzer') or self.analyzer is None:
            raise ValueError("No data loaded. Please load data first.")

        # Get all analysis results
        data_hash = self.get_data_hash()

        # Prepare analysis results
        analysis_results = {}

        # Get configuration from session state or use defaults based on available data
        min_year = min(self.data['year']) if hasattr(self, 'data') and self.data is not None else 1926
        max_year = max(self.data['year']) if hasattr(self, 'data') and self.data is not None else 2023

        # Use available years that exist in the data
        available_start_years = []
        default_start_years = [1926, 1957, 1972, 1985, 1990, 2000]
        for year in default_start_years:
            if year >= min_year and year <= max_year - 10:  # Ensure at least 10 years of data
                available_start_years.append(year)

        # If no default years are available, use the earliest possible years
        if not available_start_years:
            available_start_years = [min_year]

        config = {
            'start_years': available_start_years,
            'windows': [5, 10, 15, 20, 30],
            'thresholds': [0.0025, 0.005, 0.0075, 0.01]
        }

        try:
            # Get rolling analysis
            rolling_results = self.compute_rolling_analysis(
                config['start_years'],
                config['windows'],
                data_hash
            )
            analysis_results['rolling'] = rolling_results

            # Get no-loss analysis
            no_loss_results = self.compute_no_loss_analysis(
                config['start_years'],
                data_hash
            )
            analysis_results['no_loss'] = no_loss_results

            # Get convergence analysis
            convergence_results = self.compute_convergence_analysis(
                config['start_years'],
                config['thresholds'],
                data_hash
            )
            analysis_results['convergence'] = convergence_results

            # Get risk metrics analysis
            risk_metrics_results = self.compute_risk_metrics_analysis(
                config['start_years'],
                config['windows'],
                data_hash
            )
            analysis_results['risk_metrics'] = risk_metrics_results

            # Generate comprehensive report
            return generate_comprehensive_report(analysis_results, config, report_type)

        except Exception as e:
            st.error(f"报告生成失败: {str(e)}")
            raise

    def export_chart(self, chart_type: str, format: str = 'png') -> bytes:
        """Export high-quality charts."""
        if not hasattr(self, 'analyzer') or self.analyzer is None:
            raise ValueError("No data loaded. Please load data first.")

        try:
            if chart_type == 'risk_metrics':
                # Get risk metrics data
                data_hash = self.get_data_hash()
                config = {
                    'start_years': [1926, 1957, 1972, 1985],
                    'windows': [5, 10, 15, 20, 30]
                }

                risk_results = self.compute_risk_metrics_analysis(
                    config['start_years'],
                    config['windows'],
                    data_hash
                )

                # Prepare data for chart export
                risk_data = {'overall_metrics': {}}
                for start_year, year_data in risk_results.items():
                    if 'overall' in year_data and year_data['overall']:
                        risk_data['overall_metrics'][start_year] = year_data['overall']

                return ChartExporter.export_risk_metrics_chart(risk_data, format)

            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")

        except Exception as e:
            st.error(f"图表导出失败: {str(e)}")
            raise

    def _initialize_asset_universe(self) -> None:
        """Initialize the asset universe for multi-asset analysis."""
        for symbol, asset_info in ASSET_UNIVERSE.items():
            self.multi_asset_analyzer.add_asset(asset_info)

    def get_available_assets(self) -> Dict[str, Dict[str, Any]]:
        """Get available assets grouped by asset class."""
        assets_by_class = {}

        for symbol, asset_info in ASSET_UNIVERSE.items():
            asset_class = asset_info.asset_class.value
            if asset_class not in assets_by_class:
                assets_by_class[asset_class] = []

            assets_by_class[asset_class].append({
                'symbol': symbol,
                'name': asset_info.name,
                'description': asset_info.description,
                'inception_year': asset_info.inception_year
            })

        return assets_by_class

    def set_selected_assets(self, asset_symbols: List[str]) -> None:
        """Set the selected assets for multi-asset analysis."""
        # Validate that all symbols exist
        invalid_symbols = [s for s in asset_symbols if s not in ASSET_UNIVERSE]
        if invalid_symbols:
            raise ValueError(f"Invalid asset symbols: {invalid_symbols}")

        self.selected_assets = asset_symbols

    def compute_multi_asset_analysis(self, start_year: int, end_year: int) -> Dict[str, Any]:
        """Compute comprehensive multi-asset analysis."""
        if not self.selected_assets:
            raise ValueError("No assets selected for analysis")

        try:
            results = {}

            with st.spinner("正在计算多资产分析..."):
                # Individual asset analysis
                results['individual_assets'] = {}
                for symbol in self.selected_assets:
                    asset_summary = self.multi_asset_analyzer.get_asset_summary(symbol, start_year, end_year)
                    results['individual_assets'][symbol] = asset_summary

                # Correlation analysis
                if len(self.selected_assets) > 1:
                    correlation_matrix = self.multi_asset_analyzer.get_correlation_matrix(
                        self.selected_assets, start_year, end_year
                    )
                    results['correlation_matrix'] = correlation_matrix

                    # Covariance analysis
                    covariance_matrix = self.multi_asset_analyzer.get_covariance_matrix(
                        self.selected_assets, start_year, end_year
                    )
                    results['covariance_matrix'] = covariance_matrix

                    # Efficient frontier (if 2-8 assets)
                    if 2 <= len(self.selected_assets) <= 8:
                        efficient_frontier = self.multi_asset_analyzer.get_efficient_frontier(
                            self.selected_assets, start_year, end_year, num_portfolios=1000
                        )
                        results['efficient_frontier'] = efficient_frontier

                # Asset class analysis
                results['asset_class_summary'] = self._analyze_by_asset_class(start_year, end_year)

            return results

        except Exception as e:
            st.error(f"多资产分析失败: {str(e)}")
            raise

    def _analyze_by_asset_class(self, start_year: int, end_year: int) -> Dict[str, Any]:
        """Analyze performance by asset class."""
        asset_class_data = {}

        for symbol in self.selected_assets:
            asset_info = ASSET_UNIVERSE[symbol]
            asset_class = asset_info.asset_class.value

            if asset_class not in asset_class_data:
                asset_class_data[asset_class] = []

            # Get asset summary
            summary = self.multi_asset_analyzer.get_asset_summary(symbol, start_year, end_year)
            asset_class_data[asset_class].append({
                'symbol': symbol,
                'name': asset_info.name,
                'metrics': summary['risk_metrics']
            })

        # Calculate asset class averages
        asset_class_summary = {}
        for asset_class, assets in asset_class_data.items():
            if not assets:
                continue

            # Calculate average metrics
            avg_metrics = {}
            metric_keys = assets[0]['metrics'].keys()

            for key in metric_keys:
                values = [asset['metrics'].get(key, 0) for asset in assets if not pd.isna(asset['metrics'].get(key, np.nan))]
                if values:
                    avg_metrics[key] = np.mean(values)
                else:
                    avg_metrics[key] = np.nan

            asset_class_summary[asset_class] = {
                'count': len(assets),
                'assets': assets,
                'average_metrics': avg_metrics
            }

        return asset_class_summary

    def calculate_optimal_portfolio(self, target_return: float = None, target_risk: float = None) -> Dict[str, Any]:
        """Calculate optimal portfolio weights."""
        if len(self.selected_assets) < 2:
            raise ValueError("Need at least 2 assets for portfolio optimization")

        try:
            # Use a simple approach for now - equal weights
            num_assets = len(self.selected_assets)
            equal_weights = [1.0 / num_assets] * num_assets

            # Calculate portfolio metrics with equal weights
            start_year = 1990  # Default period
            end_year = 2023

            portfolio_metrics = self.multi_asset_analyzer.calculate_portfolio_metrics(
                self.selected_assets, equal_weights, start_year, end_year
            )

            return {
                'weights': dict(zip(self.selected_assets, equal_weights)),
                'metrics': portfolio_metrics,
                'optimization_method': 'equal_weight',
                'note': 'Equal weight portfolio (advanced optimization coming soon)'
            }

        except Exception as e:
            st.error(f"投资组合优化失败: {str(e)}")
            raise

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
            return results

    def compute_gips_compliance_analysis(
        self,
        start_year: int,
        end_year: int,
        benchmark_symbol: str = "SPY",
        firm_name: str = "Investment Firm",
        composite_name: str = "S&P 500 Tracking Composite"
    ) -> Dict:
        """
        Compute GIPS-compliant performance analysis.

        Args:
            start_year: Analysis start year
            end_year: Analysis end year
            benchmark_symbol: Benchmark asset symbol
            firm_name: Name of the investment firm
            composite_name: Name of the composite

        Returns:
            Dictionary containing GIPS compliance analysis results
        """
        if self.data is None:
            raise ValueError("No data available. Please load data first.")

        # Clear previous warnings
        self.gips_calculator.clear_warnings()

        # Prepare portfolio data from S&P 500 returns
        portfolio_data = self._prepare_portfolio_data_for_gips(start_year, end_year)
        benchmark_data = self._prepare_benchmark_data_for_gips(benchmark_symbol, start_year, end_year)

        # Calculate GIPS-compliant returns
        gips_result = self._calculate_gips_returns(
            portfolio_data, benchmark_data, start_year, end_year
        )

        # Perform attribution analysis
        attribution_analysis = self._perform_attribution_analysis(
            portfolio_data, benchmark_data
        )

        # Validate benchmark appropriateness
        benchmark_validation = self._validate_benchmark_selection(benchmark_symbol)

        # Generate compliance report
        compliance_report = self.gips_calculator.generate_gips_report(
            gips_result, firm_name, composite_name,
            f"{benchmark_symbol} Index", benchmark_data.get('total_return', 0.0)
        )

        return {
            'gips_calculation': {
                'time_weighted_return': gips_result.time_weighted_return,
                'money_weighted_return': gips_result.money_weighted_return,
                'composite_return': gips_result.composite_return,
                'calculation_method': gips_result.calculation_method.value,
                'compliance_level': gips_result.compliance_level.value,
                'validation_notes': gips_result.validation_notes
            },
            'attribution_analysis': attribution_analysis,
            'benchmark_validation': benchmark_validation,
            'compliance_report': compliance_report,
            'period_summary': {
                'start_date': f"{start_year}-01-01",
                'end_date': f"{end_year}-12-31",
                'total_assets': gips_result.total_assets,
                'number_of_portfolios': gips_result.number_of_portfolios
            }
        }

    def _prepare_portfolio_data_for_gips(self, start_year: int, end_year: int) -> Dict:
        """Prepare portfolio data for GIPS calculations."""
        # Filter data for the specified period
        period_data = self.data[
            (self.data['year'] >= start_year) &
            (self.data['year'] <= end_year)
        ].copy()

        if period_data.empty:
            raise ValueError(f"No data available for period {start_year}-{end_year}")

        # Create portfolio valuations
        valuations = []
        for _, row in period_data.iterrows():
            date = datetime(int(row['year']), 12, 31)
            # Simulate portfolio value based on cumulative returns
            market_value = 1000000 * (1 + row['return']) ** (row['year'] - start_year + 1)
            valuations.append(PortfolioValuation(date, market_value))

        # Add starting valuation
        start_date = datetime(start_year, 1, 1)
        valuations.insert(0, PortfolioValuation(start_date, 1000000.0))

        # Create sample cash flows (for demonstration)
        cash_flows = []
        if len(period_data) > 2:
            mid_year = start_year + (end_year - start_year) // 2
            cash_flows.append(
                CashFlow(datetime(mid_year, 6, 30), 50000.0, "contribution")
            )

        return {
            'valuations': valuations,
            'cash_flows': cash_flows,
            'returns': period_data['return'].tolist(),
            'years': period_data['year'].tolist()
        }

    def _prepare_benchmark_data_for_gips(self, benchmark_symbol: str, start_year: int, end_year: int) -> Dict:
        """Prepare benchmark data for GIPS calculations."""
        # For demonstration, use S&P 500 data as benchmark
        # In practice, this would load actual benchmark data
        period_data = self.data[
            (self.data['year'] >= start_year) &
            (self.data['year'] <= end_year)
        ].copy()

        if period_data.empty:
            return {'returns': [], 'total_return': 0.0}

        benchmark_returns = period_data['return'].tolist()
        total_return = np.prod([1 + r for r in benchmark_returns]) - 1

        return {
            'returns': benchmark_returns,
            'total_return': total_return,
            'symbol': benchmark_symbol,
            'years': period_data['year'].tolist()
        }

    def _calculate_gips_returns(
        self,
        portfolio_data: Dict,
        benchmark_data: Dict,
        start_year: int,
        end_year: int
    ) -> GIPSCalculationResult:
        """Calculate GIPS-compliant returns."""
        # Calculate time-weighted return
        twr = self.gips_calculator.calculate_time_weighted_return(
            portfolio_data['valuations'],
            portfolio_data['cash_flows']
        )

        # Calculate money-weighted return
        try:
            mwr = self.gips_calculator.calculate_money_weighted_return(
                portfolio_data['valuations'],
                portfolio_data['cash_flows']
            )
        except Exception as e:
            mwr = None
            self.gips_calculator.calculation_warnings.append(f"MWR calculation failed: {str(e)}")

        # Create result object
        result = GIPSCalculationResult(
            time_weighted_return=twr,
            money_weighted_return=mwr,
            composite_return=twr,  # Single portfolio composite
            calculation_method=ReturnCalculationMethod.TIME_WEIGHTED,
            period_start=datetime(start_year, 1, 1),
            period_end=datetime(end_year, 12, 31),
            number_of_portfolios=1,
            total_assets=portfolio_data['valuations'][-1].market_value,
            compliance_level=ComplianceLevel.PARTIAL_COMPLIANCE,
            validation_notes=[]
        )

        # Validate compliance
        compliance_level, notes = self.gips_calculator.validate_gips_compliance(
            result, [portfolio_data]
        )
        result.compliance_level = compliance_level
        result.validation_notes = notes

        return result

    def _perform_attribution_analysis(self, portfolio_data: Dict, benchmark_data: Dict) -> Dict:
        """Perform performance attribution analysis."""
        if len(portfolio_data['returns']) != len(benchmark_data['returns']):
            return {'error': 'Portfolio and benchmark data length mismatch'}

        # Calculate risk-adjusted attribution
        risk_adjusted = self.attribution_analyzer.calculate_risk_adjusted_attribution(
            portfolio_data['returns'],
            benchmark_data['returns']
        )

        # Sample sector attribution (for demonstration)
        portfolio_weights = {"Large Cap": 0.8, "Mid Cap": 0.15, "Small Cap": 0.05}
        portfolio_returns = {"Large Cap": 0.12, "Mid Cap": 0.10, "Small Cap": 0.08}
        benchmark_weights = {"Large Cap": 0.75, "Mid Cap": 0.20, "Small Cap": 0.05}
        benchmark_returns = {"Large Cap": 0.11, "Mid Cap": 0.09, "Small Cap": 0.07}

        sector_attribution = self.attribution_analyzer.calculate_brinson_attribution(
            portfolio_weights, portfolio_returns, benchmark_weights, benchmark_returns
        )

        return {
            'risk_adjusted_metrics': risk_adjusted,
            'sector_attribution': sector_attribution
        }

    def _validate_benchmark_selection(self, benchmark_symbol: str) -> Dict:
        """Validate benchmark selection appropriateness."""
        portfolio_characteristics = {
            "asset_class": "equity",
            "geography": "US",
            "investment_style": "large_cap_blend",
            "market_cap_focus": "large_cap"
        }

        # Define benchmark characteristics based on symbol
        benchmark_chars_map = {
            "SPY": {
                "asset_class": "equity",
                "geography": "US",
                "investment_style": "large_cap_blend",
                "market_cap_focus": "large_cap"
            },
            "QQQ": {
                "asset_class": "equity",
                "geography": "US",
                "investment_style": "large_cap_growth",
                "market_cap_focus": "large_cap"
            },
            "IWM": {
                "asset_class": "equity",
                "geography": "US",
                "investment_style": "small_cap_blend",
                "market_cap_focus": "small_cap"
            }
        }

        benchmark_characteristics = benchmark_chars_map.get(benchmark_symbol, {
            "asset_class": "unknown",
            "geography": "unknown",
            "investment_style": "unknown"
        })

        is_appropriate, validation_notes = self.benchmark_standardizer.validate_benchmark_appropriateness(
            portfolio_characteristics, benchmark_characteristics
        )

        return {
            'is_appropriate': is_appropriate,
            'validation_notes': validation_notes,
            'portfolio_characteristics': portfolio_characteristics,
            'benchmark_characteristics': benchmark_characteristics
        }
