import io
import re
from setuptools import setup

import os, sys
import shutil

try:
    if os.path.isdir(os.path.join(os.path.dirname(__file__), 'onefichier')):
        shutil.rmtree(os.path.join(os.path.dirname(__file__), 'onefichier'))
except:
    print("Can't Remove directory, installing aborted !")
    sys.exit()
try:
    os.makedirs(os.path.join(os.path.dirname(__file__), 'onefichier'))
except:
    pass
try:
    os.remove(os.path.join('onefichier', '__version__.py'))
except:
    pass
shutil.copy2('__version__.py', 'onefichier')
shutil.copy2('onefichier.py', 'onefichier')
shutil.copy2('__init__.py', 'onefichier')
shutil.copy2('size.py', 'onefichier')
#shutil.copy2('downloader.py', '1fichier')
#shutil.copy2('downloader2.py', '1fichier')

# with io.open("README.rst", "rt", encoding="utf8") as f:
#     readme = f.read()

# with io.open("__version__.py", "rt", encoding="utf8") as f:
    # version = re.search(r"version = \'(.*?)\'", f.read()).group(1)
import __version__
version = __version__.version

requirements = [
        'make_colors>=3.12',
        'requests',
        'bs4',
        'clipboard',
        'pydebugger',
        'configset',
        'pywget',
        'progressbar2',
        'bitmath'
    ]
if sys.platform == 'win32':    
    requirements += ['idm']
else:
    requirements += ['pygetch']
setup(
    name="onefichier",
    version=version,
    url="https://github.com/cumulus13/1fichier",
    project_urls={
        "Documentation": "https://github.com/cumulus13/1fichier",
        "Code": "https://github.com/cumulus13/1fichier",
    },
    license="BSD",
    author="Hadi Cahyadi LD",
    author_email="cumulus13@gmail.com",
    maintainer="cumulus13 Team",
    maintainer_email="cumulus13@gmail.com",
    description="1fichier url generator and unofficial API",
    # long_description=readme,
    # long_description_content_type="text/markdown",
    packages=["onefichier"],
    install_requires=requirements,
    entry_points = {
         "console_scripts": [
             "1fichier = onefichier.onefichier:usage",
         ]
    },
    # data_files=['__version__.py'],
    include_package_data=True,
    python_requires=">=2.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)
