from setuptools import setup, find_packages

setup(
    name="geohash_manger",
    version="0.1.0",
    description="geohash_manger for personal use",
    author="Sangwoo Park",
    python_requires=">=3.11",
    keywords=["geohash", "spatial operation"],
    install_requires=[
        find_packages(),
    ],
    extras_require={"dev": []},
)
