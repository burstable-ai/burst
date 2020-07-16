from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import config

cls = get_driver(Provider.EC2)
driver = cls(config.access, config.secret, region=config.region)
# pprint(driver.list_sizes())
# pprint(driver.list_nodes())

nodes = driver.list_nodes()
node = [x for x in nodes if '44.231.174.47' in x.public_ips][0]
pprint(node)
# driver.start_node(node)
driver.stop_node(node)