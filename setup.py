'''
Date: 2023-03-10 02:53:02
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 18:59:31
FilePath: /outlier/setup.py
'''
import setuptools

with open("README.md", encoding="utf8") as f:
    long_description = f.read()
    
setuptools.setup(
    name="outlierchat",
    version="0.0.22",
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
    install_requires=['rsa>=4.9', 'pyDes>=2.0.1'],
    python_requires='>3.6'
)