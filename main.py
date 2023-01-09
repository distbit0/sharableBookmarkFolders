import os
import json
import random
import string
from utils import *

# Recursive function to find bookmark folders with "SHARE" bookmark
def find_folders(bookmarks, share_folders):
    # Iterate through the children of the current bookmark object
    for child in bookmarks["children"]:
        # If the child is a folder, check if it has a bookmark called "SHARE"
        if child["type"] == "folder":
            # Check if the folder has a bookmark called "SHARE"
            has_share = any(
                bookmark["name"] == "SHARE" for bookmark in child["children"]
            )
            if has_share:
                # If the folder has a "SHARE" bookmark, append it to the share_folders list
                share_folders.append(child)
            # Recursively search the children of the current folder for more folders with "SHARE" bookmark
            find_folders(child, share_folders)


# Recursive function to build markdown list of urls from folder data structure
def build_markdown_list(folder, indent_level):
    markdown_list = []
    # Iterate through the children of the current folder
    for child in folder["children"]:
        # If the child is a bookmark, append it to the markdown list
        if child["type"] == "url" and child["name"] != "SHARE":
            markdown_list.append(" " * indent_level + "- " + child["url"])
        # If the child is a folder, add its name to the markdown list and recursively build the list for its children
        elif child["type"] == "folder":
            markdown_list.append(" " * indent_level + "- " + child["name"])
            markdown_list.extend(build_markdown_list(child, indent_level + 1))
    return markdown_list


def updateAllSHAREGists(bookmarks_file):
    gists = []
    with open(bookmarks_file, "r") as f:
        bookmarks = json.load(f)

    # Find all bookmark folders with "SHARE" bookmark
    share_folders = []
    find_folders(bookmarks["roots"]["bookmark_bar"], share_folders)

    # Iterate through the share folders
    for folder in share_folders:
        gistFileName = folder["name"]
        # Find the "SHARE" bookmark in the folder
        share_bookmark = next(
            bookmark for bookmark in folder["children"] if bookmark["name"] == "SHARE"
        )
        mdAsText = "\n".join(build_markdown_list(folder, 0))
        htmlFromMd = markdown_to_html(mdAsText)
        bookmarkGuid = share_bookmark["guid"]

        gistId = createOrUpdateGist(bookmarkGuid, htmlFromMd, gistFileName)
        gists.append({"name": gistFileName, "url": "https://gist.github.com/" + gistId})

    return gists


def writeGistLinksToFile(linksToGistsMd):
    config = getConfig()
    if "gistLinksOutputFile" in config and config["gistLinksOutputFile"] != "":
        with open(config["gistLinksOutputFile"], "w+") as f:
            f.write(linksToGistsMd)


if __name__ == "__main__":
    # Read the bookmarks file
    bookmarks_file = (
        "/home/pimania/.config/BraveSoftware/Brave-Browser/Default/Bookmarks"
    )
    gists = updateAllSHAREGists(bookmarks_file)
    linksToGistsMd = dict_to_markdown_list(gists)
    print(
        "https://gist.github.com/"
        + createOrUpdateGist("listOfGists", linksToGistsMd, "listOfGists")
    )
    writeGistLinksToFile(linksToGistsMd)
