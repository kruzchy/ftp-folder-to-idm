import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from pathlib import Path
import os
import keyring

username = ''
password = keyring.get_password('usb', username)
rel_path = Path()
default_local_path = Path().home()/'Desktop'


def is_file(name):
    if name[-1] == '/':
        return False
    else:
        return True


def get_list_names(soup):
    return [tag['href'] for tag in soup.find_all('a')]


def get_fd_link_auth(folder_link):
    return f"https://{username}:{password}@{folder_link.split('://')[1]}"


def get_fd_name(folder_link):
    return [a for a in folder_link.split('/') if a][-1]


def add_idm_cmd(file_name, file_link, rel_path):
    idm_cmd_template = f'idman /a /n /p "{default_local_path / rel_path}" /f "{file_name}" /d {file_link}'
    os.system(idm_cmd_template)
    # print(f'>>Added {rel_path}\\{file_name}')


def each_folder(fd_name, fd_link):
    global rel_path
    rel_path = rel_path / unquote(fd_name)
    r = requests.get(fd_link)
    # print(r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    list_of_all_names = get_list_names(soup)
    files = [name for name in list_of_all_names if is_file(name)]
    files_dict = {}
    for f in files:
        files_dict[unquote(f)] = f'{fd_link}/{f}'

    folders = [name for name in list_of_all_names if not is_file(name)][1:]
    folders_dict = {}
    for fldr in folders:
        folders_dict[unquote(fldr)] = f'{fd_link}{fldr}'

    for file_name, file_link in files_dict.items():
        print(f'>>processing file "{rel_path}\\{file_name}"')
        add_idm_cmd(file_name, file_link, rel_path)

    for folder_name, folder_link in folders_dict.items():
        print(f'----Found folder "{rel_path}\\{folder_name[:-1]}"')
        each_folder(folder_name, folder_link)
        rel_path = rel_path.parent


if __name__ == '__main__':
    base_folder_link = input('Folder link: ')
    each_folder(get_fd_name(base_folder_link), get_fd_link_auth(base_folder_link))
