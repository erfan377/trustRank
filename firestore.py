import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from constants import *
import json
from urllib.parse import urlparse
import fire


def filter(load_name, save_name="filtered_all"):
    f = open(load_name)
    data = json.load(f)
    filtered_data = {}
    i = 0
    for url in data:
        detail = data[url]
        if len(detail["sources"]) > 2:
            filtered_data[url] = detail
            i += 1
    print(i)
    with open(save_name + '.json', 'w') as fp:
        json.dump(filtered_data, fp,  indent=4)


def upload_safe(name):
    cred = credentials.Certificate('hexatorch-cabb8-135858617a8b-erfan.json')
    firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECTID,
    })

    db = firestore.client()

    f = open(name)
    data = json.load(f)
    for url in data:
        detail = data[url]
        detail["name"].sort()
        documentID = detail["name"][0]
        sources = detail["sources"]
        doc_ref = db.collection(u'approved_links').document(documentID)
        doc_ref.set(
            {"URLs": [{"URL": url, "Source": sources}]}
        )
        print('Uploaded', url, documentID)


def upload_safe_man(name):
    cred = credentials.Certificate('hexatorch-cabb8-135858617a8b-erfan.json')
    firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECTID,
    })

    db = firestore.client()

    f = open(name)
    data = json.load(f)
    data = data["arr"]
    for item in data:
        # breakpoint()
        documentID = item["name"]
        for url in item["url"]:
            netloc = urlparse(url).netloc
            sources = ["manual"]
            doc_ref = db.collection(u'approved_links').document(documentID)
            doc_ref.set(
                {"URLs": [{"URL": netloc, "Source": sources}]}
            )
            print('Uploaded', url, documentID)


if __name__ == '__main__':
    fire.Fire()
