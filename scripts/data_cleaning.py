import pandas as pd
import re
import sys
import numpy as np
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy import distance
from sklearn.preprocessing import LabelEncoder
import holidays

class CleanData:
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="gokada")
        self.nigeria_holiday= holidays.Nigeria()
        pass

    def fill_missing(self,df: pd.DataFrame, method: str,columns: list) -> pd.DataFrame:
        """
        fill missing values with specified method "mean" or "median"
        """
        if method == "mean":
            for col in columns:
                df[col].fillna(df[col].mean(), inplace=True)

        elif method == "median":
            for col in columns:
                df[col].fillna(df[col].median(), inplace=True)
        else:
            print("Method unknown")
        
        return df

    def fill_start_time(self,df:pd.DataFrame,start_col:str,end_col:str,duration_col):
        """
        fill null/na start time values by subtracting duration from the end time
        """
        fill_values=  df.apply(lambda x:x[end_col] - pd.Timedelta(minutes=x[duration_col]),axis=1)
        
        df[start_col].fillna(fill_values,inplace=True)
        return df 

    def fill_end_time(self,df:pd.DataFrame,start_col:str,end_col:str,duration_col):
        """
        fill null/na end time values by adding duration to the start time
        """
        fill_values=  df.apply(lambda x:x[start_col] + pd.Timedelta(minutes=x[duration_col]),axis=1)
        
        df[end_col].fillna(fill_values,inplace=True)
        return df 
    def remove_space(self,df:pd.DataFrame):
        columns = df.columns
        for col in columns:
            no_space=re.sub(' +', '_', col.lower().strip())
            df.rename(columns={col:no_space},inplace=True)
        return df
    def reverse_location(self,df:pd.DataFrame,lat_col_name:str="latitude",lng_col_name:str="longitude",loc_col_name:str="location"):
        locator = self.geolocator
        df[loc_col_name] = df.apply(lambda x:str(locator.reverse(str(x[lat_col_name])+","+str(x[lng_col_name]))),axis=1)
        df[loc_col_name] = df[loc_col_name].apply(lambda x:self.spliter(x))
        return df

    def spliter(self,text:str,ind:int=-4):
        try:
            text=text.split(',')[ind]
            return text 
        except Exception:
            if ind > 1:
                print("Error occured")
                sys.exit(1)
            else:
                ind+=1
                return self.spliter(text,ind)

    def find_distance(self,df:pd.DataFrame,distance_col_name:str="distance",trip_origin_col_names:list=["trip_origin"],trip_destination_col_names:list=["trip_destination"]):
        if len(trip_destination_col_names) > 1 and len(trip_origin_col_names) > 1:
            df[distance_col_name]=df.apply(lambda x:distance.distance((x[trip_origin_col_names[0]],x[trip_origin_col_names[1]]), (x[trip_destination_col_names[0]],x[trip_destination_col_names[1]])).km,axis=1)
        else:
            df[distance_col_name]=df.apply(lambda x:distance.distance((x[trip_origin_col_names[0]]), (x[trip_destination_col_names[0]])).km,axis=1)
        return df

    