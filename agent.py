import time
from sqlalchemy import create_engine
from func import download_gpx, gpx_to_png, get_temp, get_region, get_step, get_terrain, heat_matrix, norm_or_not, data_augmentation
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
import os
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def linkk(path):
    link = []
    with open(path, mode="r") as f:
        for i in f:
            link.append(i.strip())
    
    return link

def sql_post(df, name):
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5430/postgres", )
    df.to_sql(name, con=engine, if_exists="replace", index=False)

def sql_get(name):
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5430/postgres")
    df = pd.read_sql(name, con=engine)
    return df

def get_df_corr(df):
    le = LabelEncoder()
    df_corr = df.copy()
    df_corr['terrain_type'] = le.fit_transform(df['terrain_type'])
    df_corr["key_objects_str"] = le.fit_transform(df["key_objects_str"])
    df_corr['region'] = le.fit_transform(df['region'])

    df_corr['track_time'] = pd.to_datetime(df_corr['track_time'], errors="coerce")
    df_corr['season'] = df_corr['track_time'].dt.month % 12 // 3 + 1
    
    return df_corr


while True:
    try:
        print("Записываем ссылки в список")
        links = linkk("./Links.txt")
        print(f"Скачиваем GPX файлов...")
        download_gpx(links)
        print("создаем датафрейм")
        df = pd.DataFrame(columns=["track_id", "track_time", "latitude", "longitude", "altitude"])
        print(f"Создаем картинки...")
        df = gpx_to_png(df)
        print("Преоброзовываем дату")
        df['track_time'] = df['track_time'].dt.strftime('%Y-%m-%d')
        print(f"get_temp...")
        df = get_temp(df)
        
        sql_post(df, "track")
        
        print(f"get_region...")
        df = get_region(df)
        
        sql_post(df, "track")
        
        print(f"get_step...")
        df = get_step(df)
        
        sql_post(df, "track")
        
        print(f"get_terrain...")
        df = get_terrain(df)
        
        sql_post(df, "track")
        
        print("Кодирую датафрейм")
        df_corr = get_df_corr(df)
        
        sql_post(df, "track_encoded")
        
        
        print("heat_matrix")
        features = df_corr.drop(columns=["track_id", "track_time", "region"])
        heat_matrix(features)
        
        print(f"norm_or_not...")
        norm_or_not(features)
        
        print(f"data_augmentation...")
        data_augmentation()
        
        
        print("🎉 ЦИКЛ ЗАВЕРШЁН! Спим 1 час...")
        time.sleep(3600)
        
    except FileNotFoundError as e:
        print(f"Файл {e} не найден! Ждём...")
        time.sleep(60)
    except Exception as e:
        print(f"Ошибка: {e}. Ждём 5 мин...")
        # time.sleep(300)

