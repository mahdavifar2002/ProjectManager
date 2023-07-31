import subprocess

# First, install 'tqdm', the package for showing progress of python loop
WHL = ['basics\\tqdm-4.65.0-py3-none-any.whl',
       'basics\\colorama-0.4.6-py2.py3-none-any.whl']

print("Please wait for start of the process.")
for item in WHL:
    subprocess.call(["pip", "install", "--no-deps", "--no-index", str(item)], stdout=subprocess.DEVNULL)

# second, install dependency packages of the project

WHL = ['greenlet-2.0.2-cp37-cp37m-win_amd64.whl',
       'importlib_metadata-6.7.0-py3-none-any.whl',
       'jdatetime-4.1.1-py3-none-any.whl',
       'mysqlclient-2.1.0-cp37-cp37m-win_amd64.whl',
       'PySide6-6.2.4-6.2.4-cp36.cp37.cp38.cp39.cp310-none-win_amd64.whl',
       'python_dateutil-2.8.2-py2.py3-none-any.whl',
       'shiboken6-6.2.4-6.2.4-cp36.cp37.cp38.cp39.cp310-none-win_amd64.whl',
       'six-1.16.0-py2.py3-none-any.whl',
       'SQLAlchemy-2.0.19-cp37-cp37m-win_amd64.whl',
       'typing_extensions-4.7.1-py3-none-any.whl',
       'zipp-3.15.0-py3-none-any.whl']

print("Installing packages...")
from tqdm import tqdm
for item in tqdm(WHL):
    subprocess.call(["pip", "install", "--no-deps", "--no-index", str(item)], stdout=subprocess.DEVNULL)

