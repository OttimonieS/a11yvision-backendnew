import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, EmailStr

from api import start_scan

app = FastAPI(title='Accessibility Auditor API', version='0.1.0')
app.add_middleware(
	CORSMiddleware,
	allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173', '*'],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

# mount screenshots directory for frontend access
screenshots_dir = os.path.join(os.getcwd(), 'data', 'screenshots')
os.makedirs(screenshots_dir, exist_ok=True)
app.mount('/screenshots', StaticFiles(directory=screenshots_dir), name='screenshots')


class SignUpRequest(BaseModel):
	email: EmailStr
	password: str
	name: str

class SignInRequest(BaseModel):
	email: EmailStr
	password: str

class SettingsUpdateRequest(BaseModel):
	contrastThreshold: Optional[str] = None
	enableTargetSize: Optional[bool] = None
	rescanCadence: Optional[str] = None

class ScanRequest(BaseModel):
	url: HttpUrl
	mode: str = 'static'


# in-memory store for MVP (replace with DB in production)
SCANS: Dict[str, dict] = {}
USERS: Dict[str, dict] = {}  # email -> user object
SESSIONS: Dict[str, dict] = {}  # token -> {userId, email, createdAt}
SETTINGS: Dict[str, dict] = {}  # userId -> settings
API_KEYS: Dict[str, dict] = {}  # userId -> list of keys


def _set_status(scan_id: str, data: dict) -> None:
	now = datetime.utcnow().isoformat() + 'Z'
	existing = SCANS.get(scan_id, {})
	merged = {**existing, **data, 'updatedAt': now}
	SCANS[scan_id] = merged

def _hash_password(password: str) -> str:
	return hashlib.sha256(password.encode()).hexdigest()

def _verify_token(authorization: Optional[str]) -> Optional[dict]:
	if not authorization or not authorization.startswith('Bearer '):
		return None
	token = authorization[7:]
	return SESSIONS.get(token)


@app.post('/api/v1/auth/signup')
async def signup(req: SignUpRequest):
	if req.email in USERS:
		raise HTTPException(status_code=400, detail='User already exists')
	user_id = str(uuid.uuid4())
	USERS[req.email] = {
		'userId': user_id,
		'email': req.email,
		'name': req.name,
		'passwordHash': _hash_password(req.password),
		'createdAt': datetime.utcnow().isoformat() + 'Z',
	}
	token = secrets.token_urlsafe(32)
	SESSIONS[token] = {'userId': user_id, 'email': req.email, 'createdAt': datetime.utcnow().isoformat() + 'Z'}
	return {'token': token, 'user': {'userId': user_id, 'email': req.email, 'name': req.name}}

@app.post('/api/v1/auth/signin')
async def signin(req: SignInRequest):
	user = USERS.get(req.email)
	if not user or user['passwordHash'] != _hash_password(req.password):
		raise HTTPException(status_code=401, detail='Invalid credentials')
	token = secrets.token_urlsafe(32)
	SESSIONS[token] = {'userId': user['userId'], 'email': req.email, 'createdAt': datetime.utcnow().isoformat() + 'Z'}
	return {'token': token, 'user': {'userId': user['userId'], 'email': req.email, 'name': user['name']}}

@app.post('/api/v1/auth/logout')
async def logout(authorization: Optional[str] = Header(None)):
	session = _verify_token(authorization)
	if not session or not authorization:
		raise HTTPException(status_code=401, detail='Unauthorized')
	token = authorization[7:]
	SESSIONS.pop(token, None)
	return {'ok': True}

@app.get('/api/v1/auth/me')
async def get_current_user(authorization: Optional[str] = Header(None)):
	session = _verify_token(authorization)
	if not session:
		raise HTTPException(status_code=401, detail='Unauthorized')
	user = USERS.get(session['email'])
	if not user:
		raise HTTPException(status_code=404, detail='User not found')
	return {'user': {'userId': user['userId'], 'email': user['email'], 'name': user['name']}}

@app.get('/api/v1/stats')
async def get_stats():
	"""Aggregate stats for dashboard."""
	total_scans = len(SCANS)
	completed = sum(1 for s in SCANS.values() if s.get('status') == 'done')
	all_issues = []
	for scan in SCANS.values():
		if scan.get('result') and 'issues' in scan['result']:
			all_issues.extend(scan['result']['issues'])
	critical = sum(1 for i in all_issues if i.get('severity') in ['critical', 'major'])
	minor = sum(1 for i in all_issues if i.get('severity') == 'minor')
	return {
		'totalScans': total_scans,
		'completedScans': completed,
		'totalIssues': len(all_issues),
		'criticalIssues': critical,
		'minorIssues': minor,
	}

@app.get('/api/v1/settings')
async def get_settings(authorization: Optional[str] = Header(None)):
	session = _verify_token(authorization)
	if not session:
		return {'contrastThreshold': 'WCAG_AA', 'enableTargetSize': True, 'rescanCadence': 'manual'}
	settings = SETTINGS.get(session['userId'], {})
	return {
		'contrastThreshold': settings.get('contrastThreshold', 'WCAG_AA'),
		'enableTargetSize': settings.get('enableTargetSize', True),
		'rescanCadence': settings.get('rescanCadence', 'manual'),
	}

@app.put('/api/v1/settings')
async def update_settings(req: SettingsUpdateRequest, authorization: Optional[str] = Header(None)):
	session = _verify_token(authorization)
	if not session:
		raise HTTPException(status_code=401, detail='Unauthorized')
	user_id = session['userId']
	if user_id not in SETTINGS:
		SETTINGS[user_id] = {}
	if req.contrastThreshold:
		SETTINGS[user_id]['contrastThreshold'] = req.contrastThreshold
	if req.enableTargetSize is not None:
		SETTINGS[user_id]['enableTargetSize'] = req.enableTargetSize
	if req.rescanCadence:
		SETTINGS[user_id]['rescanCadence'] = req.rescanCadence
	return SETTINGS[user_id]

class ApiKeyCreateRequest(BaseModel):
	label: str

@app.post('/api/v1/api-keys')
async def create_api_key(req: ApiKeyCreateRequest, authorization: str = Header(None)):
	"""Create a new API key for the authenticated user"""
	session = _verify_token(authorization)
	user_id = session['userId']  # type: ignore

	key_id = str(uuid.uuid4())
	key_value = secrets.token_urlsafe(32)
	API_KEYS[key_id] = {
		'keyId': key_id,
		'userId': user_id,
		'label': req.label,
		'keyValue': key_value,
		'createdAt': datetime.utcnow().isoformat()
	}
	return API_KEYS[key_id]

@app.get('/api/v1/api-keys')
async def list_api_keys(authorization: str = Header(None)):
	"""List all API keys for the authenticated user"""
	session = _verify_token(authorization)
	user_id = session['userId']  # type: ignore

	user_keys = [
		{k: v for k, v in key.items() if k != 'keyValue'}  # Don't expose key value
		for key in API_KEYS.values()
		if key['userId'] == user_id
	]
	return {'items': user_keys}

@app.delete('/api/v1/api-keys/{key_id}')
async def delete_api_key(key_id: str, authorization: str = Header(None)):
	"""Delete an API key"""
	session = _verify_token(authorization)
	user_id = session['userId']  # type: ignore

	if key_id not in API_KEYS:
		raise HTTPException(404, 'API key not found')
	if API_KEYS[key_id]['userId'] != user_id:
		raise HTTPException(403, 'Not authorized')

	del API_KEYS[key_id]
	return {'message': 'API key deleted'}

@app.get('/api/v1/scans')
async def list_scans():
	"""Return list of all scans with summary fields (no heavy issues list)."""
	items = []
	for sid, data in SCANS.items():
		result = data.get('result')
		issues = result.get('issues', []) if result else []
		items.append({
			'scanId': sid,
			'url': data.get('url'),
			'status': data.get('status'),
			'createdAt': data.get('createdAt'),
			'updatedAt': data.get('updatedAt'),
			'issuesCount': len(issues),
		})
	return {'items': sorted(items, key=lambda x: x['createdAt'], reverse=True)}


@app.post('/api/v1/scans')
async def create_scan(req: ScanRequest):
	scan_id = str(uuid.uuid4())
	SCANS[scan_id] = {
		'scanId': scan_id,
		'url': str(req.url),
		'status': 'queued',
		'createdAt': datetime.utcnow().isoformat() + 'Z',
		'updatedAt': datetime.utcnow().isoformat() + 'Z',
		'progress': {
			'render': 'pending',
			'preprocess': 'pending',
			'inference': 'pending',
			'aggregate': 'pending',
		},
	}
	start_scan(scan_id, str(req.url), _set_status)
	return {'scanId': scan_id, 'status': 'queued', 'estimatedEtaSeconds': 8}


@app.get('/api/v1/scans/{scan_id}')
async def get_scan_status(scan_id: str):
	data = SCANS.get(scan_id)
	if not data:
		return {'scanId': scan_id, 'status': 'not_found'}
	# summarize if results exist
	result = data.get('result')
	if result and 'issues' in result:
		issues = result['issues']
		data['resultSummary'] = {
			'coverage': 72,
			'issuesCount': len(issues),
			'critical': sum(1 for i in issues if i.get('severity') == 'critical'),
			'major': sum(1 for i in issues if i.get('severity') == 'major'),
			'minor': sum(1 for i in issues if i.get('severity') == 'minor'),
		}
		data['progress'] = {
			'render': 'done',
			'preprocess': 'done',
			'inference': 'done',
			'aggregate': 'done',
		}
	return data


@app.get('/api/v1/scans/{scan_id}/result')
async def get_scan_result(scan_id: str):
	data = SCANS.get(scan_id)
	if not data or 'result' not in data:
		return {'scanId': scan_id, 'status': 'not_ready'}
	result = data['result']
	return {
		'scanId': scan_id,
		'url': data.get('url'),
		'scores': {'coverage': 72, 'accessibilityScore': 68},
		'issues': result.get('issues', []),
		'screenshots': [
			{
				'id': 'primary',
				'url': result.get('screenshotPath'),
				'viewport': {'width': 1280, 'height': 800},
			}
		],
	}


@app.get('/api/v1/scans/{scan_id}/issues')
async def get_scan_issues(scan_id: str):
	data = SCANS.get(scan_id)
	if not data or 'result' not in data:
		return {'scanId': scan_id, 'status': 'not_ready', 'issues': []}
	issues = data['result'].get('issues', [])
	return {'scanId': scan_id, 'count': len(issues), 'issues': issues}


@app.post('/api/v1/uploads')
async def upload_screenshot(file: UploadFile = File(...)):
	uploads_dir = os.path.join(os.getcwd(), 'data', 'uploads')
	os.makedirs(uploads_dir, exist_ok=True)
	file_id = str(uuid.uuid4())
	dest = os.path.join(uploads_dir, f'{file_id}_{file.filename}')
	content = await file.read()
	with open(dest, 'wb') as f:
		f.write(content)
	return {
		'uploadId': file_id,
		's3Url': dest,
		'thumbnailUrl': dest,
	}


@app.get('/health')
async def health():
	return {'ok': True}