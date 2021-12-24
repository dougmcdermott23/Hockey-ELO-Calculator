from configparser import ConfigParser

def config(file_name: str="config.ini", section: str="database") -> dict:
    parser = ConfigParser()
    parser.read(file_name)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {file_name} file")

    return db