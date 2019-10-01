from charmhelpers.core import hookenv
from charms.reactive import set_flag, when_not
from lib_charm_juju_local import JujuLocalHelper

helper = JujuLocalHelper()


@when_not("juju-local.installed")
def install_charm_juju_local():
    helper.gen_keys()
    helper.lxd_init()
    helper.setup_juju()
    hookenv.status_set("active", "")
    set_flag("juju-local.installed")
