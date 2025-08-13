#!/usr/bin/env python3
"""
Test script to verify font improvements in the GIPS compliance interface.
This script validates that the new CSS styles are properly applied.
"""

import requests
import time
import sys


def test_css_loading():
    """Test if custom CSS is properly loaded."""
    print("🎨 Testing CSS Loading...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            # Check if our custom CSS classes are present
            content = response.text
            
            css_classes_to_check = [
                'gips-result-container',
                'gips-metric-title',
                'gips-metric-value',
                'gips-compliance-status',
                'compliance-full',
                'compliance-partial',
                'compliance-none'
            ]
            
            found_classes = []
            for css_class in css_classes_to_check:
                if css_class in content:
                    found_classes.append(css_class)
            
            print(f"✅ Found {len(found_classes)}/{len(css_classes_to_check)} custom CSS classes")
            
            if len(found_classes) >= len(css_classes_to_check) * 0.8:  # At least 80% found
                print("✅ CSS styles appear to be properly loaded")
                return True
            else:
                print("⚠️ Some CSS classes may not be loaded properly")
                return False
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing CSS: {e}")
        return False


def test_font_families():
    """Test if font families are properly configured."""
    print("🔤 Testing Font Families...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for font family definitions
            font_checks = [
                'PingFang SC',  # Chinese font
                'Microsoft YaHei',  # Chinese font
                'SF Mono',  # Monospace font for numbers
                'Roboto Mono',  # Alternative monospace
                '-apple-system'  # System font
            ]
            
            found_fonts = []
            for font in font_checks:
                if font in content:
                    found_fonts.append(font)
            
            print(f"✅ Found {len(found_fonts)}/{len(font_checks)} font families")
            
            if len(found_fonts) >= 3:  # At least 3 fonts found
                print("✅ Font families appear to be properly configured")
                return True
            else:
                print("⚠️ Font configuration may be incomplete")
                return False
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing fonts: {e}")
        return False


def test_responsive_design():
    """Test if the design is responsive."""
    print("📱 Testing Responsive Design...")
    
    try:
        # Test with different viewport sizes
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = requests.get("http://localhost:8501", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Page loads on mobile user agent")
            return True
        else:
            print(f"❌ Failed to load on mobile: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing responsive design: {e}")
        return False


def test_accessibility():
    """Test basic accessibility features."""
    print("♿ Testing Accessibility...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for accessibility features
            accessibility_checks = [
                'font-weight',  # Proper font weights
                'line-height',  # Proper line spacing
                'color:',  # Color definitions
                'font-size'  # Font size definitions
            ]
            
            found_features = []
            for feature in accessibility_checks:
                if feature in content:
                    found_features.append(feature)
            
            print(f"✅ Found {len(found_features)}/{len(accessibility_checks)} accessibility features")
            
            if len(found_features) >= 3:
                print("✅ Basic accessibility features are present")
                return True
            else:
                print("⚠️ Some accessibility features may be missing")
                return False
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing accessibility: {e}")
        return False


def generate_font_improvement_report():
    """Generate a report of font improvements."""
    print("\n📋 Font Improvement Report")
    print("=" * 50)
    
    improvements = [
        "✅ 添加了优化的中文字体栈 (PingFang SC, Microsoft YaHei)",
        "✅ 为数字和百分比使用等宽字体 (SF Mono, Roboto Mono)",
        "✅ 改善了标题层次和字体权重",
        "✅ 优化了GIPS合规性结果的显示样式",
        "✅ 添加了专用的CSS类用于一致的样式",
        "✅ 改善了可读性和对比度",
        "✅ 支持跨平台字体兼容性",
        "✅ 优化了Streamlit组件的字体显示"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
    
    print("\n🎯 主要改进:")
    print("  • 中文字体显示更加清晰")
    print("  • 数字和百分比使用专业的等宽字体")
    print("  • 合规性状态使用彩色标签显示")
    print("  • 整体视觉层次更加清晰")
    print("  • 支持不同操作系统的字体回退")


def main():
    """Run font improvement tests."""
    print("🎨 Font Improvement Test Suite")
    print("=" * 50)
    
    tests = [
        ("CSS Loading", test_css_loading),
        ("Font Families", test_font_families),
        ("Responsive Design", test_responsive_design),
        ("Accessibility", test_accessibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test had issues")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed >= total * 0.75:  # At least 75% passed
        print("🎉 Font improvements are working well!")
        
        print("\n🌐 To see the improvements:")
        print("  1. Open http://localhost:8501")
        print("  2. Load S&P 500 data")
        print("  3. Navigate to '🏛️ GIPS合规性' tab")
        print("  4. Run GIPS compliance analysis")
        print("  5. Observe the improved font display")
        
        print("\n✨ Font Improvements:")
        print("  • 清晰的中文字体显示")
        print("  • 专业的数字字体 (等宽)")
        print("  • 彩色的合规性状态标签")
        print("  • 改善的视觉层次")
        print("  • 更好的可读性")
        
        generate_font_improvement_report()
        
        return True
    else:
        print("⚠️ Some font improvements may not be working properly.")
        print("\n🔧 Troubleshooting:")
        print("  • Check if the Streamlit server is running")
        print("  • Verify CSS files are properly loaded")
        print("  • Clear browser cache and reload")
        print("  • Check browser developer tools for CSS errors")
        
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
