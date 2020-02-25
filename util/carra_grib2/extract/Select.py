import yaml
import copy

with open('Selection.yml','r') as conf:
    conf_dict = yaml.safe_load(conf)


for type in ['an','fc']:

  for level in conf_dict['level']:
    l = conf_dict['level'][level]
    d = l['default']
    for spec in l:
        config = copy.deepcopy(d)
        config.update(l[spec])
        if type in config:
            config.update(config[type])
        print(type, config)

