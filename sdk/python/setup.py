from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="adaptive-memory-sdk",
    version="0.1.0",
    author="Adaptive Memory Team",
    author_email="dev@adaptivememory.io",
    description="Python client SDK for the Adaptive Memory Runtime",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adaptivememory/adaptive-memory-runtime",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ],
)
