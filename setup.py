'''
Date: 2023-02-26 11:12:35
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-09 21:09:43
FilePath: /outlier/setup.py
'''
import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()
    
setuptools.setup(
    name="outlierchat",
    version="0.0.5",
    author="Thetis",
    author_email="736396627@qq.com",
    description="A simple server to build a secret channel for chat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    classifers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent"
    ],
    python_requires='>3.6'
)    
