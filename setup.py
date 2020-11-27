import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "schedule-generator",
    version="0.0.1",
    author="Nikash Walia, Samraj Moorjani, Elena Zheng, Shresta Bangaru",
    author_email="nikash.walia@gmail.com,samraj.moorjani@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nikwalia/schedule-generator",
    packages=setuptools.find_packages(),
    package_data={'': ['server_info']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 30",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6'
)
