from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fmo-aprs",
    version="0.1.0",
    author="BG5ESN",
    description="FMO remote control via APRS-IS with HMAC authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BG5ESN/FMO-APRS-Remote-Control-Tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Ham Radio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="aprs ham-radio amateur-radio fmo remote-control hmac",
)
