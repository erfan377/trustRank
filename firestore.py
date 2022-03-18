import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from constants import *
import json

cred = credentials.Certificate('fromfs.json')
firebase_admin.initialize_app(cred, {
    'projectId': "lighthouse-758b0",
})

db = firestore.client()


def upload_safe(name):
    f = open(name)
    data = json.load(f)
    for url in data:
        breakpoint()
        detail = data[url]
        documentID = detail["name"][0]
        sources = detail["sources"]
        doc_ref = db.collection(u'cities').document(documentID)
        doc_ref.set(
            {"URLs": [{"URL": url, "Source": sources}]}
        )
        print('Uploaded', url, documentID)
