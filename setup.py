from setuptools import setup, find_packages
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# https://stackoverflow.com/a/58534041/8903959
setup(
    name='lib_bgpstream_website_collector',
    author="Justin Furuness, Tony Zheng",
    author_email="jfuruness@gmail.com",
    version="0.0.1",
    url='https://github.com/jfuruness/lib_bgpstream_website_collector.git',
    license="BSD",
    description="Downloads BGPStream info solely for research purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Furuness", "BGP", "Hijack", "Outage", "Leak", "BGPStream"
              "Peers", "Customers", "Providers", "BGPStream.com"],
    include_package_data=True,
    python_requires=">=3.10",
    packages=find_packages(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3'],
    entry_points={
        'console_scripts': 'lib_bgpstream_website_collector = lib_bgpstream_website_collector.__main__:main'},
)
