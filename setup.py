import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="basic_model",
    version="0.4.1",
    install_requires=requirements,
    author="(C) 2019 SMART CODE, razvoj aplikacij, d.o.o.",
    author_email="info@smartcode.eu",
    description="Serialization and deserialization made simple",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smart-code-eu/basic_model",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
