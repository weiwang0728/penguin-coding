#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# AddsrcDirectorytoPythonPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from data_manager import DataManager

def test_product_management():
    """TestProductAttributeManagementFunction"""
    try:
        data_manager = DataManager()
        
        # InitialInitializationSampleData
        data_manager.initialize_sample_data()
        print("SUCCESS: SampleDataInitialInitializationCompleteSuccess")
        
        # TestAddProductBrand（UseUseNotConflictID）
        new_product = {
            'product_id': 301,
            'name': 'TestProductBrand',
            'category': 'Electronics',
            'price': 999.99,
            'brand': 'TestBrandBrand'
        }
        
        result = data_manager.add_product(new_product)
        if result:
            print("SUCCESS: ProductBrandAddSuccess")
        
        # TestViewProductList
        products = data_manager.get_products_list()
        if len(products) >= 5:
            print(f"SUCCESS: ProductBrandListViewSuccess，Contains{len(products)}item(s)ProductBrand")
        
        return True
        
    except Exception as e:
        print(f"ERROR: ProductBrandManagementTest Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_product_management()
    sys.exit(0 if success else 1)
