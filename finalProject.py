import pandas as pd
import requests
import dash
from   dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

#Calls the NYC Data retrivial API and keeps adding 
#the results into a data frame until its full
def GetData(source):
	print(f"Getting data from: {source}")
	limit         = 100000
	offset        = 300000
	data          = []

	while True:
		q_string      = f"{source}?$limit={limit}&$offset={offset}"
		print(f'\tRows {offset} to {offset + limit}')
		payload = requests.get(q_string)
		txt = payload.json()
		if len(txt) == 0:
			print("\tall data collected")
			break
		else:
			#Add new data to existing data frame
			data += txt
			offset += 100000
	df = pd.DataFrame.from_records(data)
	return df

def DoWork():
	#Get the data
	source = r'https://data.cityofnewyork.us/resource/43nn-pn8j.json'
	df = GetData(source)

	#trim down to the columns that we will be using
	df = df[[
		"camis", "dba", "boro", 
		"zipcode", "cuisine_description", 
		"violation_description", "critical_flag", 
		"score", "grade", "inspection_date",
		"latitude", "longitude"
	]].copy()
	#convert inspection date column to date time
	df['inspection_date'] = pd.to_datetime(df['inspection_date'])

	#get the most recent review for each resturant
	df_recent = df.sort_values('inspection_date', ascending=False)
	df_recent = df_recent.drop_duplicates('camis', keep='first')
	
	#change long and lat to numerics
	df_recent["latitude"]  = pd.to_numeric(df_recent["latitude" ])
	df_recent["longitude"] = pd.to_numeric(df_recent["longitude"])
	
	#remove blanks from grade
	df_recent['grade'].replace('', np.nan, inplace=True)
	df_recent.dropna(subset=['grade'], inplace=True)
	
	#remove blanks from score, change to numeric
	df_recent['score'].replace('', np.nan, inplace=True)
	df_recent.dropna(subset=['score'], inplace=True)
	df_recent["score"]     = pd.to_numeric(df_recent["score"    ], )
	
	print("data frame complete")
	return df_recent


t = r'pk.eyJ1IjoibGluY2FycmllbGkiLCJhIjoiY2t4N3B0MGIyMGVsdDJucWhrMmptdDJmcSJ9.-LIUF4fIPi7_Is_71waYkQ'
px.set_mapbox_access_token(t)
df = DoWork()

#data groups
df_A = df[df['score'] == 'A']
df_B = df[df['score'] == 'B']
df_C = df[df['score'] == 'C']
print("sub groups made")
fig = px.scatter_mapbox(
	df,
	hover_data=['dba', 'grade'],
	lat="latitude", 
	lon="longitude", 
	color="grade", 
	size="score", 
	color_continuous_scale=px.colors.cyclical.IceFire, 
	size_max=15, 
	zoom=10)
print("mapbox complete")
fig.show()
print("program complete")