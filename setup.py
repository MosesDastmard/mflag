from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="flagify",
    version="1.1.2",
    author="Moses Dastmard",
    description="put/remove flags for files and folders",
    long_description=long_description,
    long_description_content_type='text/markdown'
)