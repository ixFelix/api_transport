#!/usr/bin/env python
# coding: utf-8

import os
import pickle
import plot
import pandas as pd
import numpy as np
import sys
import tools

readPath="data_storage/stationResponse/"
savePath="data_storage/" # must be different from readPath
saveFile="df_stationDepartures"

def readFiles():
	fileNames = os.listdir(readPath)
	readFiles = [None for i in range(len(fileNames))] # 0: file, 1: departures?
	for i in range(len(fileNames)):
		loaded = tools.load(readPath+fileNames[i])
		if type(loaded)==dict: # new storage type, else old
			loaded = loaded["departure"]
		readFiles[i] = loaded
	return readFiles

def clean_stage0(readFiles): # connect different files to one list
	cleaned_stage0 = [None for i in range(len(readFiles))]
	for i in range(len(readFiles)):
		#print("try",i)
		cleaned_stage0[i]=readFiles[i]#["DepartureBoard"]["Departure"]
	#plot.plotDict(cleaned_stage0[0][0])
	return cleaned_stage0

def clean_stage1(cleaned_stage0): # connect different trains to one list
	cleaned_stage1 = [None for i in range(1000)]
	counter=0
	for i in range(len(cleaned_stage0)):
		cleaned_stage1[counter:counter+len(cleaned_stage0[i])] = cleaned_stage0[i]
		counter += len(cleaned_stage0[i])
	#print(counter)
	return cleaned_stage1

def removeNanAtEnd(cleaned_stage1):
	countIt=0
	for i in range(len(cleaned_stage1)):
		if not type(cleaned_stage1[i])==type(None):
			countIt+=1
	#print(countIt)
	cleaned_stage1 = cleaned_stage1[0:countIt]
	return cleaned_stage1

def unwrapColumns(df): # only one value per cell!
	def handle_col(df, col, removeLayer=False):
		columns = list(df[col][0].keys())
		NewColumns = [str(col)+"_"+s for s in list(df[col][0].keys())]
		df_add = pd.DataFrame(list(df[col]), columns=columns)
		renaming = {columns[i]:NewColumns[i] for i in range(len(columns))}
		df = pd.concat([df,df_add], axis=1, sort=1)
		df=df.drop([col], axis=1)
		df = df.rename(columns=renaming)
		return df
	
	def handle_stop(df, column="stop"):
		df_add = pd.DataFrame(list(df["stop"]), columns=df["stop"][0].keys())
		df = pd.concat([df,df_add], axis=1, sort=1)
		df=df.drop(["stop"], axis=1)
		return df

	def handle_Product(df):
		keys = list(df["Product"][0].keys())
		length=len(df.index)
		for i in range(len(keys)):
			values = [None for index in range(length)]
			for j in range(length):
				values[j] = df["Product"][j][keys[i]]
			df["@Product_"+keys[i]] = values
		df = df.drop(["Product"], axis=1)
		return df
	
	def handle_notes(df):
		keys = list(df["Notes"][0]["Note"].keys())
		length=len(df.index)
		for i in range(len(keys)):
			values = [None for index in range(length)]
			for j in range(length):
				values[j] = df["Notes"][j]["Note"][keys[i]]
			df["@Notes_"+keys[i]] = values
		df = df.drop(["Notes"], axis=1)
		return df

	df = handle_col(df, "line")
	df = handle_col(df, "line_operator")
	#df = handle_col(df, "remarks", True)
	df = handle_col(df, "stop")
	df = handle_col(df, "stop_location")
	df = handle_col(df, "stop_products")
	return df

readFiles = readFiles()							# read files
#plot.plotDict(readFiles[0][0])#["DepartureBoard"]["Departure"][0])
cleaned_stage0 = clean_stage0(readFiles)		# connect files
cleaned_stage1 = clean_stage1(cleaned_stage0)	# connect trains
cleaned_stage2 = removeNanAtEnd(cleaned_stage1)
df = pd.DataFrame(cleaned_stage2, columns=cleaned_stage2[0].keys())

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
#print(df)
df = unwrapColumns(df) # remover deeper levels and add new columns instead
#print("new")
print(df[["when", "delay", "line_name", "direction"]])
#print(df.head())
stopit()

#print(df[397:400])
#print(df.loc[[32,49]])

lenBefore=len(df.index)
df = df.drop_duplicates(keep="last", subset=["@name","@direction","@date","@time","@stopExtId"])
df = df.sort_values(by =['@date', '@time'])
lenAfter = len(df.index)
print("  removed "+str(lenBefore-lenAfter)+" entries. Remaining: "+str(lenAfter))

#print(df[["@name","@direction","@date","@time"]])

def saveDf(df):
	timeString = tools.getMilliTimeString()
	tools.save(df, savePath+saveFile+"_"+timeString+".c")

saveDf(df)