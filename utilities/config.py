from configparser import ConfigParser

def config(file_name: str="config.ini", section: str="database") -> dict:
    """Given a config file and file section, return a dict containing
    the configuration parameters.

    file_name: string for the config file name
    section: string describing the config section name

    return: dictionary where the key is the config parameter and the
            value is what the config parameter is set to
    """
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