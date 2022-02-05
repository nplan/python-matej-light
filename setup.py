import setuptools

setuptools.setup(
    name="matej_light",
    version="0.1.2",
    author="Nejc Planinsek",
    author_email="planinseknejc@gmail.com",
    description="Light control package",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
    ],
)
