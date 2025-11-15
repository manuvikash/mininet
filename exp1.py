from mininet.net import Mininet
from mininet.node import Node
from mininet.link import TCLink
from mininet.log import setLogLevel, info


class LinuxRouter(Node):
  # Simple router node that turns on IP forwarding while running
    def config(self, **params):
        super().config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


def disable_rpf(host):
    # Turn off reverse-path filtering so the router can handle asymmetric routes
    for iface in host.cmd('ls /proc/sys/net/ipv4/conf').split():
        if iface != 'lo':
            host.cmd(f'sysctl -w net.ipv4.conf.{iface}.rp_filter=0')


def main():
    net = Mininet(controller=None, link=TCLink, autoSetMacs=True, autoStaticArp=True)

    # Create all hosts/routers with their IPs and default routes from the diagram
    h1 = net.addHost('h1', ip='10.0.0.1/24', defaultRoute='via 10.0.0.3')
    h2 = net.addHost('h2', ip='10.0.3.2/24', defaultRoute='via 10.0.3.4')
    h3 = net.addHost('h3', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
    r1 = net.addHost('r1', cls=LinuxRouter, ip='10.0.0.3/24')
    r2 = net.addHost('r2', cls=LinuxRouter, ip='10.0.1.2/24')

    # Wire up links using the interface/IP assignments from the topology diagram
    for left, right, intfs in (
        (h1, r1, ('h1-eth0', 'r1-eth0', '10.0.0.1/24', '10.0.0.3/24')),
        (r1, r2, ('r1-eth1', 'r2-eth0', '10.0.1.1/24', '10.0.1.2/24')),
        (r2, h3, ('r2-eth1', 'h3-eth0', '10.0.2.1/24', '10.0.2.2/24')),
        (r1, h2, ('r1-eth2', 'h2-eth0', '10.0.3.4/24', '10.0.3.2/24')),
    ):
        net.addLink(
            left,
            right,
            intfName1=intfs[0],
            intfName2=intfs[1],
            params1={'ip': intfs[2]},
            params2={'ip': intfs[3]},
        )

    net.start()

    # Allow routers to forward packets freely and add the required static routes
    r1, r2 = net['r1'], net['r2']
    for router in (r1, r2):
        disable_rpf(router)

    r1.cmd('ip route add 10.0.2.0/24 via 10.0.1.2 dev r1-eth1')
    r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.1 dev r2-eth0')
    r2.cmd('ip route add 10.0.3.0/24 via 10.0.1.1 dev r2-eth0')

    # Run the four required pings and log their raw output to result1.txt
    with open('result1.txt', 'w', encoding='utf-8') as fh:
        for src, dst, label in (
            ('h1', '10.0.2.2', 'h3'),
            ('h2', '10.0.2.2', 'h3'),
            ('h3', '10.0.0.1', 'h1'),
            ('h3', '10.0.3.2', 'h2'),
        ):
            cmd = f'ping -c 1 {dst}'
            info(f'*** {src} -> {label}: {cmd}\n')
            fh.write(f'[{src}] {cmd}\n{net[src].cmd(cmd)}\n')

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
