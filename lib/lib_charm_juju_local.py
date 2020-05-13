from pathlib import Path
import subprocess
import textwrap

from charmhelpers.core import hookenv, host


class JujuLocalHelper:
    def __init__(self):
        self.charm_config = hookenv.config()

    def gen_keys(self):
        ssh_key = Path("/home/ubuntu/.ssh/id_rsa")
        if not ssh_key.is_file():
            subprocess.check_call(
                [
                    "sudo",
                    "-u",
                    "ubuntu",
                    "ssh-keygen",
                    "-t",
                    "rsa",
                    "-N",
                    "",
                    "-f",
                    str(ssh_key),
                ]
            )

    def lxd_init(self):
        install_sh = textwrap.dedent(
            """
            lxd init --auto --storage-backend dir
            lxc network delete lxdbr0
            lxc network create lxdbr0 ipv4.address=auto ipv6.address=none"""
        )
        subprocess.call(install_sh, shell=True)

    def setup_juju(self):
        subprocess.call("sudo usermod -aG lxd ubuntu", shell=True)
        if host.is_container():
            subprocess.call(
                "sudo -u ubuntu lxc profile set default "
                "raw.lxc lxc.apparmor.profile=unconfined",
                shell=True,
            )
        subprocess.call(
            textwrap.dedent(
                """
                sudo -u ubuntu bash <<eof
                /snap/bin/juju clouds
                /snap/bin/juju bootstrap localhost lxd
                eof"""
            ),
            shell=True,
        )
