from setuptools import setup, find_namespace_packages

setup(
    name="idledataviewer",
    version="0.0.1",
    description="IdleRPG data viewer",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=["flask"],
)
