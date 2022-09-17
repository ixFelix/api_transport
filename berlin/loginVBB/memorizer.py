#!/usr/bin/env python
# coding: utf-8
import numpy as np
import pickle
import os
import tools

savePath="data_storage/"
saveFile="memoryNamesToExt.pickle"
memoryNamesToExt = {}

def doesItExist(name):
	if name in memoryNamesToExt.keys():
		return memoryNamesToExt[name]
	else:
		return False

def loadmemoryNamesToExt():
	ret=tools.load(savePath+saveFile)
	global memoryNamesToExt
	memoryNamesToExt = ret

def savememoryNamesToExt():
	tools.save(memoryNamesToExt,savePath+saveFile)

def addIfNew(name, ext):
	if name in memoryNamesToExt.keys():
		print(" memorizer already contains "+name+" with ext "+str(ext))
	else:
		print(" memorizer adds station "+name+" with ext "+str(ext))
		memoryNamesToExt.update( {name : ext} )
	savememoryNamesToExt()

if saveFile in os.listdir(savePath):
	loadmemoryNamesToExt()
