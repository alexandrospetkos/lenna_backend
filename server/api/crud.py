from sqlalchemy import func
from sqlalchemy.orm import Session
from api import models

# API

def get_user_from_key(db: Session, key: str):
	return db.query(models.ApiKey).filter(models.ApiKey.private_key == key).first().user_id

def get_conf_from_user(db: Session, user_id: int):
	return db.query(models.Conf).filter(models.Conf.user_id == user_id).first()

# QG

def get_user_qgroup_collection(db: Session, user_id: int, qgroup_id: int, mode: int):
	if mode == 0:
		return db.query(func.max(models.QGroup.query_group)).filter(models.QGroup.user_id == user_id).first()
	elif mode == 1:
		return db.query(models.QGroup).filter(models.QGroup.user_id == user_id, models.QGroup.query_group == qgroup_id).first()
	elif mode == 2:
		return db.query(models.QGroup).filter(models.QGroup.user_id == user_id).all()

def new_user_qgroup_collection(db: Session, user_id: int, qgroup_id: int, time):
	db_qgroup = models.QGroup(user_id=user_id, query_group=qgroup_id, time=time)
	db.add(db_qgroup)
	db.commit()
	db.refresh(db_qgroup)
	return db_qgroup

def get_user_qgroup_content(db: Session, user_id: int, qgroup_id: int, n_memory: int):
	return db.query(models.Query).filter(models.Query.user_id == user_id, 
		models.Query.query_group == qgroup_id, models.Query.in_memory == 1).order_by(models.Query.query_id.desc()).limit(n_memory)

def new_user_qgroup_content(db: Session, user_id: int, qgroup_id: int, request: str, response: str, in_memory: int, time):
	db_query = models.Query(query_group=qgroup_id, request=request, response=response, 
		in_memory=in_memory, time=time, user_id=user_id)
	db.add(db_query)
	db.commit()
	db.refresh(db_query)
	return db_query

# KB

def get_user_kbase_content(db: Session, user_id: int, kbase: str):
	if kbase.lower() == "default":
		return db.query(models.KBase).filter(models.KBase.name == kbase.lower()).first().body
	return db.query(models.KBase).filter(models.KBase.user_id == user_id, models.KBase.name == kbase).first().body




