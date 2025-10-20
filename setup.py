from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name='invest_agent',
        version='0.0.1',
        package_dir={"": "."},
        packages=find_packages(where="."),
    )