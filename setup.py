'''
Date: 2023-03-10 02:53:02
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 18:13:04
FilePath: /outlier/setup.py
'''
import setuptools

with open("README.md", encoding="utf8") as f:
    long_description = f.read()
    
setuptools.setup(
    name="outlierchat",
    version="0.0.16",
    author="Thetis",
    author_email="736396627@qq.com",
    description="A simple server to build a secret channel for chat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires='>3.6'
)