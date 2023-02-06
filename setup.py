# read the contents of your README file
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="mflag",
    version="1.5.2",
    author="Moses Dastmard",
    description="put/remove flags for files and folders",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=["mpath", "pandas"],
    
)