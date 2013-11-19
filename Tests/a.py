import os
import glob
import config

def insert_data():
    folder = os.path.join(config.current_folder, "pages")
    files = glob.glob(os.path.join(folder, "*html"))
    print folder
    print files

    for file in files:
        if re.search("(.{32})", os.path.basename(file)):
            print file


current_folder = os.path.dirname(os.path.realpath(__file__))
page_folder = os.path.join(current_folder, "pages")
os.mkdir(page_folder)
insert_data()
