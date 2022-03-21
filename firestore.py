import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from constants import *
import json
from urllib.parse import urlparse
import fire


def filter(load_name, save_name="filtered_all"):
    """filter the curated JSON from the websites based on your criteria

    Args:
        load_name (str): input JSON
        save_name (str, optional): Filtered JSON name to save. Defaults to "filtered_all".
    """
    f = open(load_name)
    data = json.load(f)
    filtered_data = {}
    i = 0  # count how many are kept
    for url in data:
        detail = data[url]
        # determined how many sources it should have been appeared in
        if len(detail["sources"]) > 2:
            filtered_data[url] = detail
            i += 1
    print(i)
    with open(save_name + '.json', 'w') as fp:
        json.dump(filtered_data, fp,  indent=4)


def add_data_online(documentID, netloc, sources, url_to_name, name_to_url, db, appending=False):
    # if url or name exists in the firestore, resolve the issue
    if netloc in url_to_name or documentID in name_to_url:
        # existing data in firestore
        if netloc in url_to_name and documentID not in name_to_url:
            try:
                print('error happened in this document', url_to_name[netloc])
            except:
                print('error happened in this document',
                      name_to_url[documentID])

            raise Exception(
                "THERE MIGHT BE SOME NAMING ISSUE, DO NOT DUPLICATE URLS UNDER DIFFERENT NAMES",
                netloc, documentID)
        if netloc in url_to_name and documentID in name_to_url:
            print("Found URL:", netloc,
                  "related names: ", url_to_name[netloc])
        if documentID in name_to_url:
            print("Found Name:", documentID,
                  "related URLs", name_to_url[documentID])
        # your new iput
        print("New URL: ", netloc, "or new name", documentID)

        # action to take
        val = input(
            "Put \n r for replacing " + documentID + " with " + netloc +
            "\n a for appending " + netloc + " to " + documentID + " list \n s for skip\n" or "s")
        # replace the old name with new URL entry
        if val == 'r':
            doc_ref = db.collection(
                u'approved_links').document(documentID)
            doc_ref.set(
                {"URLs": [{"URL": netloc, "Source": sources}]}
            )
        # append the new URL to the existing name
        elif val == 'a':
            doc_ref = db.collection(
                u'approved_links').document(documentID)
            doc_ref.set(
                {u"URLs": firestore.ArrayUnion([{"URL": netloc, "Source": sources}])}, merge=True)
        # do nothing
        elif val == 's':
            pass

    else:
        doc_ref = db.collection(u'approved_links').document(documentID)
        if appending:
            doc_ref.set(
                {u"URLs": firestore.ArrayUnion([{"URL": netloc, "Source": sources}])}, merge=True)
        else:
            doc_ref.set(
                {"URLs": [{"URL": netloc, "Source": sources}]}, merge=True)
        print('Uploaded', netloc, documentID)


def upload_safe(name, key_file="hexatorch-erfan.json"):
    """Upload the curated lists from the JSON filtered from major tracking lists

    Args:
        name (str): JSON file
    """
    cred = credentials.Certificate(key_file)
    firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECTID,
    })

    db = firestore.client()

    name_to_url, url_to_name = get_online_data(db)

    f = open(name)
    data = json.load(f)
    for url in data:
        detail = data[url]
        detail["name"].sort(key=len)
        documentID = detail["name"][0]  # Select the shortest name
        sources = detail["sources"]
        add_data_online(documentID, url, sources, url_to_name, name_to_url, db)


def get_online_data(db):
    """Read the firestore database and store its values
    in the mapping of URLs to the document they're saved under
    or the mapping of the names to the URLs it contains

    Args:
        db (_type_): firestore database

    Returns:
        dict: name map to its URLs, URL map to name saved under on
    """
    online_db = db.collection(u'approved_links')
    name_to_url = {}
    # reads the database
    for item in online_db.get():
        link_list = []
        for info in item.to_dict()["URLs"]:
            link_list.append(info["URL"])
        name_to_url[item.id] = link_list

    # reverses the previous dict
    url_to_name = {}
    for item in name_to_url:
        for url in name_to_url[item]:
            url_to_name[url] = item

    return name_to_url, url_to_name


def upload_safe_man(name, key_file="hexatorch-erfan.json"):
    """Add data manually from JSON to the firestore database

    Args:
        name (string): JSON path
    """
    # Initializing firestore, provide the correct keys for JSON
    cred = credentials.Certificate(key_file)
    firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECTID,
    })
    db = firestore.client()
    name_to_url, url_to_name = get_online_data(db)

    # format of json should be
    # {arr: [{"name": "NAME OF PROJECT", "url":["HTTPS://URL OF PROJECT"]}]}
    f = open(name)
    data = json.load(f)
    data = data["arr"]

    for item in data:
        documentID = item["name"]
        appending = False
        for url in item["url"]:
            # the url should be complete in json and should not be in netloc format
            netloc = urlparse(url).netloc
            add_data_online(documentID, netloc, [
                            "manual"], url_to_name, name_to_url, db, appending)
            appending = True


if __name__ == '__main__':
    fire.Fire()
