import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RefreshTest(unittest.TestCase):
    def test_active_ppp_advertisement_refresh_preserves_assigned_prefix(self):
        refresh = ROOT / 'lib/vpn-ipv6_refresh'
        self.assertTrue(refresh.exists(), 'active PPP refresh helper is missing')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fragments = root / 'radvd'
            fragments.mkdir()
            config = fragments / 'radvd.ppp0.conf'
            config.write_text('interface ppp0 {\n prefix fd12:3456::/64 {\n };\n};\n')
            cfg = root / 'cfg'; cfg.write_text('LAN=("2001:db8:abcd::/48")\n')
            functions = ROOT / 'lib/vpn-ipv6_radvd'
            script = root / 'refresh'
            script.write_text(refresh.read_text().replace('/usr/lib/iserv/cfg', str(cfg)).replace('/usr/lib/iserv/vpn-ipv6_radvd', str(functions)).replace('/var/lib/iserv/vpn-ipv6/radvd', str(fragments)))
            log = root / 'log'
            binary = root / 'bin'; binary.mkdir()
            for name, content in {
                'systemctl': f'echo "$*" >> "{log}"; exit 0',
                'netquery6': 'echo 2001:db8::53',
                'ip': 'exit 0',
                'radvd': 'exit 0',
            }.items():
                p=binary/name; p.write_text('#!/bin/sh\n'+content+'\n'); p.chmod(0o755)
            env=dict(os.environ, PATH=str(binary)+':'+os.environ['PATH'])
            subprocess.run(['/bin/bash',str(script)],env=env,check=True)
            self.assertIn('prefix fd12:3456::/64', config.read_text())
            self.assertIn('route 2001:db8:abcd::/48', config.read_text())
            self.assertIn('RDNSS 2001:db8::53', config.read_text())
            self.assertNotIn('restart', log.read_text())

if __name__ == '__main__': unittest.main()
