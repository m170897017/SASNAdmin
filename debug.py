from jinja2 import Environment, FileSystemLoader
import os

cwd = os.path.dirname(os.path.abspath(__file__))

j2_env = Environment(loader=FileSystemLoader(cwd), trim_blocks=True)

print j2_env.get_template('templates/loadApply').render(test='this is lch!!!!')