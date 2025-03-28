#!/usr/bin/env python3
import json
import unittest

import zaza.charm_lifecycle.utils as lifecycle_utils
from zaza import model


class CharmJujuLocalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jlocal_unit = "juju-local/0"
        cls.model_name = model.get_juju_model()
        cls.test_config = lifecycle_utils.get_charm_config()
        model.block_until_all_units_idle()
        # Add a test model in the remote Juju cloud
        # This is needed becuase in Juju 3.x there's no default model created
        # after bootstrapping the controller
        cls.remote_juju(["add-model", "test"], None)

    @classmethod
    def remote_juju(cls, args, format="json"):
        if format:
            fmt = "--format={}".format(format)
        else:
            fmt = ""
        cmd = """sudo -u ubuntu bash -c '/snap/bin/juju {} {}'""".format(" ".join(args), fmt)
        res = model.run_on_unit(cls.jlocal_unit, cmd)
        return_code = int(res["Code"])
        if return_code != 0:
            raise RuntimeError(
                "Failed to execute command in juju-local unit.\nStderr: {}".format(
                    res.get("Stderr")
                )
            )
        return res.get("Stdout")

    def juju_status(self):
        stdout = self.remote_juju(["status"])
        return json.loads(stdout)

    def test_juju_status(self):
        jstatus = self.juju_status()
        self.assertEqual(jstatus["model"]["controller"], "lxd")

    def test_juju_users(self):
        stdout = self.remote_juju(["users"])
        userobjects = json.loads(stdout)
        usernames = set(u["user-name"] for u in userobjects)
        self.assertTrue("admin" in usernames)

    def test_deploy(self):
        self.remote_juju(["deploy", "ubuntu"], format=None)
        model.run_on_unit(self.jlocal_unit, "sudo -u ubuntu bash -c 'juju-wait -t 1200'")
        jstatus = self.juju_status()
        _, unit = jstatus["applications"]["ubuntu"]["units"].popitem()
        self.assertEqual(unit["workload-status"]["current"], "active")
