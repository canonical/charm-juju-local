from charmhelpers.core import hookenv
from charms.layer import snap
from charms.reactive import hook, set_flag, when_not
from lib_charm_juju_local import JujuLocalHelper

helper = JujuLocalHelper()


SNAPS_TO_INSTALL = ["juju", "juju-wait"]


# Workaround for LP#1712808: manually handle snap installation.
# Don't remove layer-snap; we'll keep using it for the rest of its infrastructure
# (e.g. prereqs, snap.install/refresh), but we'll handle installation of the actual
# snaps themselves.
@hook("install")
def install():
    try:
        snap.install("snapd")
    except Exception:
        # The "snapd" install will fail on privileged containers, but subsequent retries
        # (including as a prereq of another snap) will work.  Ignore any failures on
        # this first attempt.
        pass
    for snap_name in SNAPS_TO_INSTALL:
        snap.install(snap_name, classic=True)


@hook("upgrade-charm")
def upgrade_charm():
    # Install any required snaps which might not already be installed.
    # (Note that layer-snap actually calls its own install logic on every hook via
    # hookenv.atstart(); calling install() here is fairly conservative.)
    install()
    # Refresh the installed snaps
    for snap_name in SNAPS_TO_INSTALL:
        snap.refresh(snap_name, classic=True)


@when_not("juju-local.installed")
def install_charm_juju_local():
    helper.gen_keys()
    helper.lxd_init()
    helper.setup_juju()
    hookenv.status_set("active", "")
    set_flag("juju-local.installed")
