#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# AddsrcDirectorytoPythonPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from utils.matrix_utils import MatrixUtils
import pandas as pd

def test_tfidf_matrix_transform():
    """TestTF-IDFMatrix TransformationFunction"""
    try:
        # CreateTestData
        ratings_df = pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3, 3],
            'product_id': [1, 2, 1, 3, 2, 3],
            'rating': [5.0, 4.0, 3.0, 5.0, 4.0, 3.0]
        })
        
        products_df = pd.DataFrame({
            'product_id': [1, 2, 3],
            'category': ['Electronics', 'Clothing', 'Home'],
            'brand': ['BrandBrandA', 'BrandBrandB', 'BrandBrandC'],
            'price_range': ['MidPrice', 'LowPrice', 'HighPrice']
        })
        
        # ExecuteMatrix Transformation
        user_attribute_matrix = MatrixUtils.create_user_attribute_matrix(ratings_df, products_df)
        
        # SaveResult
        output_path = '../evaluation/tfidf_output.csv'
        user_attribute_matrix.to_csv(output_path)
        
        print("SUCCESS: TF-IDFMatrix TransformationSuccess")
        print(f"MatrixDimensionRepublic: {user_attribute_matrix.shape}")
        print(f"OutputFile: {output_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Matrix TransformationFailure: {e}")
        return False

if __name__ == "__main__":
    success = test_tfidf_matrix_transform()
    sys.exit(0 if success else 1)
