from setuptools import find_packages, setup
from typing import List

def get_requirements(file_path: str) -> List[str]:
    """
    This function reads a requirements file and returns a list of required packages.
    
    """
    requirements_list: List[str] = []
    try:
        with open("requirements.txt", "r") as file:
            lines = file.readlines()
            
            for line in lines:
                requirement = line.strip()
                # ignore empty lines and -e.
                if requirement and not requirement.startswith("-e ."):
                    requirements_list.append(requirement)
    except FileNotFoundError:
        print(f"can't find your requiremnts.txt file")
        
    return requirements_list

print(get_requirements("requirements.txt"))

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author = "Abimbola Ogunsakin",
    author_email = "inboxbimbo@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements("requirements.txt"),
    
)