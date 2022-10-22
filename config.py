import yaml

def getConfig():
    """
        Auxiliar para leitura do arquivo yaml
    """
    with open('config.yaml', 'r') as stream:
        try:
            # Converts yaml document to python object
            d=yaml.safe_load(stream)
            return d
        except yaml.YAMLError as e:
            print(e)

                  