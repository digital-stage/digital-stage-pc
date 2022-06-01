import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime


def main():
    version = get_env_or_exit("JN_VERSION")
    signature = get_env_or_exit("JN_SIGNATURE")
    release_features = get_env_or_exit("JN_RELEASE_FEATURES")
    release_bugfixes = get_env_or_exit("JN_RELEASE_BUGFIXES")

    handle_rss(version, signature)
    handle_release_notes(version, release_bugfixes, release_features)


def handle_rss(version: str, signature: str):
    filename = './../appcast.xml'
    ET.register_namespace("sparkle", "http://www.andymatuschak.org/xml-namespaces/sparkle")
    tree = ET.parse(filename)
    root = tree.getroot()

    channel = root.find("channel")
    if channel is None:
        print("Expected channel tag but got none")
        sys.exit(1)

    add_item(channel, version, signature)
    tree.write(filename + ".test", "utf-8")


def add_item(element: ET.Element, version: str, signature: str):
    item = ET.Element("item")
    element.append(item)

    title = ET.SubElement(item, "title")
    title.text = f"Version {version}"

    release_notes = ET.SubElement(item, "sparkle:releaseNotesLink")
    release_notes.text = f"https://digital-stage.github.io/digital-stage-pc/releases/{version}.html"

    release = ET.SubElement(item, "pubDate")
    release.text = datetime.now().strftime("%Y%m%d %H:%M:%S+2")

    add_enclosure(item, version, signature)


def add_enclosure(element: ET.Element, version: str, signature: str):
    enclosure = ET.SubElement(element, "enclosure")
    enclosure.set("url", f"https://github.com/digital-stage/digital-stage-pc/releases/download/{version}/digitalStagePC_setup_{version}.exe")
    enclosure.set("sparkle:version", version)
    enclosure.set("sparkle:dsaSignature", signature)
    enclosure.set("sparkle:installerArguments", "/SILENT /SP- /NOICONS")
    enclosure.set("length", "0")
    enclosure.set("type", "application/octet-stream")


def get_env_or_exit(key: str) -> str:
    value = os.getenv(key)

    if value is None:
        print(f"Expected env var '{key}' does not exist")
        sys.exit(1)
    return value


def handle_release_notes(version: str, bugfix_str: str, features_str: str):
    filename = f"./../{version}.html"
    content = template_release_notes(version, bugfix_str, features_str)

    with open(filename, "w") as file:
        file.write(content)


def template_release_notes(version: str, bugfix_str: str, features_str: str) -> str:
    bugfixes = template_list(bugfix_str)
    features = template_list(features_str)

    with open("template.html") as file:
        content = file.read()

    content = content.replace("{{version}}", version)
    content = content.replace("{{features}}", features)
    content = content.replace("{{bugfixes}}", bugfixes)

    return content


def template_list(list_as_string: str) -> str:
    value = ""
    for entry in list_as_string.split(";"):
        value += f"            <li>{entry}<li>\n"
    return value


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
