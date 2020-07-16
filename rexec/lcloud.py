from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import config

cls = get_driver(Provider.EC2)
driver = cls(config.access, config.secret)