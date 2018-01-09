import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


@pytest.mark.parametrize('f',
                         ['net.ipv6.conf.all.disable_ipv6',
                          'net.ipv6.conf.default.disable_ipv6',
                          'net.ipv6.conf.lo.disable_ipv6'])
def test_systcl_settings(host, f):

    cmd = 'sysctl -n {}'.format(f)
    out = host.command.check_output(cmd)

    assert '1' == out



@pytest.mark.parametrize('f',
                         ['htop', 'vim', 'iftop', 'iotop', 'ntp', 'unzip', 'tar', 'pigz', 'zip', 'gcc', 'python-pip', 'python-dev', 'logrotate', 'sysstat', 'super', 'traceroute', 'tzdata'])
def test_packages_installed(host, f):
    pkg = host.package(f)
    assert pkg.is_installed
