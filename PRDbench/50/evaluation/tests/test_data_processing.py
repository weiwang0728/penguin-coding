
import os
import pandas as pd
from src.data_analyze_scripts.data_preparation import clean_music_data
from src.data_analyze_scripts.predict_play_counts import predict_play_counts

def test_clean_music_list():
    # Create a dummy music_list.csv for testing
    dummy_data = {'list_name': ['test1', 'test2'], 'creator': ['user1', 'user2']}
    dummy_df = pd.DataFrame(dummy_data)
    dummy_df.to_csv('src/music_data/music_list.csv', index=False)

    clean_music_data('src/music_data/music_list.csv', 'src/music_data/cleaned_music_list.csv')
    assert os.path.exists('src/music_data/cleaned_music_list.csv')

def test_clean_music_detail():
    # Create a dummy music_detail.csv for testing
    dummy_data = {'song_name': ['song1', 'song2'], 'artist': ['artist1', 'artist2']}
    dummy_df = pd.DataFrame(dummy_data)
    dummy_df.to_csv('src/music_data/music_detail.csv', index=False)

    clean_music_data('src/music_data/music_detail.csv', 'src/music_data/cleaned_music_detail.csv')
    assert os.path.exists('src/music_data/cleaned_music_detail.csv')

def test_prediction():
    # This is a placeholder test. In a real scenario, you would load the model
    # and test it with some sample data.
    predictions = predict_play_counts()
    assert len(predictions) == 20
    for p in predictions:
        assert p >= 0
