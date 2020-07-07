from setuptools import setup, find_packages


def repo_file_as_string(file_path: str) -> str:
    with open(file_path, "r") as repo_file:
        return repo_file.read()


setup(install_requires=[
    "victoria", "aiohttp==3.5.4", "aiorun", "cchardet", "aiodns"
],
      name="victoria_email",
      version="#{VERSION}#",
      description="Victoria plugin for Glasswall Rebuild for Email",
      long_description=repo_file_as_string("README.md"),
      long_description_content_type="text/markdown",
      author="Sam Gibson",
      author_email="sgibson@glasswallsolutions.com",
      url="https://github.com/glasswall-sre/victoria_email",
      packages=find_packages("."),
      python_requires=">=3.6")
