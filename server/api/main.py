import os
import datetime
import json

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api import database, crud

import engines.lenna_standard as lenna_standard
model = lenna_standard.Model() # the transformer model

import engines.ibm_translate_lite as ibm_translate
translate = ibm_translate.Translate() # the translator model

print(datetime.datetime.now())

app = FastAPI(openapi_url=None)

# Enable CORS

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index(db: Session = Depends(database.get_db)):
    return {'STATUS' : 'OK'}

@app.get('/conv_append')
def conv_append(key: str, 
	conv_id: int, 
	kbase: str,
	utterance: str, 
	engine: int = 0, 
	sample_count: int = 2,
	memory_size: int = 2, 
	memory_append: bool = False, db: Session = Depends(database.get_db)):
	
	#### make sure the values given are within a certain range ###
	sample_count, memory_size = max(0, min(3, sample_count)), max(0, min(3, memory_size))

	#### Get user_id using params::key ###
	try: user_id = crud.get_user_from_key(db, key) 
	except: raise HTTPException(status_code=400, detail="PARAMS::KEY INVALID")

	### Get conversation using params::conv_id ###
	try: 
		if crud.get_user_qgroup_collection(db, user_id, conv_id, 1) == None: raise Exception()
		qg_contents = [{'request' : q.request, 'response' : q.response} for q in 
			crud.get_user_qgroup_content(db, user_id, conv_id, memory_size)][::-1]
	except: raise HTTPException(status_code=400, detail="PARAMS::CONV_ID INVALID")

	### Get knowledge base using params::kbase ###
	try:
		kb_contents = json.loads(crud.get_user_kbase_content(db, user_id, kbase))
		if kb_contents == None: raise Exception()
	except: raise HTTPException(status_code=400, detail="PARAMS::KBASE INVALID")

	try:
		configuration = crud.get_conf_from_user(db, user_id)
	except: raise HTTPException(status_code=500, detail="INTERNAL ERROR")

	### Select engine using params::engine ###
	if engine == 0:
		kb_header = lenna_standard.kb_headers[kb_contents["format"]];

		if configuration.basic_language == "1":
			sl_utterance = translate.translate(utterance, source_language="el", target_language="en") #### translate to en ###
		else:
			sl_utterance = utterance

		response, duration = model.generate_simple(utterance) #### run the language model ###

		if configuration.basic_language == "1":
			tl_response = translate.translate(response, source_language="en", target_language="el") #### translate to el ###
		else:
			tl_response = response
		print(tl_response)

		print(user_id, conv_id, sl_utterance, response, int(memory_append), datetime.datetime.now())
		#### store the query inside the query group ###
		crud.new_user_qgroup_content(db, user_id, conv_id, sl_utterance, response, int(memory_append), datetime.datetime.now())

		return {'STATUS' : 'OK', 'RESPONSE' : tl_response, 'CANDIDATES': None, 'DURATION': duration}
	else:
		raise HTTPException(status_code=400, detail="PARAMS::ENGINE INVALID")

	raise HTTPException(status_code=500, detail="SOMETHING WENT WRONG")

@app.get('/conv_create', status_code=201)
def conv_create(key: str, db: Session = Depends(database.get_db)):
	#### Get user_id using params::key ###
	try: user_id = crud.get_user_from_key(db, key) 
	except: raise HTTPException(status_code=400, detail="PARAMS::KEY INVALID")

	#### Get user's configuration using user_id ###
	try:
		configuration = crud.get_conf_from_user(db, user_id)
		default_greeting = configuration.basic_greeting
	except: raise HTTPException(status_code=500, detail="INTERNAL ERROR")

	#### Create new query group to store individual queries ###
	try: 
		qgroup_id = crud.get_user_qgroup_collection(db, user_id, None, 0)[0]
		qgroup_id = (qgroup_id + 1) if qgroup_id != None else 0
		crud.new_user_qgroup_collection(db, user_id, qgroup_id, datetime.datetime.now())
	except: raise HTTPException(status_code=500, detail="INTERNAL ERROR")

	if configuration.basic_language == "1":
		default_greeting = translate.translate(default_greeting, source_language="en", target_language="el")
	return {'STATUS' : 'OK', 'CONVERSATION_ID' : qgroup_id, 'RESPONSE' : default_greeting}
