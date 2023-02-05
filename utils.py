import json
import requests
import hashlib


def getConfig():
    return json.loads(open("config.json").read())


def check_if_updated(string, gistId):
    # Read the hash file
    with open("./data/textCacheHashes.json", "r") as f:
        hash_dict = json.load(f)
    # Calculate the hash of the string
    string_hash = hashlib.sha1(string.encode()).hexdigest()
    # If there is no entry in the hash file for this id, return True
    if (not gistId in hash_dict) or (string_hash != hash_dict[gistId]):
        hash_dict[gistId] = string_hash
        with open("./data/textCacheHashes.json", "w") as f:
            json.dump(hash_dict, f, indent=4)

        return True
    else:
        return False


def write_to_gist(text, gistFileName, gist_id=None):
    if gist_id != None:
        if not check_if_updated(text, gist_id):
            return gist_id
    # Set the endpoint for creating a new gist or updating an existing one
    if not gist_id:
        endpoint = "https://api.github.com/gists"
    else:
        endpoint = f"https://api.github.com/gists/{gist_id}"
    # Set the data to be sent to the endpoint
    data = {
        "description": gistFileName,
        "public": False,
        "files": {gistFileName + ".md": {"content": text}},
    }
    # Set the headers for the request
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer " + getConfig()["githubApiKey"],
    }
    # Send the request to the endpoint
    response = requests.post(endpoint, json=data, headers=headers)
    # Print the response status code to indicate success or failure
    gistId = response.json()["id"]
    updated = check_if_updated(text, gistId)
    return gistId


def getGistIdFromGUID(guid):
    # Read the hash file
    with open("./data/guidsToGistIds.json", "r") as f:
        guidToGistIdDict = json.load(f)
    # Calculate the hash of the string
    gistId = guidToGistIdDict[guid] if guid in guidToGistIdDict else None
    return gistId


def setGistIdForGUID(guid, gistId):
    # Read the hash file
    with open("./data/guidsToGistIds.json", "r") as f:
        guidToGistIdDict = json.load(f)

    guidToGistIdDict[guid] = gistId
    with open("./data/guidsToGistIds.json", "w") as f:
        json.dump(guidToGistIdDict, f, indent=4)


def createOrUpdateGist(guid, markdownText, gistFileName):
    gistId = getGistIdFromGUID(guid)
    # if gistId == None: the below function reassigns it to be the actual gist id of the created gist
    gistId = write_to_gist(markdownText, gistFileName, gist_id=gistId)
    setGistIdForGUID(guid, gistId)

    return gistId


def dict_to_markdown_list(urlList):
    markdown_list = ""
    for item in urlList:
        name, url = item["name"], item["url"]
        markdown_list += f"- [{name}]({url})\n"
    return markdown_list

def convertMdUrlToHtmlUrl(mdUrl):
    # convert a markdown formatted url to an <a href> formatted url string
    name = mdUrl.split("](")[0][1:]
    url = mdUrl.split("](")[1][:-1]
    return f'<a href="{url}">{name}</a>'

def markdown_to_html(markdown):
    html = ""
    lines = markdown.split("\n")
    current_indent = 0
    for i, line in enumerate(lines):
        nextLine = "-"
        if i + 1 < len(lines):
            nextLine = lines[i + 1]
        stripped_line = line.strip()
        nextLineIndent = nextLine.index("-")
        htmlUrl = stripped_line[2:]
        if nextLineIndent <= current_indent and "](" in stripped_line:
            htmlUrl = convertMdUrlToHtmlUrl(stripped_line[2:])
        if nextLineIndent > current_indent:
            html += "<details><summary>" + stripped_line[1:] + "</summary>\n<ul>\n"
        elif nextLineIndent == current_indent:
            html += "<li>" + htmlUrl + "</li>\n"
        elif nextLineIndent < current_indent:
            html += "<li>" + htmlUrl + "</li>\n"
            html += "</ul>\n</details>\n" * (current_indent - nextLineIndent)
        current_indent = nextLineIndent
    html += "</ul>\n"
    return html
