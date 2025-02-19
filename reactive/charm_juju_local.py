"""Juju Local reactive module."""

from charmhelpers.core import hookenv  # pylint: disable=import-error
from charms.layer import snap  # pylint: disable=import-error
from charms.reactive import hook, set_flag, when_not  # pylint: disable=import-error
from lib_charm_juju_local import JujuLocalHelper  # pylint: disable=import-error

helper = JujuLocalHelper()


SNAPS_TO_INSTALL = ["juju", "juju-wait", "lxd"]


# Workaround for LP#1712808: manually handle snap installation.
# Don't remove layer-snap; we'll keep using it for the rest of its infrastructure
# (e.g. prereqs, snap.install/refresh), but we'll handle installation of the actual
# snaps themselves.
@hook("install")
def install() -> None:
    """Install reactive method."""
    try:
        snap.install("snapd")
    except Exception:  # pylint: disable=broad-exception-caught
        # The "snapd" install will fail on privileged containers, but subsequent retries
        # (including as a prereq of another snap) will work.  Ignore any failures on
        # this first attempt.
        pass
    for snap_name in SNAPS_TO_INSTALL:
        if snap_name == "juju":
            juju_channel = hookenv.config("juju-channel")
            snap.install(snap_name, channel=juju_channel, classic=True)
        else:
            snap.install(snap_name, classic=True)
    helper.lxd_migrate()


@hook("upgrade-charm")
def upgrade_charm() -> None:
    """Charm upgrade reactive method."""
    # Install any required snaps which might not already be installed.
    # (Note that layer-snap actually calls its own install logic on every hook via
    # hookenv.atstart(); calling install() here is fairly conservative.)
    install()
    # Refresh the installed snaps
    for snap_name in SNAPS_TO_INSTALL:
        snap.refresh(snap_name, classic=True)


@when_not("juju-local.installed")
def install_charm_juju_local() -> None:
    """Install charm juju local if not installed yet."""
    helper.gen_keys()
    helper.lxd_init()
    helper.setup_juju()
    hookenv.status_set("active", "")
    set_flag("juju-local.installed")
